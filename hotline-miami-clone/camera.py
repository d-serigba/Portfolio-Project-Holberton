import pygame
from constants import WIDTH, HEIGHT

class Camera:
    def __init__(self, width, height):
        self.camera = pygame.Rect(0, 0, width, height)
        self.width = width  # Stocke la largeur
        self.height = height  # Stocke la hauteur

    def apply(self, entity):
        return entity.rect.move(self.camera.topleft)

    def update(self, target):
        x = -target.rect.centerx + self.width // 2  # Utilise self.width
        y = -target.rect.centery + self.height // 2  # Utilise self.height
        self.camera.x = x
        self.camera.y = y
