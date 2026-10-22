import pygame
import sys

# --- CONFIGURATION INITIALE ---
WIDTH, HEIGHT = 800, 600
FPS = 60
TILE_SIZE = 64  # Taille d'un bloc (64x64 pixels)

# Couleurs (Temporaires, en attendant tes propres assets)
BG_COLOR = (34, 139, 34)    # Vert forêt
PLAYER_COLOR = (255, 0, 0)  # Rouge
WALL_COLOR = (139, 69, 19)   # Marron terre

# --- LA CAMÉRA (Le secret du défilement) ---
class CameraGroup(pygame.sprite.Group):
    """ Un groupe de sprites personnalisé qui se comporte comme une caméra de suivi. """
    def __init__(self):
        super().__init__()
        self.display_surface = pygame.display.get_surface()
        self.offset = pygame.math.Vector2()

    def custom_draw(self, player):
        # On calcule le décalage pour centrer le joueur à l'écran
        self.offset.x = player.rect.centerx - WIDTH // 2
        self.offset.y = player.rect.centery - HEIGHT // 2

        # On dessine tous les sprites triés par leur axe Y (effet de profondeur Y-Sort)
        for sprite in sorted(self.sprites(), key=lambda sprite: sprite.rect.bottom):
            # On applique le décalage de la caméra à la position réelle du sprite
            offset_pos = sprite.rect.topleft - self.offset
            self.display_surface.blit(sprite.image, offset_pos)

# --- LES ENTITÉS ---
class Tile(pygame.sprite.Sprite):
    """ Les blocs de décor (murs, arbres) qui bloquent le passage. """
    def __init__(self, pos, groups):
        super().__init__(groups)
        self.image = pygame.Surface((TILE_SIZE, TILE_SIZE))
        self.image.fill(WALL_COLOR)
        self.rect = self.image.get_rect(topleft=pos)
        self.hitbox = self.rect.inflate(0, -10) # Hitbox légèrement plus petite pour le réalisme

class Player(pygame.sprite.Sprite):
    """ Le héros du jeu. """
    def __init__(self, pos, groups, obstacle_sprites):
        super().__init__(groups)
        self.image = pygame.Surface((TILE_SIZE, TILE_SIZE))
        self.image.fill(PLAYER_COLOR)
        self.rect = self.image.get_rect(topleft=pos)
        self.hitbox = self.rect.inflate(0, -15) # Permet de passer un peu derrière les objets

        # Déplacements
        self.direction = pygame.math.Vector2()
        self.speed = 5
        self.obstacle_sprites = obstacle_sprites

    def input(self):
        keys = pygame.key.get_pressed()

        # Détection des axes ZQSD / Flèches
        if keys[pygame.K_UP] or keys[pygame.K_z]:
            self.direction.y = -1
        elif keys[pygame.K_DOWN] or keys[pygame.K_s]:
            self.direction.y = 1
        else:
            self.direction.y = 0

        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.direction.x = 1
        elif keys[pygame.K_LEFT] or keys[pygame.K_q]:
            self.direction.x = -1
        else:
            self.direction.x = 0

        # Normalisation du vecteur pour éviter d'aller plus vite en diagonale (Théorème de Pythagore)
        if self.direction.magnitude() > 0:
            self.direction = self.direction.normalize()

    def move(self, speed):
        # Gestion des collisions Horizontales
        self.hitbox.x += self.direction.x * speed
        self.collision('horizontal')
        
        # Gestion des collisions Verticales
        self.hitbox.y += self.direction.y * speed
        self.collision('vertical')
        
        # Le rect principal suit la hitbox
        self.rect.center = self.hitbox.center

    def collision(self, direction):
        if direction == 'horizontal':
            for sprite in self.obstacle_sprites:
                if sprite.hitbox.colliderect(self.hitbox):
                    if self.direction.x > 0: # Déplacement à droite
                        self.hitbox.right = sprite.hitbox.left
                    if self.direction.x < 0: # Déplacement à gauche
                        self.hitbox.left = sprite.hitbox.right

        if direction == 'vertical':
            for sprite in self.obstacle_sprites:
                if sprite.hitbox.colliderect(self.hitbox):
                    if self.direction.y > 0: # Déplacement vers le bas
                        self.hitbox.bottom = sprite.hitbox.top
                    if self.direction.y < 0: # Déplacement vers le haut
                        self.hitbox.top = sprite.hitbox.bottom

    def update(self):
        self.input()
        self.move(self.speed)

# --- LE CŒUR DU JEU ---
class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Zelda-Like Engine Core")
        self.clock = pygame.time.Clock()

        # Groupes de Sprites
        self.visible_sprites = CameraGroup()
        self.obstacle_sprites = pygame.sprite.Group()

        self.create_map()

    def create_map(self):
        # Une fausse carte matricielle (X = Mur, P = Joueur)
        # Tu pourras remplacer ça par un chargement de fichier TMX (Tiled) plus tard
        WORLD_MAP = [
            ['X','X','X','X','X','X','X','X','X','X','X','X','X','X','X'],
            ['X',' ',' ',' ',' ','X',' ',' ',' ',' ',' ',' ',' ',' ','X'],
            ['X',' ','P',' ',' ','X',' ','X','X','X',' ','X',' ',' ','X'],
            ['X',' ',' ',' ',' ',' ',' ','X',' ','X',' ','X',' ',' ','X'],
            ['X',' ',' ','X','X','X',' ','X',' ','X',' ','X',' ',' ','X'],
            ['X',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ','X',' ',' ','X'],
            ['X','X','X','X','X','X','X','X','X','X','X','X','X','X','X'],
        ]

        for row_index, row in enumerate(WORLD_MAP):
            for col_index, col in enumerate(row):
                x = col_index * TILE_SIZE
                y = row_index * TILE_SIZE
                if col == 'X':
                    Tile((x, y), [self.visible_sprites, self.obstacle_sprites])
                if col == 'P':
                    self.player = Player((x, y), self.visible_sprites, self.obstacle_sprites)

    def run(self):
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

            self.screen.fill(BG_COLOR)
            
            # Mise à jour et dessin via la caméra
            self.visible_sprites.update()
            self.visible_sprites.custom_draw(self.player)
            
            pygame.display.update()
            self.clock.tick(FPS)

if __name__ == '__main__':
    game = Game()
    game.run()
