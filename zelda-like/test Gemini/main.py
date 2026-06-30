import pygame
import sys
from level import Level

class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((960, 448))
        pygame.display.set_caption("Arnaud's Bizarre Adventure")
        self.clock = pygame.time.Clock()
        self.level = Level()

    def run(self):
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

            self.screen.fill((20, 20, 25)) # Fond sombre pour l'ambiance open space de nuit
            self.level.run()
            pygame.display.update()
            self.clock.tick(60)

if __name__ == '__main__':
    game = Game()
    game.run()
