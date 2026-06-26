import pygame
import math
from settings import *
from map.zone_base import ZoneBase

class ZoneS1(ZoneBase):
    NOM           = "Zone Save 1"
    LARGEUR_MONDE = 15 * TAILLE_TUILE
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
             "destination": "zone_2", "spawn": "droite"},
            {"cote": "droite", "y": H-T*4, "taille": T*2,
             "destination": "zone_8", "spawn": "gauche"},
        ]
        self._plateforme(W//2 - T*2, H - T*5, T*4, T)
        self._finaliser()
        self.drapeau_x    = W // 2
        self.drapeau_y    = H - T*5 - T*2
        self.drapeau_rect = pygame.Rect(self.drapeau_x - T, self.drapeau_y, T*2, T*2)
        self.timer_drapeau = 0
        self.deja_active   = False
        self.cooldown_save = 0

    def update(self, joueur):
        self.timer_drapeau = (self.timer_drapeau + 1) % 60
        if self.cooldown_save > 0:
            self.cooldown_save -= 1
        return super().update(joueur)

    def verifier_save(self, joueur, state_manager):
        T = TAILLE_TUILE
        if joueur.rect.colliderect(self.drapeau_rect) and self.cooldown_save == 0:
            self.deja_active   = True
            self.cooldown_save = 600
            joueur.coeurs = joueur.coeurs_max
            if joueur.capacites.get("missiles"):
                joueur.missiles = joueur.missiles_max
            state_manager.sauvegarder(
                joueur, "zone_s1",
                spawn=[self.drapeau_x - 16, self.drapeau_y + T*2],
                checkpoint_id="zone_s1_drapeau"
            )
            return True
        return False

    def dessiner(self, ecran, cam_x, cam_y):
        super().dessiner(ecran, cam_x, cam_y)
        T = TAILLE_TUILE
        x = self.drapeau_x + cam_x
        y = self.drapeau_y + cam_y
        pygame.draw.rect(ecran, (60, 60, 70), (x - 2, y, 4, T*2))
        if self.deja_active:
            pulse = int(180 + 75 * math.sin(self.timer_drapeau * 0.2))
            couleur = (0, pulse, 80)
        else:
            couleur = (90, 90, 100)
        pygame.draw.polygon(ecran, couleur, [
            (x + 2, y), (x + 2, y + 18), (x + 22, y + 9),
        ])
        f = pygame.font.SysFont("monospace", 14, bold=True)
        t = f.render("SAVE", True, (200,255,200) if self.deja_active else (140,140,150))
        ecran.blit(t, (x - t.get_width()//2, y - 20))
