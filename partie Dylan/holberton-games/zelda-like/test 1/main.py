#test

import pygame
import sys

pygame.init()
SCREEN_WIDTH, SCREEN_HEIGHT = 640, 480
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
clock = pygame.time.Clock()

TILE_SIZE = 40
WORLD_MAP = [
    ["W","W","W","W","W","W","W","W","W","W","W","W","W","W","W","W"],
    ["W",".",".",".","W",".",".",".",".",".",".",".",".",".",".","W"],
    ["W",".","W",".","W",".","W","W","W","W",".","W","W","W",".","W"],
    ["W",".","W",".",".",".","W",".",".","W",".","W",".",".",".","W"],
    ["W",".","W","W","W",".","W",".",".","W",".","W",".","W","W","W"],
    ["W",".",".",".","W",".",".",".",".",".",".","W",".",".",".","W"],
    ["W","W",".",".","W","W","W","W",".","W","W","W","W","W",".","W"],
    ["W",".",".",".",".",".",".",".",".",".",".",".",".",".",".","W"],
    ["W","W","W","W","W","W","W","W","W","W","W","W","W","W","W","W"],
]

class Player(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((32, 32))
        self.image.fill((0, 220, 100))
        self.rect = self.image.get_rect(topleft=(x, y))
        self.speed = 4

    def move(self, walls):
        keys = pygame.key.get_pressed()
        dx, dy = 0, 0
        if keys[pygame.K_LEFT]:  dx = -self.speed
        if keys[pygame.K_RIGHT]: dx = self.speed
        if keys[pygame.K_UP]:    dy = -self.speed
        if keys[pygame.K_DOWN]:  dy = self.speed

        self.rect.x += dx
        for wall in walls:
            if self.rect.colliderect(wall.rect):
                if dx > 0: self.rect.right = wall.rect.left
                if dx < 0: self.rect.left = wall.rect.right

        self.rect.y += dy
        for wall in walls:
            if self.rect.colliderect(wall.rect):
                if dy > 0: self.rect.bottom = wall.rect.top
                if dy < 0: self.rect.top = wall.rect.bottom

class Wall(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((TILE_SIZE, TILE_SIZE))
        self.image.fill((130, 70, 30))
        self.rect = self.image.get_rect(topleft=(x, y))

# --- INITIALISATION DES GROUPES ---
all_sprites = pygame.sprite.Group()
walls = pygame.sprite.Group()

# Traduction de la matrice de texte en vrais objets 2D
for row_idx, row in enumerate(WORLD_MAP):
    for col_idx, tile in enumerate(row):
        x = col_idx * TILE_SIZE
        y = row_idx * TILE_SIZE
        if tile == "W":
            wall = Wall(x, y)
            walls.add(wall)
            all_sprites.add(wall)

player = Player(60, 60)
all_sprites.add(player)

# --- BOUCLE PRINCIPALE ---
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Logique
    player.move(walls)

    # Rendu
    screen.fill((30, 30, 30))
    all_sprites.draw(screen)
    
    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()
