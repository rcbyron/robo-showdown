"""Representation of an entity's vision."""
import pygame

from colors import *
from settings import *
from geometry import *
from pygame import Color


class Vision(pygame.sprite.Sprite):

    def __init__(self, viewer_id, center, angle, color_left, color_middle, color_right):
        """Initialize a new Vision sprite."""
        super().__init__()

        self.viewer_id = viewer_id

        # vision rays start from center
        self.start = self.center = center

        ldx, ldy = angle_to_x_y(angle - SIGHT_ANGLE, SIGHT_RANGE)
        mdx, mdy = angle_to_x_y(angle, SIGHT_RANGE)
        rdx, rdy = angle_to_x_y(angle + SIGHT_ANGLE, SIGHT_RANGE)

        # vision ray end points
        self.end_left = (int(self.start[0] + ldx), int(self.start[1] + ldy))
        self.end_middle = (int(self.start[0] + mdx), int(self.start[1] + mdy))
        self.end_right = (int(self.start[0] + rdx), int(self.start[1] + rdy))

        # create a surface for the rays to be drawn on
        self.image = pygame.Surface([WIDTH, HEIGHT])
        self.image.fill(WHITE)
        self.image.set_colorkey(WHITE)

        pygame.draw.aaline(self.image, Color(*color_left), self.start, self.end_left, 1)
        pygame.draw.aaline(self.image, Color(*color_middle), self.start, self.end_middle, 1)
        pygame.draw.aaline(self.image, Color(*color_right), self.start, self.end_right, 1)

        self.rect = self.image.get_rect()

    def draw(self, screen):
        screen.blit(self.image, self.rect)

    def detects(self, circle_sprite,
                within_angle=SIGHT_ANGLE,
                within_range=SIGHT_RANGE):
        """Detect if circle sprite is within angle/range.

        If detected, return the side it was detected on."""
        r = circle_sprite.radius
        obj_center = (circle_sprite.rect.x + r, circle_sprite.rect.y + r)

        dist_to_obj_center = sqrt((self.center[0] - obj_center[0]) ** 2 +
                                  (self.center[1] - obj_center[1]) ** 2)

        if dist_to_obj_center <= within_range:  # object is within range
            angle = angle_between(self.center, self.end_middle, obj_center)
            if -within_angle <= angle < 0:
                return "left"
            elif 0 <= angle <= within_angle:
                return "right"
        return None

    def on_target(self, circle_sprite):
        """Return true if middle vision ray is pointed at circle sprite."""
        r = circle_sprite.radius
        cx = circle_sprite.rect.x + r
        cy = circle_sprite.rect.y + r

        # see if any line point intersects with the circle sprite
        for point in get_line(self.start, self.end_middle):
            # pythagorean distance formula
            if ((point[0] - cx) ** 2 + (point[1] - cy) ** 2) < (r * r):
                return True
        return False
