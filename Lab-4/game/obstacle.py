import pygame

class Obstacle:
    def __init__(self, x, ground_y, speed, width=25, height=40):
        self.x = x
        self.prev_x = x
        self.width = width
        self.height = height
        self.y = ground_y - height
        self.speed = speed
        self.scored = False

    def move(self):
        self.prev_x = self.x
        self.x -= self.speed

    def off_screen(self):
        return self.x + self.width < 0

    def rect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)

