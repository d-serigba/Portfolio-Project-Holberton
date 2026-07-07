import pygame
import sys
from level import Level

class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((960, 540)) # Taille fenetre
        pygame.display.set_caption("Arnaud's Bizarre Adventure")
        self.clock = pygame.time.Clock()
        
        # On démarre à Holberton avec un inventaire vide
        self.load_zone("holberton", None)

    def load_zone(self, zone_name, player_inventory):
        """Détruit la scène actuelle et charge la nouvelle en conservant les objets"""
        self.level = Level(zone_name, player_inventory, self.change_zone)

    def change_zone(self, target_zone, current_inventory):
        """Fonction de rappel (callback) appelée par le niveau"""
        self.load_zone(target_zone, current_inventory)

    def run(self):
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

            self.screen.fill((20, 20, 25))
            self.level.run()
            pygame.display.update()
            self.clock.tick(60)

if __name__ == '__main__':
    game = Game()
    game.run()
