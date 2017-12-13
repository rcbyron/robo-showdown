"""Representation of a fighter as a layered group of sprites."""
import pygame
import random
import time
import os
import numpy as np

from colors import *
from settings import *
from geometry import *
from vision import Vision
from pygame import Color


class SmoothCircle(pygame.sprite.Sprite):
    def __init__(self, color, radius, x, y, bg_color=WHITE):
        """Initialize a smooth circle."""
        super().__init__()

        self.bg_color = bg_color
        self.color = color
        self.radius = radius

        self.image = pygame.Surface([self.radius*2, self.radius*2])
        self.update_image()

        self.rect = self.image.get_rect()
        self.set_position(x, y)

    def set_position(self, x, y):
        """Set the position of the circle."""
        self.rect.x = x
        self.rect.y = y

    def update_image(self):
        """Update the image of the circle."""
        self.image.fill(self.bg_color)
        self.image.set_colorkey(self.bg_color)

        cx = cy = self.radius  # center point of circle

        # radius-1 otherwise circle is cut off around the edges
        pygame.gfxdraw.aacircle(self.image, cx, cy, self.radius-1, self.color)
        pygame.gfxdraw.filled_circle(self.image, cx, cy, self.radius-1, self.color)

    def draw(self, screen):
        """Update and draw the latest image to the screen."""
        self.update_image()
        screen.blit(self.image, self.rect)


class Fighter(pygame.sprite.LayeredUpdates):

    def __init__(self, id, color, radius, x, y, angle, random_weights=False):
        """Initialize a new Fighter."""
        super().__init__()

        self.id = id
        self.color = color
        self.radius = radius
        self.angle = angle
        self.speed = FIGHTER_SPEED
        self.unit_dx, self.unit_dy = angle_to_unit_x_y(self.angle)
        self.dx, self.dy = angle_to_x_y(self.angle, self.speed)

        self.reset_state()

        # Initialize Q-table with weights
        if random_weights:
            self.Q = np.random.random((NUM_STATES, NUM_ACTIONS))
        else:
            try:
                # Initialize Q-table with weights from previous session
                self.Q = np.loadtxt(MODEL_FILE, delimiter=",")
            except FileNotFoundError:
                print("Model not found, initializing fighter", self.id, "with random weights...")
                self.Q = np.random.random((NUM_STATES, NUM_ACTIONS))

        self.weapon_radius = int(radius / 3)
        self.torso = SmoothCircle(color, radius, x, y)
        self.weapon = SmoothCircle(GRAY, self.weapon_radius,
                                   x=x+radius-self.weapon_radius, y=y+radius, bg_color=color)
        self.vision = Vision(id, self.get_center(), self.angle, GRAY, GRAY, GRAY)

        self.add(self.torso)
        self.add(self.weapon)
        self.add(self.vision)

    def reset_state(self):
        """Reset observations/state of the fighter."""
        self.reloading = False
        self.last_shot_time = 0
        self.bullet_on_left = False
        self.bullet_on_right = False
        self.fighter_on_left = False
        self.fighter_on_right = False
        self.on_target = False

        self.damage = 0
        self.hits = 0

        self.state = self.get_state(prev_state=0)

    def set_random_angle(self):
        """Orient the fighter to a random angle."""
        self.angle = random.randint(0, 359)
        self.rotate_by(self.angle)

    def set_position(self, x, y):
        """Move fighter to position and maintain orientation."""
        self.torso.rect.x = x
        self.torso.rect.y = y
        self.weapon.rect.x = x+self.radius-self.weapon_radius
        self.weapon.rect.y = y+self.radius

    def rotate_by(self, angle):
        """Rotate sprite by angle and update dx dy movement components."""
        self.angle += angle
        self.angle %= 360

        # get x y vector components from current fighter angle
        self.unit_dx, self.unit_dy = angle_to_unit_x_y(self.angle)

        # move weapon sprite around inner radius according to current angle
        inner_radius = self.torso.radius - self.weapon.radius
        self.weapon.rect.x = self.torso.rect.x + inner_radius + (self.unit_dx * inner_radius)
        self.weapon.rect.y = self.torso.rect.y + inner_radius + (self.unit_dy * inner_radius)

        self.dx = self.unit_dx * self.speed
        self.dy = self.unit_dy * self.speed

    def turn_left(self):
        """Turn left by turning rate degrees."""
        self.rotate_by(-TURNING_RATE)

    def turn_right(self):
        """Turn right by turning rate degrees."""
        self.rotate_by(TURNING_RATE)

    def move_forward(self):
        """Attempt to move forward."""
        actual_dx = self.dx
        actual_dy = self.dy
        if (self.torso.rect.x + self.dx) < 0 or \
                (self.torso.rect.x + self.dx + self.torso.radius * 2) > WIDTH:
            actual_dx = 0  # cannot run out of bounds
        if (self.torso.rect.y + self.dy) < 0 or \
                (self.torso.rect.y + self.dy + self.torso.radius * 2) > HEIGHT:
            actual_dy = 0  # cannot run out of bounds

        for sprite in self.sprites():
            sprite.rect.x += actual_dx
            sprite.rect.y += actual_dy

    def shoot(self):
        """If not reloading, trigger a shoot event."""
        if not self.reloading:
            self.reloading = True
            self.last_shot_time = pygame.time.get_ticks()

            # post a new SHOOT_EVENT
            event_data = {
                'shooter': self.id,
                'x': self.weapon.rect.x,
                'y': self.weapon.rect.y,
                'angle': self.angle
            }
            pygame.event.post(pygame.event.Event(SHOOT_EVENT, event_data))

    def get_center(self):
        """Return tuple of fighter center coordinate."""
        return int(self.torso.rect.x + self.torso.radius), int(self.torso.rect.y + self.torso.radius)

    def get_state(self, prev_state):
        """Get current state based observations and previous state."""
        state = (self.fighter_on_left << 5) + (self.fighter_on_right << 4) + \
                (self.bullet_on_left << 3) + (self.bullet_on_left << 2) + \
                (self.reloading << 1) + (self.on_target << 0)  # arbitrary order
        state *= prev_state  # unique state based on previous state
        return state

    def set_color(self, color):
        self.torso.color = color
        self.torso.update_image()

    def update(self, actions):
        """Update fighter state/action before it is drawn."""
        # execute action
        action_func_dict = {
            0: self.turn_left,
            1: self.turn_right,
            2: self.move_forward,
            3: self.shoot
        }
        for action_type, do_action in enumerate(actions.tolist()[0]):
            if do_action:
                action_func_dict[action_type]()

        # update state
        prev_state = self.state
        self.state = self.get_state(prev_state)

        # create new vision sprite with updated colors
        self.vision.kill()
        color_left = color_middle = color_right = GRAY
        if self.fighter_on_left:
            color_left = color_middle = ORANGE
        if self.fighter_on_right:
            color_right = color_middle = ORANGE
        if self.bullet_on_left:
            color_left = color_middle = RED
        if self.bullet_on_right:
            color_right = color_middle = RED
        if self.on_target:
            color_middle = GREEN

        self.vision = Vision(self.id, self.get_center(), self.angle,
                             color_left, color_middle, color_right)
        self.add(self.vision)
        self.move_to_back(self.vision)  # layered below fighter sprite

    def __str__(self):
        return "(id=" + str(self.id) + \
               " hits=" + str(self.hits) + \
               " damage=" + str(self.damage) + ")"

    def __repr__(self):
        return self.__str__()
