import pygame
from settings import *
from weapon import Weapon
from bullet import Bullet

class Player(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((TILE_SIZE, TILE_SIZE))
        self.image.fill(GREEN)
        self.rect = self.image.get_rect(center=(x, y))
        self.pos = pygame.Vector2(x, y)
        self.weapon = None  # Pas d'arme au début
        self.punch_cooldown = 0
        self.fist_damage = 1
        self.alive = True

    def move(self, dx, dy, obstacles):
        # Mouvement avec collision
        new_pos = self.pos + pygame.Vector2(dx, dy) * PLAYER_SPEED
        new_rect = self.rect.copy()
        new_rect.center = new_pos
        if not any(new_rect.colliderect(obs.rect) for obs in obstacles):
            self.pos = new_pos
            self.rect.center = self.pos

    def punch(self, enemies):
        if self.punch_cooldown > 0:
            return
        # Crée une hitbox devant le joueur (direction face à la souris)
        mouse = pygame.mouse.get_pos()
        # ... calcul direction
        # Si collision avec un ennemi, il meurt
        # self.punch_cooldown = 10

    def pickup_weapon(self, ground_weapon):
        if self.pos.distance_to(ground_weapon.pos) < PICKUP_DISTANCE:
            self.weapon = ground_weapon
            ground_weapon.kill()  # retire du sol

    def shoot(self, bullets_group):
        if self.weapon and self.weapon.can_fire():
            mouse_pos = pygame.mouse.get_pos()
            self.weapon.fire(self.pos, mouse_pos, bullets_group)

    def update(self):
        if self.punch_cooldown > 0:
            self.punch_cooldown -= 1
        if self.weapon:
            self.weapon.update()
