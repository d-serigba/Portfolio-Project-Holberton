import pygame

class Brother(pygame.sprite.Sprite):
    def __init__(self, pos, groups, obstacle_sprites, name="Brother"):
        super().__init__(groups)
        self.sprite_type = 'enemy'
        self.image = pygame.Surface((64, 64))
        self.image.fill((50, 50, 50)) # Couleur sombre et menaçante
        self.rect = self.image.get_rect(topleft=pos)
        self.hitbox = self.rect.inflate(-10, -10)
        self.spawn_time = pygame.time.get_ticks()
        self.status = 'waiting' # 🟢 NOUVEAU : Ils commencent en mode "attente"

        # Statistiques du boss final
        self.health = 11
        self.speed = 2
        self.obstacle_sprites = obstacle_sprites
        self.name = name

    def update_behavior(self, player):
        current_time = pygame.time.get_ticks()

        # 1. Vérifier d'abord l'état d'attente (timer)
        if self.status == 'waiting':
            if current_time - self.spawn_time > 16000:
                self.status = 'chase'
            else:
                return  # Le boss est figé, on arrête ici

        # 2. Ensuite vérifier si une cinématique bloque le mouvement
        if hasattr(player.ui, 'cinematic_active') and player.ui.cinematic_active:
            self.direction = pygame.math.Vector2()
            return

        # 3. IA de poursuite classique
        boss_vec = pygame.math.Vector2(self.rect.center)
        player_vec = pygame.math.Vector2(player.rect.center)

        if (player_vec - boss_vec).magnitude() > 0:
            self.direction = (player_vec - boss_vec).normalize()
        else:
            self.direction = pygame.math.Vector2()

        self.move(self.speed)
        self.check_death(player.ui)

        # IA de poursuite agressive classique (qui tourne à 100% maintenant !)
        boss_vec = pygame.math.Vector2(self.rect.center)
        player_vec = pygame.math.Vector2(player.rect.center)
        
        if (player_vec - boss_vec).magnitude() > 0:
            self.direction = (player_vec - boss_vec).normalize()
        else:
            self.direction = pygame.math.Vector2()

        # Il bouge uniquement s'il a passé les blocages du dessus !
        self.move(self.speed)
        self.check_death(player.ui)

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

    def check_death(self, ui):
        if self.health <= 0:
            ui.show_message(f"{self.name} à été vaincu !")
            self.kill()
