import pygame

class Enemy(pygame.sprite.Sprite):
    def __init__(self, pos, groups, obstacle_sprites):
        super().__init__(groups)
        self.sprite_type = 'enemy'
        
        # Graphique temporaire (Un carré rouge/orange de mauvaise augure)
        self.image = pygame.Surface((48, 64))
        self.image.fill((200, 50, 50))
        self.rect = self.image.get_rect(topleft=pos)
        self.hitbox = self.rect.inflate(-30, -40)

        # Statistiques
        self.health = 2
        self.speed = 1
        self.obstacle_sprites = obstacle_sprites

        # IA de détection
        self.notice_radius = 250

    def get_player_distance_direction(self, player):
        """Calcule la distance et la direction vers Arnaud"""
        enemy_vec = pygame.math.Vector2(self.rect.center)
        player_vec = pygame.math.Vector2(player.rect.center)
        distance = (player_vec - enemy_vec).magnitude()

        if distance > 0:
            direction = (player_vec - enemy_vec).normalize()
        else:
            direction = pygame.math.Vector2()

        return (distance, direction)

    def actions(self, player):
        """Définit le comportement selon la distance"""
        distance, direction = self.get_player_distance_direction(player)

        if distance <= self.notice_radius:
            # Mode Poursuite !
            self.direction = direction
        else:
            # Immobile si Arnaud est trop loin
            self.direction = pygame.math.Vector2()

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

    def check_death(self):
        if self.health <= 0:
            self.kill() # Disparaît du jeu

    def update_behavior(self, player):
        """Méthode personnalisée appelée par le niveau pour lui injecter les coordonnées du joueur"""
        self.actions(player)

        # Si l'ennemi se fait toucher, on peut appliquer un mini recul ici
        # Pour ce tuto, on va simplement le faire reculer à l'opposé de sa direction
        if hasattr(self, 'direction') and self.direction.magnitude() > 0:
            # Si le joueur attaque et le touche, la logique de niveau baisse sa vie
            # On vérifie sa vie pour la mort
            pass

        self.move(self.speed)
        self.check_death()
