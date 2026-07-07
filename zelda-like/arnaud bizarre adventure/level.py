import pygame
from tile import Tile, TransitionTile
from player import Player
from npc import NPC
from weapon import Weapon
from ui import UI
from enemy import Enemy
from boss import MetroBoss
from tile import Tile, TransitionTile, ItemTile
from car import Car
from final_boss import Brother

class YSortCameraGroup(pygame.sprite.Group):
    def __init__(self):
        super().__init__()
        self.display_surface = pygame.display.get_surface()
        self.half_width = self.display_surface.get_size()[0] // 2
        self.half_height = self.display_surface.get_size()[1] // 2
        self.offset = pygame.math.Vector2()

    def custom_draw(self, player):
        self.offset.x = player.rect.centerx - self.half_width
        self.offset.y = player.rect.centery - self.half_height

        for sprite in sorted(self.sprites(), key=lambda sprite: sprite.rect.centery):
            offset_pos = sprite.rect.topleft - self.offset
            
            # --- MÉCANIQUE D'INVISIBILITÉ DES LUNETTES ---
            if hasattr(sprite, 'sprite_type') and sprite.sprite_type == 'invisible_enemy':
                # Si le joueur n'a PAS les lunettes, on ne dessine PAS l'ennemi (mais il existe et peut frapper)
                if not player.inventory.get("lunettes_baceux", False):
                    continue 
            
            self.display_surface.blit(sprite.image, offset_pos)

