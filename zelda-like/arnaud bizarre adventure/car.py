import pygame

class Car(pygame.sprite.Sprite):
    def __init__(self, pos, groups):
        super().__init__(groups)
        self.sprite_type = 'obstacle_mouvant'
        self.image = pygame.Surface((50, 80))
        self.image.fill((120, 120, 140)) # Couleur carrosserie
        self.rect = self.image.get_rect(topleft=pos)
        self.hitbox = self.rect.inflate(-5, -5)
        
        self.speed = 4
        self.direction = pygame.math.Vector2(0, 1) # Défile vers le bas

    def update(self):
        """La voiture descend l'autoroute en boucle"""
        self.hitbox.y += self.speed
        self.rect.center = self.hitbox.center
        
        # Si la voiture sort par le bas de l'autoroute, elle réapparaît en haut
        if self.hitbox.y > 600:
            self.hitbox.y = 0
