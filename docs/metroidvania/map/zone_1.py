# ============================================================
#  ARNAUD METROIDVANIA — zone_1.py
#  Grande zone verticale — hub central
# ============================================================

import pygame
from settings import *
from map.zone_base import ZoneBase


class Zone1(ZoneBase):
    NOM           = "Zone 1"
    LARGEUR_MONDE = 20 * TAILLE_TUILE
    HAUTEUR_MONDE = 80 * TAILLE_TUILE

    def __init__(self):
        self._init_groupes()
        self._construire()

    def _construire(self):
        T  = TAILLE_TUILE
        W  = self.LARGEUR_MONDE
        H  = self.HAUTEUR_MONDE
        G  = T*2
        M  = W//2 - T*2
        D  = W - T*6
        LP = T*5

        # SORTIES EN PREMIER — ZoneBase génère les murs avec les trous
        self.sorties = [
            {"cote": "gauche", "y": H-T*4,  "taille": T*2,
             "destination": "zone_a",  "spawn": "droite"},
            {"cote": "gauche", "y": H-T*36, "taille": T*4,
             "destination": "zone_3",  "spawn": "droite"},
            {"cote": "gauche", "y": H-T*42, "taille": T*4,
             "destination": "zone_s2", "spawn": "droite"},
            {"cote": "gauche", "y": H-T*72, "taille": T*4,
             "destination": "zone_5",  "spawn": "droite"},
            {"cote": "gauche", "y": T*2,    "taille": T*4,
             "destination": "zone_6",  "spawn": "droite"},
            {"cote": "droite", "y": H-T*4,  "taille": T*2,
             "destination": "zone_2",  "spawn": "gauche"},
            {"cote": "droite", "y": H-T*56, "taille": T*4,
             "destination": "zone_4",  "spawn": "gauche"},
        ]

        # PLATEFORMES motif G/M/D/M/G
        self._plateforme(G, H-T*6,  LP, T)
        self._plateforme(M, H-T*10, LP, T)
        self._plateforme(D, H-T*14, LP, T)
        self._plateforme(M, H-T*18, LP, T)
        self._plateforme(G, H-T*22, LP, T)
        self._plateforme(M, H-T*26, LP, T)
        self._plateforme(D, H-T*30, LP, T)
        self._plateforme(G, H-T*34, LP, T)   # vers Z3
        self._plateforme(D, H-T*35, LP, T)   # collée Z3
        self._plateforme(G, H-T*38, LP, T)   # vers ZS2
        self._plateforme(D, H-T*42, LP, T)   # palier ZS2
        self._plateforme(G, H-T*46, LP, T)
        self._plateforme(D, H-T*48, LP, T)
        self._plateforme(M, H-T*51, LP, T)
        self._plateforme(G, H-T*56, LP, T)
        self._plateforme(M, H-T*62, LP, T)
        self._plateforme(D, H-T*68, LP, T)
        self._plateforme(M, H-T*74, LP, T)

        # ZoneBase génère sol, plafond et murs avec trous
        self._finaliser()
