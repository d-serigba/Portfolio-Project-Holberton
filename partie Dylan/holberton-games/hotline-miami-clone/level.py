import pygame
from settings import *
from enemy import Enemy, Boss
from weapon import Weapon

class Level:
    def __init__(self, level_number):
        self.number = level_number
        self.obstacles = pygame.sprite.Group()
        self.enemies = pygame.sprite.Group()
        self.pickups = pygame.sprite.Group()
        self.player_start = (0, 0)
        self.exit_rect = None
        self.load_level(level_number)

    def load_level(self, num):
        if num == 1:
            layout = [
                "################",
                "#..............#",
                "#..............#",
                "#..............#",
                "#......P.......#",
                "#..............#",
                "#..............#",
                "#..............#",
                "#......E.......#",
                "#..............#",
                "#..............#",
                "#......E.......#",
                "#..............#",
                "#........X.....#",
                "################"
            ]
        elif num == 2:
            layout = [
                "################",
                "#..............#",
                "#..............#",
                "#...P..........#",
                "#..............#",
                "#......G.......#",  # G = arme au sol
                "#..............#",
                "#......E.......#",  # ennemi mêlée
                "#..............#",
                "#......R.......#",  # ennemi armé
                "#..............#",
                "#........X.....#",
                "################"
            ]
        elif num == 3:
            layout = [
                "################",
                "#..............#",
                "#..............#",
                "#...P..........#",
                "#..............#",
                "#......G.......#",  # pickup arme auto
                "#..............#",
                "#......R.......#",
                "#..............#",
                "#......R.......#",
                "#........X.....#",
                "################"
            ]
        elif num == 4:
            layout = [
                "################",
                "#..............#",
                "#..............#",
                "#......B.......#",  # B = boss
                "#..............#",
                "#..............#",
                "#......P.......#",
                "#..............#",
                "#..............#",
                "################"
            ]
        else:
            raise ValueError("Niveau inconnu")

        self.parse_layout(layout)

    def parse_layout(self, layout):
        for row_idx, row in enumerate(layout):
            for col_idx, char in enumerate(row):
                x = col_idx * TILE_SIZE
                y = row_idx * TILE_SIZE
                if char == '#':
                    wall = Wall(x, y)
                    self.obstacles.add(wall)
                elif char == 'P':
                    self.player_start = (x + TILE_SIZE // 2, y + TILE_SIZE // 2)
                elif char == 'E':
                    enemy = Enemy(x + TILE_SIZE // 2, y + TILE_SIZE // 2, 'melee')
                    self.enemies.add(enemy)
                elif char == 'R':
                    # ennemi armé avec une arme semi-auto ou auto selon le niveau
                    if self.number == 2:
                        weapon = Weapon('semi', 6, 500)  # 500 ms entre tirs
                    else:
                        weapon = Weapon('auto', 20, 200)
                    enemy = Enemy(x + TILE_SIZE // 2, y + TILE_SIZE // 2, 'ranged', weapon)
                    self.enemies.add(enemy)
                elif char == 'G':
                    # Pickup d’arme au sol
                    if self.number == 2:
                        weapon = Weapon('semi', 10, 500, (x + TILE_SIZE // 2, y + TILE_SIZE // 2))
                    else:
                        weapon = Weapon('auto', 30, 200, (x + TILE_SIZE // 2, y + TILE_SIZE // 2))
                    self.pickups.add(weapon)  # à adapter : un sprite contenant l'arme ?
                elif char == 'B':
                    boss = Boss(x + TILE_SIZE // 2, y + TILE_SIZE // 2)
                    self.enemies.add(boss)
                elif char == 'X':
                    self.exit_rect = pygame.Rect(x, y, TILE_SIZE, TILE_SIZE)


class Wall(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((TILE_SIZE, TILE_SIZE))
        self.image.fill(BLUE)
        self.rect = self.image.get_rect(topleft=(x, y))
