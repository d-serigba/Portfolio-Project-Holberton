import pygame

class Bullet(pygame.sprite.Sprite):
    def __init__(self, pos, direction, speed=10):
        super().__init__()
        self.image = pygame.Surface((5, 5))
        self.image.fill(YELLOW)
        self.rect = self.image.get_rect(center=pos)
        self.pos = pygame.Vector2(pos)
        self.direction = direction
        self.speed = speed

    def update(self):
        self.pos += self.direction * self.speed
        self.rect.center = self.pos
        # Détruit la balle si elle sort de l'écran ou heurte un obstacle
