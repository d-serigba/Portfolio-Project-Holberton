import pygame

class Tile(pygame.sprite.Sprite):
    def __init__(self, pos, groups):
        super().__init__(groups)
        # Pour l'instant, on utilise des rectangles de couleur avant de mettre des images
        self.image = pygame.Surface((64, 64))
        self.image.fill((80, 80, 90)) # Couleur grise pour les bureaux/murs
        self.rect = self.image.get_rect(topleft=pos)
        
        # La hitbox de collision peut être légèrement plus petite que le visuel 
        # pour donner un effet de perspective 2.5D (le joueur peut passer un peu derrière)
        self.hitbox = self.rect.inflate(0, -10)
