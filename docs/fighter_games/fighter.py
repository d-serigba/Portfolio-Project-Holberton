import pygame

class Fighter():
    def __init__(self, player, x, y, flip, data, sprite_sheet, animation_steps, sound):
        self.player = player
        self.size = data[0]
        self.image_scale = data[1]
        self.offset = data[2]
        self.flip = flip
        self.animation_list = self.load_images(sprite_sheet, animation_steps)
        self.action = 0  # 0:idle, 1:run, 2:jump, 3:attack1, 4:attack2, 5:hit, 6:death
        self.frame_index = 0
        self.image = self.animation_list[self.action][self.frame_index]
        self.update_time = pygame.time.get_ticks()
        self.rect = pygame.Rect((x, y, 80, 180))
        self.vel_y = 0
        self.running = False
        self.jump = False
        self.attacking = False
        self.attack_type = 0
        self.attack_cooldown = 0
        self.attack_sound = sound
        self.hit = False
        self.health = 100
        self.alive = True

    def load_images(self, sprite_sheet, animation_steps):
        # extraire les images de la spritesheet
        animation_list = []
        for y, animation in enumerate(animation_steps):
            temp_img_list = []
            for x in range(animation):
                temp_img = sprite_sheet.subsurface(x * self.size, y * self.size, self.size, self.size)
                scaled_img = pygame.transform.scale(temp_img, (self.size * self.image_scale, self.size * self.image_scale))
                temp_img_list.append(scaled_img)
            animation_list.append(temp_img_list)
        return animation_list

    def move(self, screen_width, screen_height, surface, target, round_over):
        SPEED = 10
        GRAVITY = 2
        dx = 0
        dy = 0
        self.running = False
        self.attack_type = 0

        # récupérer les touches
        key = pygame.key.get_pressed()

        # actions possibles seulement si vivant et pas en train d'attaquer
        if self.attacking == False and self.alive == True and round_over == False:
            # joueur 1 (AZERTY adapté : Q=gauche, D=droite, Z=saut)
            if self.player == 1:
                if key[pygame.K_q]:
                    dx = -SPEED
                    self.running = True
                if key[pygame.K_d]:
                    dx = SPEED
                    self.running = True
                if key[pygame.K_z] and self.jump == False:
                    self.vel_y = -30
                    self.jump = True
                if key[pygame.K_r] or key[pygame.K_t]:
                    self.attack(target)
                    if key[pygame.K_r]:
                        self.attack_type = 1
                    if key[pygame.K_t]:
                        self.attack_type = 2

            # joueur 2
            if self.player == 2:
                if key[pygame.K_LEFT]:
                    dx = -SPEED
                    self.running = True
                if key[pygame.K_RIGHT]:
                    dx = SPEED
                    self.running = True
                if key[pygame.K_UP] and self.jump == False:
                    self.vel_y = -30
                    self.jump = True
                if key[pygame.K_KP1] or key[pygame.K_KP2]:
                    self.attack(target)
                    if key[pygame.K_KP1]:
                        self.attack_type = 1
                    if key[pygame.K_KP2]:
                        self.attack_type = 2

        # gravité
        self.vel_y += GRAVITY
        dy += self.vel_y

        # limites de l'écran
        if self.rect.left + dx < 0:
            dx = -self.rect.left
        if self.rect.right + dx > screen_width:
            dx = screen_width - self.rect.right
        if self.rect.bottom + dy > screen_height - 40:
            self.vel_y = 0
            self.jump = False
            dy = screen_height - 40 - self.rect.bottom

        # orienter les joueurs l'un vers l'autre
        if target.rect.centerx > self.rect.centerx:
            self.flip = False
        else:
            self.flip = True

        # cooldown d'attaque
        if self.attack_cooldown > 0:
            self.attack_cooldown -= 1

        # mise à jour des positions
        self.rect.x += dx
        self.rect.y += dy

    def update(self):
        # déterminer l'action actuelle
        if self.health <= 0:
            self.health = 0
            self.alive = False
            self.update_action(6) # 6: death
        elif self.hit == True:
            self.update_action(5) # 5: hit
        elif self.attacking == True:
            if self.attack_type == 1:
                self.update_action(3) # 3: attack1
            elif self.attack_type == 2:
                self.update_action(4) # 4: attack2
        elif self.jump == True:
            self.update_action(2) # 2: jump
        elif self.running == True:
            self.update_action(1) # 1: run
        else:
            self.update_action(0) # 0: idle

        animation_cooldown = 50
        # s'assurer qu'on ne sorte pas de la liste
        if self.action < len(self.animation_list) and self.frame_index < len(self.animation_list[self.action]):
            self.image = self.animation_list[self.action][self.frame_index]
        
        # gestion du timer de frame
        if pygame.time.get_ticks() - self.update_time > animation_cooldown:
            self.frame_index += 1
            self.update_time = pygame.time.get_ticks()

        # boucle ou fin d'animation
        if self.frame_index >= len(self.animation_list[self.action]):
            if self.alive == False:
                self.frame_index = len(self.animation_list[self.action]) - 1
            else:
                self.frame_index = 0
                if self.action == 3 or self.action == 4:
                    self.attacking = False
                    self.attack_cooldown = 20
                if self.action == 5:
                    self.hit = False
                    self.attacking = False
                    self.attack_cooldown = 20

    def attack(self, target):
        if self.attack_cooldown == 0:
            self.attacking = True
            self.attack_sound.play()
            
            # Ajustement de la hitbox selon l'orientation
            if self.flip == False:
                attacking_rect = pygame.Rect(self.rect.right, self.rect.y, 2 * self.rect.width, self.rect.height)
            else:
                attacking_rect = pygame.Rect(self.rect.left - (2 * self.rect.width), self.rect.y, 2 * self.rect.width, self.rect.height)
                
            if attacking_rect.colliderect(target.rect):
                target.health -= 10
                target.hit = True

    def update_action(self, new_action):
        if new_action != self.action:
            self.action = new_action
            self.frame_index = 0
            self.update_time = pygame.time.get_ticks()

    def draw(self, surface):
        img = pygame.transform.flip(self.image, self.flip, False)
        surface.blit(img, (self.rect.x - (self.offset[0] * self.image_scale), self.rect.y - (self.offset[1] * self.image_scale)))

    def move_npc(self, screen_width, screen_height, surface, target, round_over):
        """IA simple — cible le joueur et attaque quand proche."""
        import random
        SPEED = 8
        GRAVITY = 2
        dx = 0
        dy = 0
        self.running = False
        self.attack_type = 0

        if self.attacking == False and self.alive == True and round_over == False:
            # Se déplace vers le joueur
            dist_x = target.rect.centerx - self.rect.centerx
            dist_y = target.rect.centery - self.rect.centery

            # Déplacement horizontal vers J1
            if abs(dist_x) > 100:
                if dist_x > 0:
                    dx = SPEED
                    self.running = True
                else:
                    dx = -SPEED
                    self.running = True

            # Attaque si assez proche
            if abs(dist_x) < 200 and abs(dist_y) < 100:
                self.attack(target)
                self.attack_type = random.choice([1, 2])

            # Saut aléatoire ou pour éviter
            if self.jump == False and random.randint(0, 120) == 0:
                self.vel_y = -30
                self.jump = True

        # Gravité
        self.vel_y += GRAVITY
        dy += self.vel_y

        # Limites écran
        if self.rect.left + dx < 0:
            dx = -self.rect.left
        if self.rect.right + dx > screen_width:
            dx = screen_width - self.rect.right
        if self.rect.bottom + dy > screen_height - 40:
            self.vel_y = 0
            self.jump = False
            dy = screen_height - 40 - self.rect.bottom

        # Orientation vers la cible
        if target.rect.centerx > self.rect.centerx:
            self.flip = False
        else:
            self.flip = True

        if self.attack_cooldown > 0:
            self.attack_cooldown -= 1

        self.rect.x += dx
        self.rect.y += dy
