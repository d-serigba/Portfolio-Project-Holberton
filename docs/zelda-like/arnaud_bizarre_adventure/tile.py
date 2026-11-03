import pygame

import pygame 

class Tile(pygame.sprite.Sprite):
    def __init__(self, pos, groups, sprite_type, surface=None):
        super().__init__(groups)
        self.sprite_type = sprite_type
        if surface is None:
            surface = pygame.Surface((64, 64))
            surface.fill((100, 100, 100))  # gris, pour au moins les voir clairement
        self.image = surface
        self.rect = self.image.get_rect(topleft=pos)
        
        # LA GESTION INTELLIGENTE DES HITBOXES
        if sprite_type == 'invisible' or sprite_type == 'mur':
            # 1. Les murs de bordure : On garde le bloc entier (64x64) pour faire un mur lisse
            self.hitbox = self.rect.inflate(0, 0) 
        else:
            # 2. Les objets isolés (arbres, rochers) : On réduit la base pour la profondeur
            self.hitbox = self.rect.inflate(0, -20)

class TransitionTile(pygame.sprite.Sprite):
    def __init__(self, pos, groups, target_zone):
        super().__init__(groups)
        self.sprite_type = 'transition'
        self.image = pygame.Surface((64, 64))
        self.image.fill((255, 165, 0)) # Orange pour repérer la sortie de l'Open Space
        self.rect = self.image.get_rect(topleft=pos)
        self.hitbox = self.rect.copy()
        self.target_zone = target_zone # Exemple : "metro"

class ItemTile(pygame.sprite.Sprite):
    def __init__(self, pos, groups, item_name):
        super().__init__(groups)
        self.sprite_type = 'item'
        self.item_name = item_name
        self.image = pygame.Surface((40, 40))

        if item_name == "epee_lego":
            self.image.fill((255, 215, 0)) # Doré
        elif item_name == "lunettes_baceux":
            self.image.fill((0, 191, 255)) # Bleu ciel baceux
        elif item_name == "koenigsegg":
            self.image.fill((220, 220, 220)) # Gris Métal Jesko

        self.rect = self.image.get_rect(center=pos)
        self.hitbox = self.rect.copy()
