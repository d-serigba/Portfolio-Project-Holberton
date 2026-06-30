import pygame

class Player(pygame.sprite.Sprite):
    def __init__(self, pos, groups, obstacle_sprites):
        super().__init__(groups)
        self.image = pygame.Surface((48, 64))
        self.image.fill((0, 102, 204)) # Bleu Arnaud
        self.rect = self.image.get_rect(topleft=pos)
        self.hitbox = self.rect.inflate(-10, -26) 

        # Déplacements
        self.direction = pygame.math.Vector2()
        self.speed = 5
        self.facing = 'down' # Permet de savoir où Arnaud regarde

        # États du joueur
        self.is_attacking = False
        self.attack_cooldown = 300 # Temps de l'attaque en millisecondes
        self.attack_time = 0

        # Éléments de l'histoire (GDD)
        self.inventory = {
            "opinel": False,          
            "epee_lego": False,       
            "lunettes_baceux": False, 
            "koenigsegg": False       
        }
        self.current_weapon = None

        # Liaisons avec le monde
        self.obstacle_sprites = obstacle_sprites
        self.interaction_sprites = None 
        self.create_attack = None # Fonction qu'on liera dans level.py
        self.destroy_attack = None # Fonction qu'on liera dans level.py

    def input(self):
        if self.is_attacking:
            return # Bloque les actions si Arnaud est déjà en train de frapper

        keys = pygame.key.get_pressed()

        # Déplacements Y
        if keys[pygame.K_UP] or keys[pygame.K_z]:
            self.direction.y = -1
            self.facing = 'up'
        elif keys[pygame.K_DOWN] or keys[pygame.K_s]:
            self.direction.y = 1
            self.facing = 'down'
        else:
            self.direction.y = 0

        # Déplacements X
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.direction.x = 1
            self.facing = 'right'
        elif keys[pygame.K_LEFT] or keys[pygame.K_q]:
            self.direction.x = -1
            self.facing = 'left'
        else:
            self.direction.x = 0

        # Touche d'action (Interaction PNJ)
        if keys[pygame.K_RETURN]:
            self.check_npc()

        # Touche d'attaque (Espace) - Seulement si on a l'Opinel !
        if keys[pygame.K_SPACE] and self.inventory["opinel"]:
            self.is_attacking = True
            self.attack_time = pygame.time.get_ticks()
            self.direction.x = 0
            self.direction.y = 0
            if self.create_attack:
                self.create_attack() # On génère la hitbox de l'arme

    def check_npc(self):
        if self.interaction_sprites:
            check_rect = self.hitbox.inflate(20, 20)
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

        self.hitbox.x += self.direction.x * speed
        self.collision('horizontal')
        self.hitbox.y += self.direction.y * speed
        self.collision('vertical')
        self.rect.center = self.hitbox.center

    def collision(self, direction):
        if direction == 'horizontal':
            for sprite in self.obstacle_sprites:
                if sprite.hitbox.colliderect(self.hitbox):
                    if self.direction.x > 0: self.hitbox.right = sprite.hitbox.left
                    if self.direction.x < 0: self.hitbox.left = sprite.hitbox.right
        if direction == 'vertical':
            for sprite in self.obstacle_sprites:
                if sprite.hitbox.colliderect(self.hitbox):
                    if self.direction.y > 0: self.hitbox.bottom = sprite.hitbox.top
                    if self.direction.y < 0: self.hitbox.top = sprite.hitbox.bottom

    def update(self):
        self.input()
        self.cooldowns()
        self.move(self.speed)
