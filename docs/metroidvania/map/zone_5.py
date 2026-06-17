# ============================================================
#  ARNAUD METROIDVANIA — zone_5.py
# ============================================================

import pygame
from settings import *


class Zone5:
    LARGEUR_MONDE = 50 * TAILLE_TUILE
    HAUTEUR_MONDE = 40 * TAILLE_TUILE

    def __init__(self):
        self.plateformes = pygame.sprite.Group()
        self.murs        = pygame.sprite.Group()
        self.ennemis     = pygame.sprite.Group()
        self.legos       = pygame.sprite.Group()
        self.checkpoints = []
        self.missiles    = pygame.sprite.Group()
        self._construire()
        self.spawns = {
            "defaut" : (self.LARGEUR_MONDE // 2, self.HAUTEUR_MONDE - 3 * TAILLE_TUILE),
            "haut"   : (self.LARGEUR_MONDE // 2, 3 * TAILLE_TUILE),
            "gauche" : (3 * TAILLE_TUILE, self.HAUTEUR_MONDE // 2),
            "droite" : (self.LARGEUR_MONDE - 3 * TAILLE_TUILE, self.HAUTEUR_MONDE // 2),
        }
        self.sorties = []

    def _construire(self):
        T = TAILLE_TUILE
        W = self.LARGEUR_MONDE
        H = self.HAUTEUR_MONDE
        self._plateforme(0, H - T*2, W, T*2)
        self._plateforme(0, 0, W, T*2, GRIS_MUR)
        self._mur(0, 0, T*2, H)
        self._mur(W - T*2, 0, T*2, H)

    def _plateforme(self, x, y, w, h, couleur=None):
        if couleur is None:
            couleur = GRIS_PLATEFORME
        s = pygame.sprite.Sprite()
        s.image = pygame.Surface((w, h))
        s.image.fill(couleur)
        pygame.draw.rect(s.image, (
            min(couleur[0]+30,255),
            min(couleur[1]+30,255),
            min(couleur[2]+30,255)
        ), (0, 0, w, 4))
        s.rect = s.image.get_rect(topleft=(x, y))
        self.plateformes.add(s)

    def _mur(self, x, y, w, h):
        s = pygame.sprite.Sprite()
        s.image = pygame.Surface((w, h))
        s.image.fill(GRIS_MUR)
        for i in range(0, h, 16):
            pygame.draw.line(s.image, (50,50,60), (0,i), (w,i), 1)
        s.rect = s.image.get_rect(topleft=(x, y))
        self.murs.add(s)

    def update(self, joueur):
        pass

    def dessiner(self, ecran, cam_x, cam_y):
        for groupe in [self.plateformes, self.murs, self.ennemis, self.legos]:
            for s in groupe:
                ecran.blit(s.image, (s.rect.x + cam_x, s.rect.y + cam_y))
        f = pygame.font.SysFont("monospace", 28, bold=True)
        t = f.render("zone_5 — squelette", True, (60, 60, 80))
        ecran.blit(t, (ecran.get_width()//2 - t.get_width()//2, 40))
