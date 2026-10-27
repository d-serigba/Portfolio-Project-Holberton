import pygame
from tile import Tile, TransitionTile
from player import Player
from npc import NPC
from weapon import Weapon
from ui import UI
from enemy import Enemy
from boss import MetroBoss
from boss import GardienDeLaVoiture
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
            # Ennemi invisible sans les lunettes -> on ne le dessine pas du tout
            if hasattr(sprite, 'sprite_type') and sprite.sprite_type == 'invisible_enemy':
                if not player.inventory.get("lunettes_baceux", False):
                    continue

            offset_pos = sprite.rect.topleft - self.offset
            self.display_surface.blit(sprite.image, offset_pos)
            
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
        ['x','x','x','x','x','x','x','x','x','x','x','x','x','x','x','x','x','x','x','x','x','x','x','x','x','x','x','x','x','x','x','x','x','x','x','x','x','x','x','x'],
        ['x','.','.','.','.','.','.','.','.','.','.','x','x','.','.','.','.','.','.','.','.','.','.','.','.','.','.','.','.','.','.','.','.','.','.','.','.','.','.','x'],
        ['x','.','p','.','.','.','.','e','.','.','.','x','x','.','.','.','e','.','.','.','.','.','x','x','.','.','.','.','.','.','.','.','.','.','.','.','.','.','.','x'],
        ['x','.','.','.','.','.','.','.','.','.','.','.','.','.','.','.','.','.','.','.','.','.','x','x','.','.','.','.','.','.','.','.','.','.','.','.','.','.','.','x'],
        ['x','.','.','.','.','.','.','.','.','.','.','.','.','.','.','.','.','.','.','.','.','.','.','.','.','.','.','.','e','.','.','.','.','.','.','.','.','.','.','x'],
        ['x','.','.','.','e','.','.','.','.','.','.','.','.','.','.','.','.','.','.','.','.','.','.','.','.','.','.','.','.','.','.','.','.','.','.','.','B','.','.','x'],
        ['x','.','.','.','.','.','.','.','.','.','.','x','x','.','.','.','.','.','.','.','.','.','.','.','.','.','.','.','.','.','.','.','.','.','.','.','.','.','t2','x'],
        ['x','.','.','.','.','.','.','.','.','.','.','x','x','.','.','.','e','.','.','.','.','.','x','x','.','.','.','.','.','.','.','.','.','.','.','.','.','.','.','x'],
        ['x','.','.','.','.','.','.','.','.','.','.','.','.','.','.','.','.','.','.','.','.','.','x','x','.','.','.','.','.','.','.','.','.','.','.','.','.','.','.','x'],
        ['x','.','.','.','.','.','.','.','.','.','.','.','.','.','.','.','.','.','.','.','.','.','.','.','.','.','.','.','.','.','.','.','.','.','.','.','.','.','.','x'],
        ['x','x','x','x','x','x','x','x','x','x','x','x','x','x','x','x','x','x','x','x','x','x','x','x','x','x','x','x','x','x','x','x','x','x','x','x','x','x','x','x'],
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
        ['x','x','x','x','x','x','x','x','x','x','x'],
        ['x',' ',' ',' ',' ','t4',' ',' ',' ',' ','x'], # La rampe de sortie vers l'autoroute
        ['x',' ',' ',' ',' ',' ',' ',' ',' ',' ','x'],
        ['x',' ',' ',' ',' ',' ',' ',' ',' ',' ','x'],
        ['x',' ',' ',' ','E',' ',' ',' ',' ',' ','x'],  # Le Gardien au centre de l'arène
        ['x',' ',' ',' ',' ',' ',' ',' ',' ',' ','x'],
        ['x',' ',' ',' ',' ',' ',' ',' ',' ',' ','x'],
        ['x',' ',' ',' ',' ',' ',' ',' ',' ',' ','x'],
        ['x',' ',' ',' ',' ',' ',' ',' ',' ',' ','x'],
        ['x','p',' ',' ',' ',' ',' ',' ',' ',' ','x'], # Arnaud entre par le bas
        ['x','x','x','x','x','x','x','x','x','x','x'],
    ],
    # MONDE 3 : L'Autoroute (Grande carte verticale)
    "autoroute": [
        ['x','x','x','x','x','x','x','x','x','x','x'],
        ['x',' ',' ',' ',' ',' ',' ',' ',' ',' ','x'], # La sortie tout en haut vers la maison
        ['x',' ',' ',' ',' ',' ',' ',' ',' ','t4','x'], # 't4' pour la sortie
        ['x',' ','c',' ',' ',' ',' ','c',' ',' ','x'], # Plus de voies = plus de trafic ('c') !
        ['x',' ',' ',' ',' ','c',' ',' ',' ',' ','x'],
        ['x',' ',' ',' ',' ',' ',' ',' ','c',' ','x'],
        ['x',' ','c',' ',' ',' ',' ',' ',' ',' ','x'],
        ['x',' ',' ',' ',' ',' ','c',' ',' ',' ','x'],
        ['x',' ',' ',' ','c',' ',' ',' ',' ',' ','x'],
        ['x',' ',' ',' ',' ',' ',' ',' ','c',' ','x'],
        ['x',' ','c',' ',' ',' ',' ',' ',' ',' ','x'],
        ['x',' ',' ',' ',' ',' ',' ','c',' ',' ','x'],
        ['x',' ',' ',' ','c',' ',' ',' ',' ',' ','x'],
        ['x',' ',' ',' ',' ',' ',' ',' ','c',' ','x'],
        ['x',' ',' ','c',' ',' ',' ',' ',' ',' ','x'],
        ['x',' ',' ',' ',' ',' ','c',' ',' ',' ','x'],
        ['x',' ',' ',' ',' ',' ',' ',' ',' ',' ','x'],
        ['x',' ','c',' ',' ',' ',' ',' ',' ',' ','x'],
        ['x',' ',' ',' ',' ','c',' ',' ',' ',' ','x'],
        ['x',' ',' ',' ',' ',' ',' ',' ','c',' ','x'],
        ['x',' ',' ','c',' ',' ',' ',' ',' ',' ','x'],
        ['x',' ',' ',' ',' ',' ',' ','c',' ',' ','x'],
        ['x',' ',' ',' ',' ','c',' ',' ',' ',' ','x'],
        ['x',' ',' ',' ',' ',' ',' ',' ',' ',' ','x'],
        ['x',' ','c',' ',' ',' ',' ','c',' ',' ','x'],
        ['x',' ',' ',' ',' ',' ',' ',' ',' ',' ','x'],
        ['x',' ',' ',' ','c',' ',' ',' ',' ',' ','x'],
        ['x',' ',' ',' ',' ',' ',' ',' ',' ',' ','x'],
        ['x',' ',' ',' ',' ',' ','c',' ',' ',' ','x'],
        ['x',' ',' ',' ',' ',' ',' ',' ',' ',' ','x'],
        ['x',' ',' ',' ',' ',' ',' ',' ',' ',' ','x'], # La Koenigsegg t'attend sur la droite
        ['x',' ','p',' ',' ',' ',' ',' ',' ',' ','x'], # Arnaud commence en bas à gauche
        ['x',' ',' ',' ',' ',' ',' ',' ',' ',' ','x'],
        ['x','x','x','x','x','x','x','x','x','x','x'],
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
    ],
    "ecran_fin": [
        ['x','x','x','x','x','x','x','x','x','x','x'],
        ['x',' ',' ',' ',' ',' ',' ',' ',' ',' ','x'],
        ['x',' ',' ',' ',' ',' ',' ',' ',' ',' ','x'],
        ['x',' ',' ',' ',' ',' ',' ',' ',' ',' ','x'],
        ['x',' ',' ','n','p','n','n',' ',' ',' ','x'], # La famille et Arnaud alignés !
        ['x',' ',' ',' ',' ',' ',' ',' ',' ',' ','x'],
        ['x',' ',' ',' ',' ',' ',' ',' ',' ',' ','x'],
        ['x',' ',' ',' ',' ',' ',' ',' ',' ',' ','x'],
        ['x',' ',' ',' ',' ',' ',' ',' ',' ',' ','x'],
        ['x',' ',' ',' ',' ',' ',' ',' ',' ',' ','x'],
        ['x','x','x','x','x','x','x','x','x','x','x'],
    ],
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
        self.attack_sprites = pygame.sprite.Group()

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
                "Pere d'Arnaud: 'Arnaud ! Tu es enfin la!'",
                "Frere d'Arnaud: 'Sauve-nous Arnaud!'",
                "Les Brothers : 'Te voilà enfin Arnaud!'"
            ])

        if self.current_zone == "ecran_fin":
            self.ui.show_message([
                "Bravo ! Vous avez vaincu Abdel et Niko et sauvé votre famille !",
                "Bon bah... C'est la fin du jeu vous pouvez fermer la fenêtre maintenant.",
                "Vous êtes encore là ? J'ai dit que c'était fini ! Cassez vous maintenant !"
            ])

    def create_map(self):
        layouts = ZONES[self.current_zone]

        # 🟢 PASSAGE 1 : on cherche et crée le joueur EN PREMIER, quoi qu'il arrive
        for row_index, row in enumerate(layouts):
            for col_index, col in enumerate(row):
                if col == 'p':
                    x = col_index * 64
                    y = row_index * 64
                    self.player = Player((x, y), [self.visible_sprites], self.obstacle_sprites, self.create_attack, self.destroy_attack, self.player_inventory, self.current_zone)
                
        # 🟢 PASSAGE 2 : tout le reste, self.player existe déjà à coup sûr
        for row_index, row in enumerate(layouts):
            for col_index, col in enumerate(row):
                x = col_index * 64
                y = row_index * 64

                if col == 'x':
                    Tile((x, y), [self.visible_sprites, self.obstacle_sprites], 'mur')
                # IL FAUT AJOUTER TES AUTRES OBSTACLES :
                elif col == 'm' or col == 'r': 
                    Tile((x, y), [self.visible_sprites, self.obstacle_sprites])
                elif col == 'p':
                    continue
                elif col == 'n':
                    NPC((x, y), [self.visible_sprites, self.interaction_sprites], self.obstacle_sprites, self.player)
                
                # --- NOUVEAU SYSTÈME DE TRANSITION DIRECTE ---
                elif col == 't1': 
                    TransitionTile((x, y), [self.visible_sprites, self.transition_sprites], "metro")
                elif col == 't2': 
                    TransitionTile((x, y), [self.visible_sprites, self.transition_sprites], "rer")
                elif col == 't3': 
                    # 🟢 CORRECTION : Le RER mène d'abord au Parking !
                    TransitionTile((x, y), [self.visible_sprites, self.transition_sprites], "parking")
                elif col == 't4': 
                    # 🟢 CORRECTION : Double usage de t4 !
                    # Si on est dans le parking, t4 mène à l'autoroute. Sinon, à la maison.
                    target = "autoroute" if self.current_zone == "parking" else "maison"
                    TransitionTile((x, y), [self.visible_sprites, self.transition_sprites], target)
                
                elif col == 'B':
                    MetroBoss((x, y), [self.visible_sprites, self.attackable_sprites], self.obstacle_sprites, self.spawn_reward)
                elif col == 'bi': # Ton Boss Invisible du RER
                    # 1. On crée le boss normalement en le mettant dans les bons groupes
                    boss_invisible = MetroBoss((x, y), [self.visible_sprites, self.attackable_sprites], self.obstacle_sprites, None)
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
                elif col == 'E':
                    GardienDeLaVoiture((x, y), [self.visible_sprites, self.attackable_sprites], self.obstacle_sprites, self.spawn_keys, self.ui)
                elif col == 'F':
                    # On fait apparaître deux Brothers côte à côte pour doubler le défi
                    Brother((x - 150, y), [self.visible_sprites, self.attackable_sprites], self.obstacle_sprites, "Abdel")
                    Brother((x + 150, y), [self.visible_sprites, self.attackable_sprites], self.obstacle_sprites, "Nikola")
        

        # Configuration du joueur
        self.player.interaction_sprites = self.interaction_sprites
        self.player.ui = self.ui
        self.player.create_attack = self.create_attack
        self.player.destroy_attack = self.destroy_attack

        # Si on change de zone, on réinjecte l'inventaire précédent pour ne rien perdre
        if self.player_inventory:
            self.player.inventory = self.player_inventory
            if self.player.inventory.get("epee_lego"):
                self.player.current_weapon = "epee_lego"
            elif self.player.inventory.get("opinel"):
                self.player.current_weapon = "opinel"

       # 🟢 L'ELLIPSE CINÉMATOGRAPHIQUE
        if self.current_zone == "autoroute" and self.player.inventory.get("cles_koenigsegg"):
            self.player.current_weapon = "mains_nues"
            self.player.speed = 12
            self.victory_triggered = False
            self.victory_timer = 0
            
            # --- CORRECTION ICI : Inversion des dimensions pour la verticale ---
            # Largeur : 45 (profil affiné), Hauteur : 80 (châssis long)
            self.player.image = pygame.Surface((45, 80)) 
            
            self.player.image.fill((220, 220, 220)) # Voiture Blanche/Argent
            self.player.rect = self.player.image.get_rect(center=self.player.rect.center)

            self.victory_triggered = False
            self.victory_timer = 0

    def create_attack(self):
        self.current_attack = Weapon(self.player, [self.visible_sprites])

    def destroy_attack(self):
        if self.current_attack:
            self.current_attack.kill()
        self.current_attack = None

    def check_transitions(self):
        for sprite in self.transition_sprites:
            if sprite.hitbox.colliderect(self.player.hitbox):
                
                # --- LES PORTES ---
                if hasattr(sprite, 'target_zone'):
                    # Si on veut aller sur l'autoroute sans les clés, on bloque !
                    target = sprite.target_zone
                    if target == "autoroute" and not self.player.inventory.get("cles_koenigsegg"):
                        self.ui.show_message("Il vous faut les cles de la voiture pour passer !")
                        self.player.hitbox.y += 10 # Repousse le joueur en arrière
                    else:
                        if self.change_zone_callback:
                            self.change_zone_callback(target, self.player.inventory)
                            
                # --- LES OBJETS ---
                elif hasattr(sprite, 'item_name'):
                    item = sprite.item_name
                    self.player.inventory[item] = True
                    
                    if item == "lunettes_baceux":
                        self.player.current_weapon = item
                        self.ui.show_message("Lunettes de baceux equipées!")
                    elif item == "cles_koenigsegg":
                        # On ne change pas l'arme, on garde juste les clés en poche pour le moment
                        self.ui.show_message("Cles récupérées ! Direction l'autoroute !")
                    elif item == "epee_lego":
                        # 🟢 NOUVEAU : Changement d'arme et message de confirmation
                        self.player.current_weapon = "epee_lego"
                        self.ui.show_message("Épée en Lego obtenue !")
                    
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

        if getattr(self, 'victory_triggered', False):
            if pygame.time.get_ticks() - self.victory_timer > 5000:
                if self.change_zone_callback:
                    self.change_zone_callback("ecran_fin", self.player.inventory)
                    self.victory_triggered = False # On réinitialise pour éviter un bug

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
                    # 🟢 CORRECTION : Utilisation de getattr pour éviter le crash !
                    if self.current_zone == "maison" and len(self.attackable_sprites) <= 1 and enemy.health <= 0:
                        # Si la variable n'existe pas, on considère qu'elle est "False"
                        if not getattr(self, 'victory_triggered', False):
                            self.victory_triggered = True
                            self.victory_timer = pygame.time.get_ticks()
                            self.ui.show_message("Abdel et Niko ont tous les deux ete vaincus !")
                    break

    def spawn_reward(self, pos):
        """Fait apparaître l'Épée en Lego"""
        self.reward_item = ItemTile(pos, [self.visible_sprites, self.transition_sprites], "epee_lego")
        self.ui.show_message("Le Boss des crackheads a été vaincu !")

    def spawn_keys(self, pos):
        """Fait apparaître les clés après la mort du boss du parking"""
        ItemTile(pos, [self.visible_sprites, self.transition_sprites], "cles_koenigsegg")
        self.ui.show_message("Le sbire a fait tomber des clés de voiture.")

    def check_item_pickup(self):
        """Vérifie si Arnaud marche sur l'item légendaire"""
        if hasattr(self, 'reward_item') and self.reward_item:
            if self.player.hitbox.colliderect(self.reward_item.hitbox):
                self.player.inventory["epee_lego"] = True
                self.player.current_weapon = "epee_lego"
                self.ui.show_message("Vous avez obtenu l'Epee en Lego !")
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
