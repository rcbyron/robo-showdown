"""Representation of a bullet as a sprite."""
import pygame

from colors import *
from settings import *
from geometry import *
from pygame import Color


class Bullet(pygame.sprite.Sprite):

    def __init__(self, shooter, x, y, angle, speed, radius=5):
        """Initialize the bullet object."""
        super().__init__()

        self.shooter = shooter

        self.radius = radius

        self.image = pygame.Surface([radius*2, radius*2])
        self.image.fill(Color(*WHITE))
        self.image.set_colorkey(Color(*WHITE))
     
        self.dx, self.dy = angle_to_x_y(angle, speed)

        pygame.draw.circle(self.image, Color(*BLACK), (radius, radius), radius)

        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

    def update(self):
        """Update the bullet before it is drawn."""
        self.rect.x += self.dx
        self.rect.y += self.dy

        if self.rect.x + self.rect.w < 0 or self.rect.x > WIDTH or \
                self.rect.y + self.rect.h < 0 or self.rect.y > HEIGHT:
            self.kill()