# Nos deux cartes : l'Open Space et la Station de Métro
ZONES = {
    "holberton": [
        ['x','x','x','x','x','x','x','x','x','x','x','x','x','x','x'],
        ['x',' ',' ',' ',' ','x',' ',' ',' ',' ',' ',' ','x','t1','x'], # 't' est la porte de sortie
        ['x',' ',' ',' ',' ','x',' ',' ',' ',' ',' ',' ','x',' ','x'],
        ['x',' ','x',' ',' ',' ',' ',' ',' ','x',' ',' ',' ',' ','x'],
        ['x','p','x',' ',' ',' ',' ',' ','n','x',' ',' ',' ',' ','x'],
        ['x','x','x','x','x','x','x','x','x','x','x','x','x','x','x'],
    ],
    "metro": [
        ['x','x','x','x','x','x','x','x','x','x','x','x','x','x','x','x','x','x','x','x'],
        ['.','.','.','.','.','.','.','.','.','.','.','.','.','.','.','.','.','.','.','.'],
        ['x','p','.','.','.','.','.','.','.','e','.','.','.','.','e','.','.','.','.','x'],
        ['.','.','.','.','.','.','.','.','.','.','.','.','.','.','.','.','.','.','.','.'], 
        ['.','.','.','.','e','.','.','.','.','.','.','.','.','.','.','.','.','.','B','.'],
        ['x','.','.','.',' .','X','x','x','x','x','.','.','e','.','.','.','.','.','t2','x'], # Transition 't' après le boss
        ['x','x','x','x','x','x','x','x','x','x','x','x','x','x','x','x','x','x','x','x'],
    ],
    # MONDE 2 : Le wagon de RER (Tracé très long et rectiligne)
    "rer": [
        ['x','x','x','x','x','x','x','x','x','x','x','x','x','x','x','x','x','x','x','x','x','x','x','x','x','x','x','x','x','x'],
        ['x','','.','.','.','.','L','.','.','.','.','.','.','.','.','.','.','.','.','.','.','.','.','.','.','.','.','.','.','x'],
        ['x','p','.','.','.','.','.','.','.','.','.','.','.','.','.','.','.','.','.','.','.','ei','.','.','.','.','.','.','.','x'],
        ['x','.','.','.','e','.','.','.','.','.','.','.','.','.','ei','.','.','.','.',',','.','.','.','.','.','.','bi','.','x'], # Plus d'espace au centre pour 'bi'
        ['x','.','.','.','.','.','.','.','.','ei','.','.','.','.','.','.','.','.','.','.','.','.','.','.','.','.','.','.','t3','x'],
        ['x','','.','.','.','.','.','.','.','.','.','.','.','.','.','.','.','.','.','.','.','.','.','.','.','.','.','.','.','x'],
        ['x','x','x','x','x','x','x','x','x','x','x','x','x','x','x','x','x','x','x','x','x','x','x','x','x','x','x','x','x','x'],
    ],
    # Ici, ei = Ennemi Invisible, bi = Boss Invisible, L = Lunettes de baceux au début du wagon
    "parking": [
        ['x','x','x','x','x','x','x'],
        ['x',' ',' ','t4',' ',' ','x'], # t4 vers l'autoroute une fois en voiture
        ['x',' ',' ','K',' ',' ','x'],  # La Koenigsegg gardée par l'ennemi
        ['x',' ',' ','E','.',' ','x'],  # 'E' est le concessionnaire corrompu / ennemi à battre
        ['x','p',' ',' ',' ',' ','x'],
        ['x','x','x','x','x','x','x'],
    ],
    # MONDE 3 : L'Autoroute (Grande carte verticale)
    "autoroute": [
        ['x','x','x','x','x','x','x'],
        ['x',' ',' ',' ',' ',' ','x'], # La sortie tout en haut vers la maison
        ['x',' ',' ',' ',' ','t4','x'], # 'K' pour la Koenigsegg Jesko au bout
        ['x',' ','c',' ',' ',' ','x'], # 'c' pour une voiture (obstacle mouvant)
        ['x',' ',' ',' ','c',' ','x'],
        ['x',' ',' ',' ',' ',' ','x'],
        ['x',' ',' ','c',' ',' ','x'],
        ['x',' ',' ',' ',' ',' ','x'],
        ['x','c',' ',' ',' ',' ','x'],
        ['x',' ',' ',' ',' ',' ','x'],
        ['x',' ',' ',' ',' ',' ','x'],
        ['x',' ',' ',' ',' ',' ','x'],
        ['x',' ',' ',' ',' ',' ','x'],
        ['x',' ',' ',' ',' ',' ','x'],
        ['x',' ',' ',' ',' ',' ','x'],
        ['x',' ',' ',' ',' ',' ','x'],
        ['x',' ',' ',' ',' ',' ','x'],
        ['x',' ',' ',' ',' ',' ','x'],
        ['x',' ',' ',' ',' ',' ','x'],
        ['x',' ',' ','K',' ',' ','x'],
        ['x','p',' ',' ',' ',' ','x'],
        ['x',' ',' ',' ',' ',' ','x'], # Arnaud commence en bas de l'autoroute
        ['x','x','x','x','x','x','x'],
    ],
    "maison": [
        ['x','x','x','x','x','x','x','x','x','x','x'],
        ['x',' ',' ',' ',' ',' ',' ',' ',' ',' ','x'],
        ['x',' ',' ',' ',' ','F',' ',' ',' ',' ','x'], # 'F' pour l'affrontement Final contre les Brothers
        ['x',' ',' ',' ',' ',' ',' ',' ',' ',' ','x'],
        ['x',' ',' ',' ',' ',' ',' ',' ',' ',' ','x'],
        ['x',' ',' ',' ',' ',' ',' ',' ',' ',' ','x'],
        ['x',' ',' ',' ',' ',' ',' ',' ',' ',' ','x'],
        ['x',' ',' ',' ',' ',' ',' ',' ',' ',' ','x'],
        ['x',' ',' ',' ',' ',' ',' ',' ',' ',' ','x'],
        ['x',' ',' ',' ','p',' ',' ',' ',' ',' ','x'], # Arnaud apparaît au centre de son salon
        ['x','x','x','x','x','x','x','x','x','x','x'],
    ]
}

