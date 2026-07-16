# ============================================================
#  ARNAUD METROIDVANIA — world.py
#  Tuiles, caméra, niveau de test du moteur
# ============================================================

import pygame
from settings import *


# ============================================================
#  TUILES
# ============================================================

class Tuile(pygame.sprite.Sprite):
    def __init__(self, x, y, type_tuile):
        super().__init__()
        self.image = self._dessiner(type_tuile)
        self.rect  = self.image.get_rect(topleft=(x, y))

    def _dessiner(self, t):
        surf = pygame.Surface((TAILLE_TUILE, TAILLE_TUILE))
        if t == "sol":
            surf.fill(GRIS_PLATEFORME)
            pygame.draw.rect(surf, (110, 110, 125), (0, 0, 32, 4))   # bord haut clair
            pygame.draw.rect(surf, (60, 60, 70),    (0, 28, 32, 4))  # bord bas sombre
        elif t == "mur":
            surf.fill(GRIS_MUR)
            for i in range(0, 32, 8):
                pygame.draw.line(surf, (55, 55, 65), (0, i), (32, i), 1)
            for j in range(0, 32, 16):
                pygame.draw.line(surf, (55, 55, 65), (j, 0), (j, 32), 1)
        elif t == "plafond":
            surf.fill(GRIS_MUR)
            pygame.draw.rect(surf, (60, 60, 70), (0, 0, 32, 4))
        elif t == "save":
            surf.fill((20, 60, 80))
            pygame.draw.rect(surf, (40, 120, 160), (8, 8, 16, 16))
            pygame.draw.rect(surf, (60, 160, 200), (12, 12, 8, 8))
        else:
            surf.fill(GRIS_MUR)
        return surf


class TuileSolide(Tuile):
    """Tuile qui bloque le joueur dans toutes les directions."""
    pass


class TuileSol(Tuile):
    """Plateforme — bloque seulement par le dessus."""
    pass


# ============================================================
#  CAMÉRA
# ============================================================

class Camera:
    def __init__(self, largeur_monde, hauteur_monde):
        self.dx = 0
        self.dy = 0
        self.largeur_monde  = largeur_monde
        self.hauteur_monde  = hauteur_monde

    def appliquer(self, entite):
        return entite.rect.move(self.dx, self.dy)

    def appliquer_rect(self, rect):
        return rect.move(self.dx, self.dy)

    def mettre_a_jour(self, cible):
        x = LARGEUR  // 2 - cible.rect.centerx
        y = HAUTEUR  // 2 - cible.rect.centery

        # Zone morte verticale — la caméra ne suit pas chaque micro-saut
        zone_morte = 80
        cible_y = HAUTEUR // 2 - cible.rect.centery
        if abs(cible_y - self.dy) > zone_morte:
            self.dy += (cible_y - self.dy) * 0.1
        else:
            self.dy = self.dy  # reste stable

        # Horizontal : suit immédiatement
        self.dx = x

        # Limites du monde
        self.dx = min(0, self.dx)
        self.dy = min(0, self.dy)
        self.dx = max(LARGEUR  - self.largeur_monde,  self.dx)
        self.dy = max(HAUTEUR  - self.hauteur_monde, self.dy)

        self.dx = int(self.dx)
        self.dy = int(self.dy)


# ============================================================
#  NIVEAU DE TEST — pour valider le moteur physique
#
#  Légende :
#  . = vide
#  S = sol solide
#  M = mur solide
#  P = plafond
#  _ = plateforme (sol traversable par le bas)  [à implémenter]
#  Z = spawn Arnaud
# ============================================================

CARTE_TEST = [
    "MMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMM",
    "M....................................M",
    "M....................................M",
    "M....................................M",
    "M.............SSSS...................M",
    "M....................................M",
    "M....................................M",
    "M...SSSS.............................M",
    "M....................................M",
    "M....................................M",
    "M..............SSSSSS................M",
    "M....................................M",
    "M....................................M",
    "M.Z..................................M",
    "MSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSM",
    "MSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSM",
]


class Niveau:
    def __init__(self, carte=None):
        if carte is None:
            carte = CARTE_TEST

        self.solides    = pygame.sprite.Group()  # murs + plafonds
        self.plateformes = pygame.sprite.Group() # sols traversables
        self.tous_sols  = pygame.sprite.Group()  # sol + solides (pour gravité)
        self.spawn      = (100, 100)

        self._charger(carte)

        self.largeur_monde = len(carte[0]) * TAILLE_TUILE
        self.hauteur_monde = len(carte)    * TAILLE_TUILE
        self.camera = Camera(self.largeur_monde, self.hauteur_monde)

    def _charger(self, carte):
        for lig_idx, ligne in enumerate(carte):
            for col_idx, char in enumerate(ligne):
                x = col_idx * TAILLE_TUILE
                y = lig_idx * TAILLE_TUILE

                if char == "Z":
                    self.spawn = (x, y - TAILLE_TUILE)  # spawn au-dessus du sol

                if char in ("M", "P"):
                    t = TuileSolide(x, y, "mur" if char == "M" else "plafond")
                    self.solides.add(t)
                    self.tous_sols.add(t)

                elif char == "S":
                    t = TuileSol(x, y, "sol")
                    self.plateformes.add(t)
                    self.tous_sols.add(t)

    def dessiner(self, ecran, camera):
        for t in self.plateformes:
            ecran.blit(t.image, camera.appliquer(t))
        for t in self.solides:
            ecran.blit(t.image, camera.appliquer(t))
