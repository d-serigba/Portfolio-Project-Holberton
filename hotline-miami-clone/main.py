import pygame
from settings import *
from player import Player
from level import Level
from camera import Camera

class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        self.clock = pygame.time.Clock()
        self.running = True
        self.current_level = 1
        self.level = Level(self.current_level)
        self.player = Player(*self.level.player_start)
        self.bullets = pygame.sprite.Group()
        self.camera = Camera(WIDTH, HEIGHT)

    def run(self):
        while self.running:
            dt = self.clock.tick(FPS) / 1000
            self.handle_events()
            self.update()
            self.draw()

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # clic gauche = tir ou coup de poing
                    if self.player.weapon:
                        self.player.shoot(self.bullets)
                    else:
                        self.player.punch(self.level.enemies)
            # Ramassage arme au sol sur touche E
            if event.type == pygame.KEYDOWN and event.key == pygame.K_e:
                for pickup in self.level.pickups:
                    self.player.pickup_weapon(pickup)

    def update(self):
        if not self.player.alive:
            self.reset_level()
            return

        # Mouvement joueur (flèches ou ZQSD)
        keys = pygame.key.get_pressed()
        dx, dy = 0, 0
        if keys[pygame.K_LEFT] or keys[pygame.K_q]: dx -= 1
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]: dx += 1
        if keys[pygame.K_UP] or keys[pygame.K_z]: dy -= 1
        if keys[pygame.K_DOWN] or keys[pygame.K_s]: dy += 1
        self.player.move(dx, dy, self.level.obstacles)

        # Mise à jour ennemis
        for enemy in self.level.enemies:
            if enemy.type == 'boss':
                enemy.update(self.player, self.level.obstacles)
            else:
                enemy.move_towards_player(self.player, self.level.obstacles)
                if enemy.type == 'melee':
                    enemy.melee_attack(self.player)
                elif enemy.type == 'ranged':
                    enemy.shoot_at_player(self.player, self.bullets)
            # Si l'ennemi est mort (ex: touché par balle ou poing)
            if enemy.health <= 0:
                enemy.drop_weapon()  # possible
                enemy.kill()

        # Mise à jour projectiles
        for bullet in self.bullets:
            bullet.update()
            # Collision avec obstacles
            if pygame.sprite.spritecollide(bullet, self.level.obstacles, False):
                bullet.kill()
            # Collision avec ennemis (si tir du joueur)
            if bullet.owner == 'player':
                hits = pygame.sprite.spritecollide(bullet, self.level.enemies, False)
                for e in hits:
                    e.health -= 1
                    bullet.kill()
            # Collision avec joueur (si tir ennemi)
            elif bullet.owner == 'enemy' and bullet.rect.colliderect(self.player.rect):
                self.player.alive = False
                bullet.kill()

        # Vérifier escalier
        if self.player.rect.colliderect(self.level.exit_rect):
            self.next_level()

        self.camera.update(self.player)

    def next_level(self):
        self.current_level += 1
        if self.current_level > 4:
            self.show_victory()
        else:
            self.level = Level(self.current_level)
            self.player = Player(*self.level.player_start)
            self.bullets.empty()

    def reset_level(self):
        # Recommencer le niveau actuel
        self.level = Level(self.current_level)
        self.player = Player(*self.level.player_start)
        self.bullets.empty()

    def draw(self):
        self.screen.fill(BLACK)
        # Appliquer caméra
        for sprite in self.level.obstacles:
            self.screen.blit(sprite.image, self.camera.apply(sprite))
        # ...
        pygame.display.flip()
