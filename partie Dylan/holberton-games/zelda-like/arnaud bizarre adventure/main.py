# ============================================================
#   ARNAUD'S BIZARRE ADVENTURE (zelda-like) — main_web.py
#   Version adaptée pour pygbag (exécution dans le navigateur)
#
#   Seul changement nécessaire : la boucle run() devient async.
#   Ce jeu ne parle pas à l'API (pas de requests, pas de score envoyé),
#   donc pas de pont JS nécessaire ici.
# ============================================================

import asyncio
import sys
import pygame
from level import Level


class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((960, 540))
        pygame.display.set_caption("Arnaud's Bizarre Adventure")
        self.clock = pygame.time.Clock()
        self.load_zone("holberton", None)

    def load_zone(self, zone_name, player_inventory):
        self.level = Level(zone_name, player_inventory, self.change_zone)

    def change_zone(self, target_zone, current_inventory):
        self.load_zone(target_zone, current_inventory)

    # 🔁 CHANGEMENT : async + await asyncio.sleep(0) à chaque tour.
    # Note : `sys.exit()` fonctionne différemment sous Emscripten (il ne
    # tue pas vraiment le processus) — on utilise un simple `return` à la
    # place pour sortir proprement de la boucle.
    async def run(self):
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

            self.screen.fill((20, 20, 25))
            self.level.run()
            pygame.display.update()
            self.clock.tick(60)

            await asyncio.sleep(0)  # rend la main au navigateur

        pygame.quit()


if __name__ == "__main__":
    game = Game()
    asyncio.run(game.run())