class Level:
    def __init__(self, zone_name, player_inventory=None, change_zone_callback=None):
        self.display_surface = pygame.display.get_surface()
        self.current_zone = zone_name
        self.change_zone_callback = change_zone_callback
        self.player_inventory = player_inventory

        # Groupes de sprites
        self.visible_sprites = YSortCameraGroup()
        self.obstacle_sprites = pygame.sprite.Group()
        self.interaction_sprites = pygame.sprite.Group()
        self.transition_sprites = pygame.sprite.Group() # Nouveau groupe
        self.attackable_sprites = pygame.sprite.Group()

        self.current_attack = None
        self.ui = UI()

        self.create_map()

        if self.current_zone == "holberton" and not player_inventory:
            self.ui.show_message([
                "Le telephone d'Arnaud vibre...",
                "Inconnu: 'Allo Arnaud ? C'est Abdel & Niko.'",
                "Abdel & Niko: 'On retiens ta famille en otage, on t'attends a la maison...'",
                "Abdel & Niko: 'Et dépêche-toi... Avec tout le respect !'"
            ])

        if self.current_zone == "maison":
            self.ui.show_message([
                "Mere d'Arnaud: 'Arnaud ! Au secours!'",
                "Pere d'Arnaud: 'Arnaud ! Fais attention ! Ils sont derriere toi !!'",
                "Frere d'Arnaud: 'Sauve-nous Arnaud !'",
                "Les Brothers : 'Te voilà enfin Arnaud !'"
            ])

    def create_map(self):
        layouts = ZONES[self.current_zone]
        for row_index, row in enumerate(layouts):
            for col_index, col in enumerate(row):
                x = col_index * 64
                y = row_index * 64
                
                if col == 'x':
                    Tile((x, y), [self.visible_sprites, self.obstacle_sprites])
                elif col == 'n':
                    NPC((x, y), [self.visible_sprites, self.interaction_sprites], self.obstacle_sprites)
                
                # --- NOUVEAU SYSTÈME DE TRANSITION DIRECTE ---
                elif col == 't1': # Sortie d'Holberton
                    TransitionTile((x, y), [self.visible_sprites, self.transition_sprites], "metro")
                elif col == 't2': # Sortie du Métro
                    TransitionTile((x, y), [self.visible_sprites, self.transition_sprites], "rer")
                elif col == 't3': # Sortie du RER
                    TransitionTile((x, y), [self.visible_sprites, self.transition_sprites], "autoroute")
                elif col == 't4': # Sortie de l'Autoroute
                    TransitionTile((x, y), [self.visible_sprites, self.transition_sprites], "maison")
                
                elif col == 'B':
                    MetroBoss((x, y), [self.visible_sprites, self.attackable_sprites], self.obstacle_sprites, self.spawn_reward)
                elif col == 'bi': # Ton Boss Invisible du RER
                    # 1. On crée le boss normalement en le mettant dans les bons groupes
                    boss_invisible = MetroBoss((x, y), [self.visible_sprites, self.attackable_sprites], self.obstacle_sprites, self.spawn_reward)
                    # 2. On lui donne son attribut d'invisibilité juste après, sur sa propre ligne !
                    boss_invisible.sprite_type = 'invisible_enemy'
                elif col == 'e':
                    Enemy((x, y), [self.visible_sprites, self.attackable_sprites], self.obstacle_sprites)
                elif col == 'ei': # Ennemi Invisible du RER
                    ennemi_invisible = Enemy((x, y), [self.visible_sprites, self.attackable_sprites], self.obstacle_sprites)
                    ennemi_invisible.sprite_type = 'invisible_enemy'
                elif col == 'L':
                    ItemTile((x, y), [self.visible_sprites, self.transition_sprites], "lunettes_baceux")
                elif col == 'K':
                    ItemTile((x, y), [self.visible_sprites, self.transition_sprites], "koenigsegg")
                elif col == 'c':
                    Car((x, y), [self.visible_sprites])
                elif col == 'p':
                    self.player = Player((x, y), [self.visible_sprites], self.obstacle_sprites)
                elif col == 'F':
                    # On fait apparaître deux Brothers côte à côte pour doubler le défi
                    Brother((x - 40, y), [self.visible_sprites, self.attackable_sprites], self.obstacle_sprites, "Abdel")
                    Brother((x + 40, y), [self.visible_sprites, self.attackable_sprites], self.obstacle_sprites, "Nikola")
                

        # Configuration du joueur
        self.player.interaction_sprites = self.interaction_sprites
        self.player.ui = self.ui
        self.player.create_attack = self.create_attack
        self.player.destroy_attack = self.destroy_attack

        # Si on change de zone, on réinjecte l'inventaire précédent pour ne rien perdre
        if self.player_inventory:
            self.player.inventory = self.player_inventory
            if self.player.inventory["opinel"]:
                self.player.current_weapon = "opinel"

    def create_attack(self):
        self.current_attack = Weapon(self.player, [self.visible_sprites])

    def destroy_attack(self):
        if self.current_attack:
            self.current_attack.kill()
        self.current_attack = None

    def check_transitions(self):
        for sprite in self.transition_sprites:
            if sprite.hitbox.colliderect(self.player.hitbox):
                if hasattr(sprite, 'target_zone'): # C'est une vraie tuile de changement de niveau
                    if self.change_zone_callback:
                        self.change_zone_callback(sprite.target_zone, self.player.inventory)
                elif hasattr(sprite, 'item_name'): # C'est un item au sol !
                    self.player.inventory[sprite.item_name] = True
                    self.player.current_weapon = sprite.item_name
                    
                    if sprite.item_name == "lunettes_baceux":
                        self.ui.show_message("Lunettes de baceux equipées ! Vous y voyez plus clair.")
                elif sprite.item_name == "koenigsegg":
                    self.player.inventory["koenigsegg"] = True
                    self.player.current_weapon = "koenigsegg"
                    self.ui.show_message("Vous montez dans la Koenigsegg Jesko ! Vitesse MAXIMUM !")
                    self.player.speed = 12
                    
                    # Transformation visuelle : Arnaud est dans sa voiture blanche/argent
                    self.player.image = pygame.Surface((64, 40))
                    self.player.image.fill((220, 220, 220)) 
                    self.player.rect = self.player.image.get_rect(center=self.player.rect.center)
                    sprite.kill()

    def run(self):
        # Mettre à jour les comportements spécifiques des ennemis d'abord
        for sprite in self.visible_sprites:
            if hasattr(sprite, 'update_behavior'):
                sprite.update_behavior(self.player)

        # Logiques de collisions et de combat
        self.visible_sprites.update()
        self.check_transitions()
        self.attack_logic()
        self.enemy_damage_logic() # NOUVEAU
        self.car_collision_logic() # MIS À JOUR
        self.check_game_over()     # NOUVEAU

        # Dessin
        self.visible_sprites.custom_draw(self.player)
        self.ui.display(self.player)

        self.car_collision_logic()

    def car_collision_logic(self):
        """Modifiée pour enlever directement toute la vie (Mort instantanée par voiture)"""
        for sprite in self.visible_sprites:
            if hasattr(sprite, 'sprite_type') and sprite.sprite_type == 'obstacle_mouvant':
                if sprite.hitbox.colliderect(self.player.hitbox):
                    self.player.get_damage(self.player.max_health) # Mort directe !

    def attack_logic(self):
        """Vérifie si l'arme d'Arnaud touche un ennemi"""
        if self.current_attack: # Si Arnaud est en train de donner un coup
            # On cherche les collisions entre l'arme et les monstres éliminables
            for enemy in self.attackable_sprites:
                if self.current_attack.rect.colliderect(enemy.hitbox):
                    # L'ennemi prend un dégât !
                    enemy.health -= 1
                    
                    # On détruit temporairement l'arme pour éviter d'infliger 
                    # 60 dégâts par seconde sur la même animation
                    self.destroy_attack()
                    if self.current_zone == "maison" and len(self.attackable_sprites) <= 1 and enemy.health <= 0:
                        self.ui.show_message("Victoire ! Vous avez sauve votre famille !")
                    break

    def spawn_reward(self, pos):
        """Fait apparaître l'Épée en Lego"""
        self.reward_item = ItemTile(pos, [self.visible_sprites], "epee_lego")
        self.ui.show_message("Le Boss des crackheads a été vaincu ! Ramassez votre dû !")

    def check_item_pickup(self):
        """Vérifie si Arnaud marche sur l'item légendaire"""
        if hasattr(self, 'reward_item') and self.reward_item:
            if self.player.hitbox.colliderect(self.reward_item.hitbox):
                self.player.inventory["epee_lego"] = True
                self.player.current_weapon = "epee_lego"
                self.ui.show_message("Vous avez obtenu l'Epee en Lego ! Portee augmentée !")
                self.reward_item.kill()
                self.reward_item = None

    def check_game_over(self):
        """Vérifie si Arnaud n'a plus de PV ou s'est fait écraser"""
        if self.player.health <= 0:
            # On appelle le gestionnaire principal (main.py) pour relancer la zone actuelle
            if self.change_zone_callback:
                self.ui.show_message("Game Over... Réapparition dans la zone.")
                pygame.time.wait(1000) # Petite pause dramatique
                # On recharge la MÊME zone avec l'inventaire préservé
                self.change_zone_callback(self.current_zone, self.player.inventory)

    def enemy_damage_logic(self):
        """Vérifie si les ennemis touchent physiquement Arnaud"""
        for sprite in self.attackable_sprites:
            if sprite.hitbox.colliderect(self.player.hitbox):
                # Si c'est le Boss final ou de métro, ils font 2 dégâts, les crackheads 1 dégât
                damage = 2 if hasattr(sprite, 'status') or hasattr(sprite, 'name') else 1
                self.player.get_damage(damage)
