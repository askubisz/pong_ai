import pygame
import random

# Auxiliary function
def sign(x):
    if x >= 0: 
        return 1
    else:
        return -1

class Ball:
    COLOUR=(0,0,0)
    def __init__(self, x, y, radius, max_velocity):
        self.random_velocity=random.uniform(-2, 2)
        self.x=self.original_x=x
        self.y=self.original_y=y
        self.radius=radius
        side=1 if random.random()<0.5 else -1
        self.MAX_VELOCITY=max_velocity
        self.x_velocity=side*self.MAX_VELOCITY
        self.y_velocity=self.random_velocity

    def draw(self, win):
        pygame.draw.circle(win, self.COLOUR, (self.x, self.y), self.radius)

    def move(self):
        self.x=self.x+self.x_velocity
        self.y=self.y+self.y_velocity

    def reset(self):
        self.random_velocity=random.uniform(-2, 2)
        self.x=self.original_x
        self.y=self.original_y
        self.y_velocity=self.random_velocity
        if self.x_velocity>=0:
            self.x_velocity=self.MAX_VELOCITY*-1
        else:
            self.x_velocity=self.MAX_VELOCITY