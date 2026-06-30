import pygame
import sys
from tile import Tile
from player import Player
from npc import NPC
from weapon import Weapon 
from ui import UI

# Configuration de la carte d'Holberton (Phase 0)
HOLBERTON_MAP = [
    ['x','x','x','x','x','x','x','x','x','x','x','x','x','x','x'],
    ['x','p',' ',' ',' ','x',' ',' ',' ',' ',' ',' ',' ',' ','x'], #p = player
    ['x',' ','x','x',' ','x',' ','x','x','x',' ','x','x',' ','x'],
    ['x',' ','x',' ',' ',' ','n',' ',' ','x',' ',' ','x',' ','x'], # 'n' placé au milieu
    ['x',' ','x',' ','x','x','x','x',' ','x','x',' ','x',' ','x'],
    ['x',' ',' ',' ','x',' ',' ','x',' ',' ',' ',' ',' ',' ','x'],
    ['x','x','x','x','x','x','x','x','x','x','x','x','x','x','x'],
]

class Level:
    def __init__(self):
        self.display_surface = pygame.display.get_surface()

        # Groupes de sprites
        self.visible_sprites = pygame.sprite.Group()
        self.obstacle_sprites = pygame.sprite.Group()
        self.interaction_sprites = pygame.sprite.Group() # Nouveau groupe pour les PNJ

        # Attaque actuelle
        self.current_attack = None

        # Initialisation de l'UI
        self.ui = UI()

        self.create_map()

    def create_map(self):
        for row_index, row in enumerate(HOLBERTON_MAP):
            for col_index, col in enumerate(row):
                x = col_index * 64
                y = row_index * 64
                
                if col == 'x':
                    Tile((x, y), [self.visible_sprites, self.obstacle_sprites])
                if col == 'n':
                    NPC((x, y), [self.visible_sprites, self.interaction_sprites], self.obstacle_sprites)
                if col == 'p':
                    self.player = Player((x, y), [self.visible_sprites], self.obstacle_sprites)
                    
        self.player.interaction_sprites = self.interaction_sprites
        
        # On donne l'accès de l'UI au joueur pour que le PNJ puisse l'utiliser
        self.player.ui = self.ui
        
        # On connecte les fonctions d'attaque du joueur au gestionnaire du niveau
        self.player.create_attack = self.create_attack
        self.player.destroy_attack = self.destroy_attack

    def create_attack(self):
        self.current_attack = Weapon(self.player, [self.visible_sprites])

    def destroy_attack(self):
        if self.current_attack:
            self.current_attack.kill()
        self.current_attack = None

    def run(self):
        # Logique et dessin du monde
        self.visible_sprites.update()
        self.visible_sprites.draw(self.display_surface)
        
        # Dessin de l'UI par-dessus le monde
        self.ui.display(self.player)
