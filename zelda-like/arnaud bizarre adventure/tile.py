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
