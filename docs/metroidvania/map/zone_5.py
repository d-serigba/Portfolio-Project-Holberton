# ============================================================
#  ARNAUD METROIDVANIA — zone_5.py
# ============================================================
import pygame
from settings import *
from map.zone_base import ZoneBase
from map.panneau import Panneau
from map.zone_a import EnnemBasique

class Zone5(ZoneBase):
    NOM           = "Zone 5"
    LARGEUR_MONDE = 40 * TAILLE_TUILE
    HAUTEUR_MONDE = 20 * TAILLE_TUILE

    def __init__(self):
        self._init_groupes()
        self.panneaux = pygame.sprite.Group()
        self._construire()

    def _construire(self):
        T = TAILLE_TUILE
        W = self.LARGEUR_MONDE
        H = self.HAUTEUR_MONDE

        self.sorties = [
            {"cote": "droite", "y": H-T*4, "taille": T*2,
             "destination": "zone_1", "spawn": "depuis_z5"},
        ]

        # Arche inversee — 2 piliers du plafond, gap accroupi en bas
        arche_x = W // 4
        arche_h = H - T*2 - 60 - T  # gap de 60px au dessus du sol
        self._mur(arche_x,        T*2, T*2, arche_h)  # pilier gauche
        self._mur(arche_x + T*8,  T*2, T*2, arche_h)  # pilier droit
        self._plateforme(arche_x, T*2, T*10, T*2, GRIS_MUR)  # barre du haut

        # Plateformes escalier pour atteindre le Légo
        self._plateforme(T*2, H - T*6,  T*6, T)
        self._plateforme(T*2, H - T*10, T*6, T)
        self._plateforme(T*2, H - T*14, T*6, T)
        self._plateforme(T*2, T*5,      T*6, T)

        # Légo bleu
        lego = pygame.sprite.Sprite()
        lego.image = self._dessiner_lego()
        lego.rect  = lego.image.get_rect(topleft=(T*3, T*4))
        self.legos.add(lego)

        # Ennemi dans l arche
        EnnemBasique(
            arche_x + T*3, H - T*2 - 32,
            arche_x + T*2, arche_x + T*8
        ).add(self.ennemis)

        # Ennemi à droite du mur
        EnnemBasique(W - T*6, H - T*2 - 32, W - T*10, W - T*4).add(self.ennemis)

        # Panneau accroupissement
        Panneau(T*2, H-T*4-T*2, [
            "ACCROUPIR",
            "S / Fleche bas",
            "passe sous les obstacles"
        ]).add(self.panneaux)

        self._finaliser()
        self.spawns["droite"] = (W - T*4, H - T*3)

    def _dessiner_lego(self):
        surf = pygame.Surface((16, 16), pygame.SRCALPHA)
        couleur = (40, 100, 220)
        sombre  = (20, 60, 160)
        pygame.draw.rect(surf, couleur, (0, 4, 16, 12))
        pygame.draw.rect(surf, sombre,  (0, 0, 16, 4))
        pygame.draw.circle(surf, sombre, (5, 4), 3)
        pygame.draw.circle(surf, sombre, (11, 4), 3)
        return surf

    def update(self, joueur):
        for e in list(self.ennemis):
            e.update(joueur, self.plateformes.sprites())
            if e.est_mort(): e.kill()
        zone_atk = joueur.get_zone_attaque()
        if zone_atk:
            for e in list(self.ennemis):
                if zone_atk.colliderect(e.rect):
                    e.recevoir_degats(joueur.degats)
        for p in self.panneaux: p.update(joueur)
        for l in list(self.legos):
            if joueur.rect.colliderect(l.rect):
                joueur.collecter_lego()
                l.kill()
        return super().update(joueur)

    def dessiner(self, ecran, cam_x, cam_y):
        super().dessiner(ecran, cam_x, cam_y)
        for p in self.panneaux: p.dessiner(ecran, cam_x, cam_y)
        for e in self.ennemis:
            ecran.blit(e.image, (e.rect.x + cam_x, e.rect.y + cam_y))
        for l in self.legos:
            ecran.blit(l.image, (l.rect.x + cam_x, l.rect.y + cam_y))
