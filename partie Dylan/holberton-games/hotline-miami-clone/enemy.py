import pygame
from constants import ENEMY_SPEED, ENEMY_FIST_RANGE
from constants import WIDTH, HEIGHT

class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y, enemy_type, weapon=None):
        super().__init__()
        # Charger une image pour l'ennemi
        self.image = pygame.Surface((32, 32))  # Surface temporaire (à remplacer par une vraie image)
        self.image.fill((255, 0, 0))  # Remplir en rouge pour visualiser
        self.rect = self.image.get_rect(center=(x, y))
        self.speed = ENEMY_SPEED = 2
        ENEMY_FIST_RANGE = 50
        self.type = enemy_type  # 'melee', 'ranged', 'boss'
        self.pos = pygame.Vector2(x, y)
        self.weapon = weapon  # pour les ennemis armés
        self.health = 1       # meurent en un coup (sauf boss)

    def move_towards_player(self, player, obstacles):
        direction = player.pos - self.pos
        if direction.length() > 0:
            direction.normalize_ip()

        # Essaie de bouger horizontalement puis verticalement
        new_x = self.pos.x + direction.x * self.speed
        temp_rect = self.rect.copy()
        temp_rect.centerx = new_x
        if not any(temp_rect.colliderect(obs.rect) for obs in obstacles):
            self.pos.x = new_x
        else:  # glissement si bloqué
            new_y = self.pos.y + direction.y * self.speed
            temp_rect = self.rect.copy()
            temp_rect.centery = new_y
            if not any(temp_rect.colliderect(obs.rect) for obs in obstacles):
                self.pos.y = new_y

        new_y = self.pos.y + direction.y * self.speed
        temp_rect = self.rect.copy()
        temp_rect.centery = new_y
        if not any(temp_rect.colliderect(obs.rect) for obs in obstacles):
            self.pos.y = new_y

        self.rect.center = self.pos

    def melee_attack(self, player):
        if self.pos.distance_to(player.pos) < ENEMY_FIST_RANGE:
            player.alive = False  # mort instantanée

    def shoot_at_player(self, player, bullets_group):
        if self.weapon and self.weapon.can_fire():
            self.weapon.fire(self.pos, player.pos, bullets_group)

class Boss(Enemy):
    def __init__(self, x, y):
        super().__init__(x, y, 'boss')
        self.health = BOSS_HEALTH
        self.charge_cooldown = 0
        self.state = 'idle'  # idle, charging

    def update(self, player, obstacles, bullets_group=None):
        if self.health <= 0:
            self.kill()
            return

        if self.charge_cooldown > 0:
            self.charge_cooldown -= 1

        distance = self.pos.distance_to(player.pos)

        if self.state == 'idle':
            if distance < 200 and self.charge_cooldown == 0:
                self.state = 'charging'
                self.direction = (player.pos - self.pos).normalize()
                self.charge_cooldown = 120  # 2 sec à 60 fps
            else:
                self.move_towards_player(player, obstacles)
                if distance < ENEMY_FIST_RANGE * 2:
                    player.alive = False  # coup mortel

        elif self.state == 'charging':
            self.pos += self.direction * BOSS_CHARGE_SPEED
            self.rect.center = self.pos
            # Si le boss heurte un mur, il s'arrête et repasse en idle
            if any(self.rect.colliderect(obs.rect) for obs in obstacles):
                self.state = 'idle'
                self.charge_cooldown = 90
            # S'il touche le joueur, mort instantanée
            if self.rect.colliderect(player.rect):
                player.alive = False
