import os
import pygame
from support import import_sprite_sheet # 🟢 Notre emporte-pièce !

class Player(pygame.sprite.Sprite):
    def __init__(self, pos, groups, obstacle_sprites, create_attack=None, destroy_attack=None, player_inventory=None, zone_name=None):
        super().__init__(groups)
        
        # --- PARAMÈTRES DE BASE (LA PEAU) ---
        self.image = pygame.Surface((48, 64))
        self.image.fill((0, 102, 204)) # Bleu Arnaud par défaut (sécurité)
        
        # --- SYSTÈME D'ANIMATION ---
        self.status = 'face_droite' # Arnaud regarde de 3/4 face par défaut
        self.frame_index = 0
        self.animation_speed = 0.15
        
        # Arme par défaut au lancement
        self.current_weapon = 'mains_nues' 

        self.zone_name = zone_name
        
        # On charge les nouvelles armoires (découpe de l'image)
        self.import_player_assets()
        
        # 1. Arnaud met son t-shirt (l'image prend sa taille finale, par ex 128x128)
        self.image = self.wardrobes['mains_nues'][self.status][0]

        # 2. SEULEMENT MAINTENANT, on crée les boîtes basées sur cette image
        self.rect = self.image.get_rect(topleft=pos)

        # 3. On taille la hitbox (l'ombre) dans cette grande image
        # Avant :
        # -90 pour bien écraser la largeur (les côtés)
        # -40 pour rabaisser le plafond vers la tête
        # (N'hésite pas à ajuster : si -40 est trop haut, essaie -50 ou -60)
        self.hitbox = self.rect.inflate(-30, -15) # 64x64 -> hitbox 44x54, largement positif

        # --- DÉPLACEMENTS (LES MUSCLES) ---
        self.direction = pygame.math.Vector2()
        self.speed = 5
        self.facing = 'down' # Permet de savoir où Arnaud regarde pour les attaques

        # --- ÉTATS DU JOUEUR (LES RÉFLEXES) ---
        self.is_attacking = False
        self.attack_cooldown = 400 # Temps de l'attaque en millisecondes
        self.attack_time = 0

        # --- ÉLÉMENTS DE L'HISTOIRE (LES POCHES) ---
        # On conserve l'inventaire précis avec les objets de ton univers
        self.inventory = player_inventory if player_inventory else {
            "opinel": False, 
            "epee_lego": False, 
            "lunettes_baceux": False, 
            "koenigsegg": False
        }

        # --- LIAISONS AVEC LE MONDE (LES YEUX) ---
        self.obstacle_sprites = obstacle_sprites
        self.interaction_sprites = None 
        self.create_attack = create_attack
        self.destroy_attack = destroy_attack

        # --- STATISTIQUES VITALES (LE COEUR) ---
        self.max_health = 20
        self.health = 20
        
        # Invulnérabilité temporaire après un coup
        self.vulnerable = True
        self.hurt_time = 0
        self.invulnerability_duration = 5000 

        # Le réglage fin de l'ourlet (en pixels). 
        # Si le carré bleu est trop bas, on augmente ce chiffre (ex: 8, 12, 16...)
        self.pixel_offset_y = 0

    def input(self):
        if self.is_attacking:
            return # Bloque les actions si Arnaud est déjà en train de frapper

        keys = pygame.key.get_pressed()

        # Déplacements Y
        if keys[pygame.K_UP] or keys[pygame.K_z]:
            self.direction.y = -1
            self.status = 'face_haut'   # <-- Le signal pour l'habilleur
            self.facing = 'up'          # <-- Ton signal d'origine
        elif keys[pygame.K_DOWN] or keys[pygame.K_s]:
            self.direction.y = 1
            self.status = 'face_bas'    # <-- Le signal pour l'habilleur
            self.facing = 'down'
        else:
            self.direction.y = 0

        # Déplacements X
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.direction.x = 1
            self.status = 'face_droite' # <-- Le signal pour l'habilleur
            self.facing = 'right'
        elif keys[pygame.K_LEFT] or keys[pygame.K_q]:
            self.direction.x = -1
            self.status = 'face_gauche' # <-- Le signal pour l'habilleur
            self.facing = 'left'
        else:
            self.direction.x = 0

        # Touche d'action (Interaction PNJ)
        if keys[pygame.K_RETURN]:
            if not hasattr(self, 'return_pressed') or not self.return_pressed:
                self.check_npc()
                self.return_pressed = True
        else:
            self.return_pressed = False

        # Touche d'attaque (Espace) - Le Cran de Sûreté
        # L'attaque ne part QUE si on tient autre chose que 'mains_nues'
        # LA DÉTENTE (Touche Espace)
        if keys[pygame.K_SPACE]:
            # On regarde l'heure qu'il est en millisecondes
            current_time = pygame.time.get_ticks()
                
            # On vérifie le dossier de l'armurerie ET le chronomètre
            if self.current_weapon != 'mains_nues' and current_time - self.attack_time >= self.attack_cooldown:
                self.is_attacking = True
                self.attack_time = current_time # On lance le chrono pour ce coup !
                    
                self.direction.x = 0 
                self.direction.y = 0
                self.frame_index = 0 
                    
                if self.create_attack:
                    self.create_attack()

    def check_npc(self):
        if self.interaction_sprites:
            check_rect = self.hitbox.inflate(-90, 100)
            for sprite in self.interaction_sprites:
                if hasattr(sprite, 'interact') and sprite.hitbox.colliderect(check_rect):
                    sprite.interact(self)

    def cooldowns(self):
        """Gère le timing pour arrêter l'attaque automatiquement"""
        current_time = pygame.time.get_ticks()
        if self.is_attacking:
            if current_time - self.attack_time >= self.attack_cooldown:
                self.is_attacking = False
                if self.destroy_attack:
                    self.destroy_attack() # On supprime la hitbox de l'arme

    def move(self, speed):
        if self.direction.magnitude() != 0:
            self.direction = self.direction.normalize()

        # Axe X : Mouvement -> Impact
        self.hitbox.x += self.direction.x * speed
        self.collision('horizontal')

        # Axe Y : Mouvement -> Impact
        self.hitbox.y += self.direction.y * speed
        self.collision('vertical')

        # À la fin, on aligne le dessin sur la réalité physique (la hitbox)
        self.rect.midbottom = (self.hitbox.midbottom[0], self.hitbox.midbottom[1] + self.pixel_offset_y)

    def collision(self, direction):
        if direction == 'horizontal':
            for sprite in self.obstacle_sprites:
                # Si le champ de force d'Arnaud touche un obstacle (qui n'est pas lui-même)
                if sprite.hitbox.colliderect(self.hitbox) and sprite != self:
                    if self.direction.x > 0: # Arnaud fonce vers la DROITE
                        # On cloue le côté droit d'Arnaud sur le côté gauche du mur
                        self.hitbox.right = sprite.hitbox.left
                    elif self.direction.x < 0: # Arnaud fonce vers la GAUCHE
                        # On cloue le côté gauche d'Arnaud sur le côté droit du mur
                        self.hitbox.left = sprite.hitbox.right

        if direction == 'vertical':
            for sprite in self.obstacle_sprites:
                if sprite.hitbox.colliderect(self.hitbox) and sprite != self:
                    if self.direction.y > 0: # Arnaud fonce vers le BAS
                        # On cloue le bas d'Arnaud sur le haut du mur
                        self.hitbox.bottom = sprite.hitbox.top
                    elif self.direction.y < 0: # Arnaud fonce vers le HAUT
                        # On cloue le haut d'Arnaud sur le bas du mur
                        self.hitbox.top = sprite.hitbox.bottom

    def get_damage(self, amount):
        """Appelée par level.py quand Arnaud se fait toucher"""
        if self.vulnerable:
            self.health -= amount
            self.vulnerable = False
            self.hurt_time = pygame.time.get_ticks()
            #self.ui.show_message(f"Aïe ! PV restants : {self.health}/{self.max_health}")
            print(f"Aïe ! PV restants : {self.health}/{self.max_health}")

    def check_invulnerability(self):
        """Rend Arnaud à nouveau vulnérable après le délai d'anti-framerate"""
        if not self.vulnerable:
            current_time = pygame.time.get_ticks()
            if current_time - self.hurt_time >= self.invulnerability_duration:
                self.vulnerable = True

    def get_status(self):
        # 1. PRIORITÉ ABSOLUE : L'ATTAQUE
        if self.is_attacking:
            self.direction.x = 0
            self.direction.y = 0
            if not '_attack' in self.status:
                if '_idle' in self.status:
                    self.status = self.status.replace('_idle', '')
                self.status = self.status + '_attack'

        # 2. L'IMMOBILITÉ (Arnaud est à l'arrêt, le combat est fini)
        elif self.direction.x == 0 and self.direction.y == 0:
            # 🚨 LA CORRECTION : On arrache de force l'étiquette d'attaque si elle était restée !
            if '_attack' in self.status:
                self.status = self.status.replace('_attack', '')
                
            # Ensuite seulement, on lui colle son étiquette de repos
            if not '_idle' in self.status:
                self.status = self.status + '_idle'

        # 3. LE MOUVEMENT (Arnaud marche)
        else:
            if '_idle' in self.status:
                self.status = self.status.replace('_idle', '')
            if '_attack' in self.status:
                self.status = self.status.replace('_attack', '')

    def update(self):
        self.input()
        self.get_status()   # 2. On calcule s'il est de dos, de face, etc.
        self.animate()      # 3. ON CHANGE L'IMAGE (La manivelle tourne !)
        self.move(self.speed)
        self.cooldowns()
        self.check_invulnerability() # <-- APPEL DE LA MÉTHODE SÉCURISÉE

    def import_player_assets(self):
        # --- BIFURCATION VÉHICULE (Si on est sur l'autoroute) ---
        if self.zone_name == "autoroute":
            # 1. On charge l'image unique (en partant du principe qu'elle pointe vers le HAUT par défaut)
            car_img_originale = pygame.image.load('graphics/arnaud/koenigsegg.png').convert_alpha()
    
            # 🟢 On redimensionne d'abord à la même taille que les voitures de car.py (50x80)
            car_img = pygame.transform.scale(car_img_originale, (50, 80))

            # 2. On prépare une armoire simplifiée (Le faux système d'animation)
            self.wardrobes = {'mains_nues': {}}

            # 3. On remplit tous les statuts possibles avec LA MÊME image, pas de rotation
            for state in [
                'face_haut', 'face_haut_idle', 'face_haut_attack',
                'face_bas', 'face_bas_idle', 'face_bas_attack',
                'face_gauche', 'face_gauche_idle', 'face_gauche_attack',
                'face_droite', 'face_droite_idle', 'face_droite_attack'
            ]:
                self.wardrobes['mains_nues'][state] = [car_img]

            # 🚨 STOP ABSOLU : On sort de la fonction. Le reste du code d'Arnaud ne sera jamais lu pour ce niveau.
            return 
            
        # --- LE RESTE DU CODE NORMAL (Si on est à pied) ---
        # (Ici se trouve ton code actuel avec sheet_base, sheet_opinel, w, h = 64, 64, get_frame, fill_wardrobe, etc...)

        # 1. CHARGEMENT DE TOUTES LES PLANCHES
        sheet_base = pygame.image.load('graphics/arnaud/arnaud_marche_normal.png').convert_alpha()
        sheet_opinel_marche = pygame.image.load('graphics/arnaud/opinel_marche.png').convert_alpha()
        sheet_opinel_attaque = pygame.image.load('graphics/arnaud/opinel_attack.png').convert_alpha()
        sheet_epee_marche = pygame.image.load('graphics/arnaud/epee_marche.png').convert_alpha()
        sheet_epee_attaque = pygame.image.load('graphics/arnaud/lego_attack.png').convert_alpha()
        sheet_lunettes_marche = pygame.image.load('graphics/arnaud/lunettes_marche.png').convert_alpha()
        sheet_lunettes_attaque = pygame.image.load('graphics/arnaud/lunettes_attack.png').convert_alpha()

        w, h = 64, 64 

        # 2. LE NOUVEL EMPORTE-PIÈCE (Il demande la planche 'sheet' maintenant)
        def get_frame(sheet, col, row):
            surface = pygame.Surface((w, h), pygame.SRCALPHA)
            surface.blit(sheet, (0, 0), (col * w, row * h, w, h))
            return surface

        # 3. PRÉPARATION DE LA GRANDE ARMOIRE GLOBALE
        self.wardrobes = {
            'mains_nues': {},
            'opinel': {},
            'epee_lego': {},
            'lunettes': {} 
        }

        # 4. LE ROBOT DE RANGEMENT 
        def fill_wardrobe(wardrobe_name, sheet_marche, sheet_attaque):
            # Ligne 0 : Droite
            self.wardrobes[wardrobe_name]['face_droite'] = [get_frame(sheet_marche, 0, 0), get_frame(sheet_marche, 1, 0), get_frame(sheet_marche, 2, 0)]
            self.wardrobes[wardrobe_name]['face_droite_idle'] = [get_frame(sheet_marche, 0, 0)]
            # Ligne 1 : Gauche
            self.wardrobes[wardrobe_name]['face_gauche'] = [get_frame(sheet_marche, 0, 1), get_frame(sheet_marche, 1, 1), get_frame(sheet_marche, 2, 1)]
            self.wardrobes[wardrobe_name]['face_gauche_idle'] = [get_frame(sheet_marche, 0, 1)]
            # Ligne 2 : Haut
            self.wardrobes[wardrobe_name]['face_haut'] = [get_frame(sheet_marche, 0, 2), get_frame(sheet_marche, 1, 2), get_frame(sheet_marche, 2, 2)]
            self.wardrobes[wardrobe_name]['face_haut_idle'] = [get_frame(sheet_marche, 0, 2)]
            # Ligne 3 : Bas 
            self.wardrobes[wardrobe_name]['face_bas'] = [get_frame(sheet_marche, 0, 3), get_frame(sheet_marche, 1, 3), get_frame(sheet_marche, 2, 3)]
            self.wardrobes[wardrobe_name]['face_bas_idle'] = [get_frame(sheet_marche, 0, 3)]

            # --- LES ATTAQUES (2 frames : Idle puis Frappe) ---
            if sheet_attaque: 
                # L'emporte-pièce prend : get_frame(planche, colonne, ligne)
                
                # GAUCHE (On va chercher la colonne 1 sur la planche d'attaque)
                self.wardrobes[wardrobe_name]['face_gauche_attack'] = [get_frame(sheet_marche, 0, 0), get_frame(sheet_attaque, 1, 0)]
                
                # DROITE (On va chercher la colonne 0 sur la planche d'attaque)
                self.wardrobes[wardrobe_name]['face_droite_attack'] = [get_frame(sheet_marche, 0, 1), get_frame(sheet_attaque, 0, 0)]
                
                # HAUT (Dos)
                # Frame 0 = Marche (Col 0, Ligne 2) | Frame 1 = Attaque (Col 0, Ligne 1)
                self.wardrobes[wardrobe_name]['face_haut_attack'] = [get_frame(sheet_marche, 0, 2), get_frame(sheet_attaque, 0, 1)]
                
                # BAS (Face)
                # Frame 0 = Marche (Col 0, Ligne 3) | Frame 1 = Attaque (Col 1, Ligne 1)
                self.wardrobes[wardrobe_name]['face_bas_attack'] = [get_frame(sheet_marche, 0, 3), get_frame(sheet_attaque, 1, 1)]

        # 5. EXÉCUTION DU ROBOT (C'est lui qui appelle get_frame avec les 3 ingrédients !)
        fill_wardrobe('mains_nues', sheet_base, None) 
        fill_wardrobe('opinel', sheet_opinel_marche, sheet_opinel_attaque)
        fill_wardrobe('epee_lego', sheet_epee_marche, sheet_epee_attaque)
        fill_wardrobe('lunettes', sheet_lunettes_marche, sheet_lunettes_attaque)

    def animate(self):
        current_wardrobe = self.current_weapon

        # Le style prime : si on a les lunettes de baceux, on force cet acteur
        # (sauf en voiture, où il n'y a qu'une seule armoire 'mains_nues')
        if self.zone_name != "autoroute" and self.inventory.get("lunettes_baceux", False):
            current_wardrobe = 'lunettes'

        animation = self.wardrobes[current_wardrobe][self.status]

        # 3. Le pouce tourne la page du folioscope
        self.frame_index += self.animation_speed

        # 4. Si on arrive à la fin de la bobine
        if self.frame_index >= len(animation):
            self.frame_index = 0
            # Si c'était une attaque, c'est fini, on abaisse l'arme
            if self.is_attacking:
                self.is_attacking = False

                # 🚨 L'INTERVENTION DU NETTOYEUR
                # On vérifie si le joueur possède l'ordre de destruction, et on l'exécute !
                if hasattr(self, 'destroy_attack') and self.destroy_attack:
                    self.destroy_attack()

        # 5. On affiche la photo
        self.image = animation[int(self.frame_index)]

        # 6. LA SUPER-GLUE (On garde l'ourlet de collision intact !)
        self.rect = self.image.get_rect(midbottom=(self.hitbox.midbottom[0], self.hitbox.midbottom[1] + self.pixel_offset_y))
