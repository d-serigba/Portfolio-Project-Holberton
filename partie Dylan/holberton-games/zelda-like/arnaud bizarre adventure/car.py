import pygame
import random

class Car(pygame.sprite.Sprite):
    def __init__(self, pos, groups):
        super().__init__(groups)
        self.sprite_type = 'obstacle_mouvant'
        self.image = pygame.Surface((50, 80))
        self.image.fill((120, 120, 140)) # Couleur carrosserie
        self.rect = self.image.get_rect(topleft=pos)
        self.hitbox = self.rect.inflate(-5, -5)
        
        self.speed = random.randint(3, 6)
        self.direction = pygame.math.Vector2(0, 1) # Défile vers le bas

    def update(self):
        """La voiture descend l'autoroute en boucle"""
        self.hitbox.y += self.speed
        self.rect.center = self.hitbox.center
        
        # Si la voiture sort par le bas de l'autoroute, elle réapparaît en haut
        if self.hitbox.y > 2400:
            self.hitbox.y = -100

            # 🟢 LA MAGIE EST ICI : Changement de voie aléatoire !
            # Ton autoroute a 9 voies (de la colonne 1 à 9). 
            # Chaque case fait 64 pixels. Pour centrer la voiture de 50px, on ajoute +7.
            voies_possibles = [col * 64 + 7 for col in range(1, 10)]
            
            # La voiture choisit une nouvelle voie au hasard
            self.hitbox.x = random.choice(voies_possibles)
            
            # Elle choisit aussi une nouvelle vitesse pour surprendre le joueur
            self.speed = random.randint(3, 7)
