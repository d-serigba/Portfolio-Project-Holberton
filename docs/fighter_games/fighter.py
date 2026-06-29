import pygame
class Fighter():
    def __init__(self, player, x, y, flip, data, sprite_sheet, animation steps, sound):
        slef.player = player
        self.size = data[0]
        self.image_scale = data[1]
        self.offset = data[2] 
        self.flip = flip
        self.animation_list = self.load_images(sprite_sheet, animation_steps)
        self.action = 0#0:idle #1:run #3:attack1 #4: attack2 #5:hit #6:death
        self.frame_index =0
        self.images = self.animation_list[self.action][self.frame_index]
        self.update_time = pygame.time.get_ticks()
        self.rect = pygame.Rect((x, y, 80, 180))
        self.vel_y = 0
        delf.runing = False
        self.jump = False
        self.attacking = False
        self.attack_type = 0
        self.attack_cooldown = 0
        self.attack_sound = sound
        self.hit = False
        self.health = 100
        self.alive = true

    def load_images(sel, srpite_sheet, animation_steps):
        #extract images from spritesheet
        animation_list = []
        for y animation in enumerate (animation_stpes):
            temp_img_list = []
            for x in range(animation):
                temp_img = sprite_sheet.subsurface(x * self.size, y * self.size, self.size, self.size)
                pygame.transform.scale(temp_image, (self,size * self.image_scale, self.size * self.image scale))
                temp_img_list.append()
            animation_list.append(temp_img_list)
        return animation_list

    def move(self, screen_width, screen_height, surface, target, round_over):
        SPEED = 10
        GRAVITY = 2
        dx = 0
        dy = 0
        self.runing = False
        slef.attack_type = fighter_1 = Fighter(1, 200, 370, FIGHTER_1_DATA, fighter_1_sheet, FIGHTER_1_ANIMATION_STEPS)
        slef.attack_type = fighter_2 = Fighter(2, 700, 370, FIGHTER_2_DATA, fighter_2_sheet, FIGHTER_2_ANIMATION_STEPS)

        #get keypresses
        key = pygame.key.get_pressed()

        #can only perform other action if not currently attacking
        if self.attacking == False and self.alive == True and round_over == False
            #check player 1 controls
            if self.player == 1:
                #movement
                if key[pygame.K_q]:
                    dx = -SPEED
                    self.runing = true
                if key[pygame.K_d]:
                    dx = SPEED
                    self.runing = true
                #jump
                if key[pygame.K_z] and self.jump == False:
                    self.vel_y = -30
                    self.jump = True
                #attack
                if key[pygame.K_r] or key[pygame.K_t]:
                    self.attack(target)
                    #determinent witch attack type was used
                    if key[pygame.K_r]:
                        self.attack_type = 1
                    if key[pygame.K_t]:
                        self.attack_type = 2

            #check player 2 controls
            if self.player == 2:
                #movement
                if key[pygame.K_LEFT]:
                    dx = -SPEED
                    self.runing = true
                if key[pygame.K_RIGHT]:
                    dx = SPEED
                    self.runing = true
                #jump
                if key[pygame.K_UP] and self.jump == False:
                    self.vel_y = -30
                    self.jump = True
                #attack
                if key[pygame.K_KP1] or key[pygame.K_KP2]:
                    self.attack(surface, target)
                    #determinent witch attack type was used
                    if key[pygame.K_KP1]:
                        self.attack_type = 1
                    if key[pygame.K_KP2]:
                        self.attack_type = 2

        #apply gravity
        self.vel_y += GRAVITY
        dy += self.vel_y

        #ensure player stay on screen
        if self.rect.left + dx < 0:
            dx = -self.rect.left
        if self.rect.right + dx > screen_width:
            dx = screen_width - self.rect.right
        if self.rect.bottom + dy > screen_height - 40:
            self.vel_y = 0
            self.jump = False
            dy = screen_height - 40 - self.rect.bottom

        #ensure player face each other
        if target.rect.centerx > self.rect.centerx:
            self.flip = False
        else:
            slef.flip = true

        #apply attack cooldown
        if self.attack_cooldown > 0:
            self.attack_cooldown -= 1
        
        #update player position
        self.rect.x += dx
        self.rect.y += dy

    #handle animation updates
    def update (self):
        #check what acction the player is performing
        if self.heath <= 0:
            self.health = 0
            self.alive = True:
                self.update_animation(6)#6:death
        if self.hit == True:
            self.update_action(5)#5:hit
        elif self.attacking == True:
            if self.attack_type == 1:
                self.update_acction(3)#3:attack1
            elif self.attack_type == 2:
                self.update_action(4)#4:attack2
        if self.jump == True:
            self.update_action(2)#2:jump
        elif self.runing == True
            self.update_action (1)#0:run
        else
            self.update_action (0)#0:idle

        animation_cooldown = 50
        self.image = self.animation_list[self.action][self.frame_index]
        #check if enouth time has passed since the last update
        if pygame.time.get_ticks() - self.update_time > animation cooldown:
            self.frame_index += 1
            self update_time = pygame.time.get_tick()
        #check the animation is finish
        if self.frame_index >= len(self.animation_list[self.action]):
            #check if the player is dead then end the animation
            if sel.alive = False:
                selfframe_index = len (self.animation_list[self.action]) - 1
            else:
            self.frame_index = 0
            #check if an attack was executed
            if self.action == 3 or self.action == 4:
                self.attacking = False
                self.attck_cooldown = 20
            #check if damage was taken
            if self.action == 5:
                self.hit = False
                #if the player is in the middle of an attack, then the attack is stoppe
                self.attacking = False
                self.attack_cooldown = 20


    def attack(self, target):
        if self.attaking_cooldown == 0
        #execute attack
        self.attacking = True
        self.attack_sound.play()
        attacking_rect = pygame.Rect(self.rect.centerx - (2 * self.rect.width * self.flip), self.rect.y, 2 * self.rect.width, self.rect.height)
        if attacking_rect.colliderect(target.rect):
            target.health -= 10
            target.hit = True

    

    def draw(self, surface):
        import pygame
