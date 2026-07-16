import pygame

class MetroBoss(pygame.sprite.Sprite):
    def __init__(self, pos, groups, obstacle_sprites, trigger_reward_callback):
        super().__init__(groups)
        self.sprite_type = 'enemy'
        self.image = pygame.Surface((96, 96))
        self.image.fill((139, 0, 0)) # Rouge foncé imposant
        self.rect = self.image.get_rect(topleft=pos)
        self.hitbox = self.rect.inflate(-15, -15)

        # Statistiques du Boss
        self.health = 10
        self.speed = 1
        self.obstacle_sprites = obstacle_sprites
        self.trigger_reward_callback = trigger_reward_callback

        # États du Boss : 'chase' (poursuite), 'charging' (préparation), 'dash' (charge)
        self.status = 'chase'
        self.state_timer = pygame.time.get_ticks()
        self.direction = pygame.math.Vector2()

    def update_behavior(self, player):
        current_time = pygame.time.get_ticks()

        # Calcul de la position du joueur
        boss_vec = pygame.math.Vector2(self.rect.center)
        player_vec = pygame.math.Vector2(player.rect.center)
        distance = (player_vec - boss_vec).magnitude()
        
        if self.status == 'chase':
            # 🟢 NOUVEAU : Le Rayon de Vision (Aggro Radius)
            if distance > 500:
                self.speed = 0 # Il reste immobile
                # Optionnel : Tu peux le rendre plus sombre quand il est inactif
                # self.image.fill((80, 0, 0)) 
                return # On arrête le code ici, il ne chasse pas et ne charge pas
                
            # S'il est assez près, le combat commence vraiment :
            self.speed = 2
            self.image.fill((139, 0, 0)) # Couleur normale
            if distance > 0:
                self.direction = (player_vec - boss_vec).normalize()
            
            # (Garde le reste de ton code pour la charge en dessous...)
            # Toutes les 4 secondes, il prépare une charge
            if current_time - self.state_timer > 4000:
                self.status = 'charging'
                self.state_timer = current_time
                self.direction = pygame.math.Vector2() # Il s'arrête pour viser

        elif self.status == 'charging':
            self.image.fill((255, 140, 0)) # Clignote en orange : Attention !
            if current_time - self.state_timer > 1000: # Charge après 1 seconde
                self.status = 'dash'
                self.state_timer = current_time
                # Il fixe sa cible finale
                if (player_vec - boss_vec).magnitude() > 0:
                    self.direction = (player_vec - boss_vec).normalize()

        elif self.status == 'dash':
            self.speed = 8 # Vitesse fulgurante !
            self.image.fill((255, 0, 0)) # Rouge vif furieux
            if current_time - self.state_timer > 800: # Le dash dure 0.8 seconde
                self.status = 'chase'
                self.state_timer = current_time

        self.move(self.speed)
        self.check_death()

    def move(self, speed):
        self.hitbox.x += self.direction.x * speed
        self.collision('horizontal')
        self.hitbox.y += self.direction.y * speed
        self.collision('vertical')
        self.rect.center = self.hitbox.center

    def collision(self, direction):
        for sprite in self.obstacle_sprites:
            if sprite.hitbox.colliderect(self.hitbox):
                if direction == 'horizontal':
                    if self.direction.x > 0: self.hitbox.right = sprite.hitbox.left
                    if self.direction.x < 0: self.hitbox.left = sprite.hitbox.right
                    if self.status == 'dash': self.status = 'chase' # Assommé par le mur
                if direction == 'vertical':
                    if self.direction.y > 0: self.hitbox.bottom = sprite.hitbox.top
                    if self.direction.y < 0: self.hitbox.top = sprite.hitbox.bottom
                    if self.status == 'dash': self.status = 'chase'

    def check_death(self):
        if self.health <= 0:
            if self.trigger_reward_callback:
                self.trigger_reward_callback(self.rect.center) # Fait apparaître la récompense à sa mort
            self.kill()

class GardienDeLaVoiture(pygame.sprite.Sprite):
    def __init__(self, pos, groups, obstacle_sprites, trigger_reward_callback, ui):
        super().__init__(groups)
        self.sprite_type = 'enemy'
        self.image = pygame.Surface((64, 64))
        self.image.fill((128, 0, 128)) # Violet (style mafieux)
        self.rect = self.image.get_rect(topleft=pos)
        self.hitbox = self.rect.inflate(-10, -10)

        # Statistiques
        self.health = 8
        self.speed = 0 # Immobile au début !
        self.obstacle_sprites = obstacle_sprites
        self.trigger_reward_callback = trigger_reward_callback
        self.ui = ui

        # États : 'dialogue' -> 'chase'
        self.status = 'dialogue'
        self.dialogue_triggered = False
        self.direction = pygame.math.Vector2()

    def update_behavior(self, player):
        boss_vec = pygame.math.Vector2(self.rect.center)
        player_vec = pygame.math.Vector2(player.rect.center)
        distance = (player_vec - boss_vec).magnitude()

        if self.status == 'dialogue':
            # Si Arnaud s'approche à moins de 200 pixels
            if distance < 200 and not self.dialogue_triggered:
                self.ui.show_message("Sbire: Si tu veux cette voiture tu vas devoir me vaincre !")
                self.dialogue_triggered = True
                self.status = 'chase' # Le combat commence !
                self.speed = 3
        elif self.status == 'chase':
            if distance > 0:
                self.direction = (player_vec - boss_vec).normalize()
        
        self.move(self.speed)
        self.check_death()

    def move(self, speed):
        self.hitbox.x += self.direction.x * speed
        self.collision('horizontal')
        self.hitbox.y += self.direction.y * speed
        self.collision('vertical')
        self.rect.center = self.hitbox.center

    def collision(self, direction):
        for sprite in self.obstacle_sprites:
            if sprite.hitbox.colliderect(self.hitbox):
                if direction == 'horizontal':
                    if self.direction.x > 0: self.hitbox.right = sprite.hitbox.left
                    if self.direction.x < 0: self.hitbox.left = sprite.hitbox.right
                if direction == 'vertical':
                    if self.direction.y > 0: self.hitbox.bottom = sprite.hitbox.top
                    if self.direction.y < 0: self.hitbox.top = sprite.hitbox.bottom

    def check_death(self):
        if self.health <= 0:
            if self.trigger_reward_callback:
                self.trigger_reward_callback(self.rect.center) # Fait tomber les clés
            self.kill()
