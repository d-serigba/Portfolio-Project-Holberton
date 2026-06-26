# ============================================================
#  ARNAUD METROIDVANIA — zone_2.py
# ============================================================
import pygame
from settings import *
from map.zone_base import ZoneBase

class Zone2(ZoneBase):
    NOM           = "Zone 2"
    LARGEUR_MONDE = 60 * TAILLE_TUILE
    HAUTEUR_MONDE = 10 * TAILLE_TUILE

    def __init__(self):
        self._init_groupes()
        self._construire()

    def _construire(self):
        T = TAILLE_TUILE
        W = self.LARGEUR_MONDE
        H = self.HAUTEUR_MONDE

        self.sorties = [
            {"cote": "gauche", "y": H-T*4, "taille": T*2,
             "destination": "zone_1", "spawn": "depuis_z2"},
            {"cote": "droite", "y": H-T*4, "taille": T*2,
             "destination": "zone_s1", "spawn": "gauche"},
        ]

        self._finaliser()

    def update(self, joueur):
        return super().update(joueur)

    def dessiner(self, ecran, cam_x, cam_y):
        super().dessiner(ecran, cam_x, cam_y)
