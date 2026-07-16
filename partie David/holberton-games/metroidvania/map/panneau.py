# ============================================================
#  ARNAUD METROIDVANIA — panneau.py
#  Panneaux d'information in-game
# ============================================================

import pygame
from settings import *


class Panneau(pygame.sprite.Sprite):
    """
    Panneau flottant avec texte — s'affiche quand Arnaud s'approche.
    """
    DISTANCE_AFFICHAGE = 120   # pixels

    def __init__(self, x, y, lignes):
        super().__init__()
        self.rect   = pygame.Rect(x, y, TAILLE_TUILE, TAILLE_TUILE*2)
        self.lignes = lignes   # liste de strings
        self.police = pygame.font.SysFont("monospace", 13, bold=True)
        self.visible = False
        self.image  = self._dessiner_panneau()

    def _dessiner_panneau(self):
        T = TAILLE_TUILE
        surf = pygame.Surface((T, T*2), pygame.SRCALPHA)
        # Poteau
        pygame.draw.rect(surf, (80, 60, 40), (T//2-2, T, 4, T))
        # Panneau
        pygame.draw.rect(surf, (180, 140, 80), (0, 0, T, T-4))
        pygame.draw.rect(surf, (140, 100, 50), (0, 0, T, T-4), 2)
        # Point d'exclamation
        f = pygame.font.SysFont("monospace", 18, bold=True)
        t = f.render("!", True, (60, 30, 10))
        surf.blit(t, (T//2 - t.get_width()//2, 4))
        return surf

    def update(self, joueur):
        dx = abs(joueur.rect.centerx - self.rect.centerx)
        dy = abs(joueur.rect.centery - self.rect.centery)
        self.visible = (dx < self.DISTANCE_AFFICHAGE and dy < self.DISTANCE_AFFICHAGE * 1.5)

    def dessiner(self, ecran, cam_x, cam_y):
        # Panneau physique
        ecran.blit(self.image, (self.rect.x + cam_x, self.rect.y + cam_y))

        # Bulle de texte si proche
        if self.visible:
            self._dessiner_bulle(ecran, cam_x, cam_y)

    def _dessiner_bulle(self, ecran, cam_x, cam_y):
        marge   = 10
        padding = 8
        hauteur_ligne = 16

        # Calculer dimensions
        largeur_max = max(self.police.size(l)[0] for l in self.lignes) + padding*2
        hauteur     = len(self.lignes) * hauteur_ligne + padding*2

        # Position au-dessus du panneau
        bx = self.rect.centerx + cam_x - largeur_max // 2
        by = self.rect.y + cam_y - hauteur - 8

        # Fond semi-transparent
        surf = pygame.Surface((largeur_max, hauteur), pygame.SRCALPHA)
        surf.fill((20, 20, 30, 200))
        pygame.draw.rect(surf, (100, 180, 255), (0, 0, largeur_max, hauteur), 2)
        ecran.blit(surf, (bx, by))

        # Texte
        for i, ligne in enumerate(self.lignes):
            couleur = (255, 220, 50) if i == 0 else (200, 220, 255)
            t = self.police.render(ligne, True, couleur)
            ecran.blit(t, (bx + padding, by + padding + i * hauteur_ligne))
