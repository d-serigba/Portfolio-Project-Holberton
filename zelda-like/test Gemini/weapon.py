import pygame

class Weapon(pygame.sprite.Sprite):
    def __init__(self, player, groups):
        super().__init__(groups)
        self.sprite_type = 'weapon'
        direction = player.facing
        
        # Graphisme temporaire de l'Opinel (un petit rectangle rouge)
        self.image = pygame.Surface((30, 10)) if direction in ['left', 'right'] else pygame.Surface((10, 30))
        self.image.fill((255, 50, 50)) 
        
        # Positionnement de la lame devant Arnaud selon sa direction
        if direction == 'right':
            self.rect = self.image.get_rect(midleft = player.rect.midright + pygame.math.Vector2(-10, 0))
        elif direction == 'left':
            self.rect = self.image.get_rect(midright = player.rect.midleft + pygame.math.Vector2(10, 0))
        elif direction == 'up':
            self.rect = self.image.get_rect(midbottom = player.rect.midtop + pygame.math.Vector2(0, 10))
        elif direction == 'down':
            self.rect = self.image.get_rect(midtop = player.rect.midbottom + pygame.math.Vector2(0, -10))
