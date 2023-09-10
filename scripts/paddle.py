import pygame

class Paddle:
    COLOUR=(0,0,0)

    def __init__(self, x, y, width, height, velocity):
        self.x=self.original_x=x
        self.y=self.original_y=y
        self.width=width
        self.height=height
        self.velocity=velocity

    def draw(self, win):
        pygame.draw.rect(win, self.COLOUR, (self.x, self.y, self.width, self.height))
    
    def move(self, up=True):
        if up:
            self.y=self.y-self.velocity
        else:
            self.y=self.y+self.velocity

    def reset(self):
        self.x=self.original_x
        self.y=self.original_y