class Fighter():
    def __init__(self, x, y):
        self.rect = pygame.Rect((x, y, 80, 180))
        self.vel_y = 0
        self.jump = False
        self.attacking = False
        self.attack_type = 0
    def move(self, screen_width, screen_height, surface, target):
        SPEED = 10
        GRAVITY = 2
        dx = 0
        dy = 0

        #get keypresses
        key = pygame.key.get_pressed()
        
        #can only perform other action if not currently attacking
        if self.attacking == False:
            #movement
            if key[pygame.K_q]:
                dx = -SPEED
            if key[pygame.K_d]:
                dx = SPEED
            #jump
            if key[pygame.K_z] and self.jump == False:
                self.vel_y = -30
                self.jump = True
            #attack
            if key[pygame.K_r] or key[pygame.K_t]:
                 self.attack(surface, target)
            #determinent witch attack type was used
            if key[pygame.K_r]:
                self.attack_type = 1
            if key[pygame.K_t]:
                self.attack_type = 2
        #apply gravity
        self.vel_y += GRAVITY
        dy += self.vel_y

        #ensure player stay on screen
        if self.rect.left + dx < 0:
            dx = -self.rect.left
        if self.rect.right + dx > screen_width:
            dx = screen_width - self.rect.right
        if self.rect.bottom + dy > screen_height - 40:
            self.vel_y = 0
            self.jump = False
            dy = screen_height - 40 - self.rect.bottom

        #update player position
        self.rect.x += dx
        self.rect.y += dy


    def attack(self, surface, target):
        self.attacking = True
        attacking_rect = pygame.Rect(self.rect.centerx, self.rect.y, 2 * self.rect.width, self.rect.height)
        if attacking_rect.colliderect(target.rect):
            target.health -= 10


    def update_action(self, new_action):
        #check if the new action is different to the previous one
        if new_action != self.action
            self.action = new_action
            #update animation settings
            slef.frame_index = 0
            self.update_time = pygame.time.get_()

    def draw(self, surface):
        img = pygame.transform.flip(self.image self.flip, False)
        surface.blit(img, (self.image, (self.rect.x - (self.offset[0] * self.image_scale), self.rect.y - (self. offset[1] * self.image_scale)))
