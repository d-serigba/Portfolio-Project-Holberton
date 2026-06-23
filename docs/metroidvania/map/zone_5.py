# ============================================================
#  ARNAUD METROIDVANIA — zone_5.py
#  Zone avec mur plein et passage accroupi
# ============================================================
import pygame
from settings import *
from map.zone_base import ZoneBase
from map.zone_a import EnnemBasique


class Zone5(ZoneBase):
    NOM           = "Zone 5"
    LARGEUR_MONDE = 40 * TAILLE_TUILE
    HAUTEUR_MONDE = 20 * TAILLE_TUILE

    def __init__(self):
        self._init_groupes()
        self._construire()

    def _construire(self):
        T = TAILLE_TUILE
        W = self.LARGEUR_MONDE
        H = self.HAUTEUR_MONDE

        # Sortie droite vers Z1
        self.sorties = [
            {"cote": "droite", "y": H-T*4, "taille": T*2,
             "destination": "zone_1", "spawn": "depuis_z5"},
        ]

        # ── MUR PLEIN — occupe 3/4 droits, du plafond au sol ───
        mur_x = W // 4
        # Mur du plafond jusqu'à H - T*4 (laisse gap accroupi en bas)
        self._mur(mur_x, T*2, T*2, H - T*2 - T*4)

        # ── PASSAGE ACCROUPI — gap de 2T en bas du mur plein ───
        # (pas de mur entre H-T*4 et H-T*2 = passage)

        # ── PLATEFORME LÉGO — haut gauche ──────────────────────
        self._plateforme(T*2, T*5, T*5, T)
        # Légo bleu dessus
        lego = pygame.sprite.Sprite()
        lego.image = self._dessiner_lego()
        lego.rect  = lego.image.get_rect(topleft=(T*3, T*4))
        self.legos.add(lego)

        # ── ENNEMI — au sol à droite du mur plein ──────────────
        EnnemBasique(
            W - T*8, H - T*2 - 32,
            mur_x + T*2, W - T*4
        ).add(self.ennemis)

        self._finaliser()

        # Spawn depuis Z1 — au sol à droite
        self.spawns["droite"] = (W - T*4, H - T*3)

    def _dessiner_lego(self):
        T = TAILLE_TUILE
        surf = pygame.Surface((T, T), pygame.SRCALPHA)
        couleur = (40, 100, 220)   # bleu
        sombre  = (20, 60, 160)
        pygame.draw.rect(surf, couleur, (0, 4, T, T-4))
        pygame.draw.rect(surf, sombre,  (0, 0, T, 4))
        pygame.draw.circle(surf, sombre, (T//4, 4), 4)
        pygame.draw.circle(surf, sombre, (3*T//4, 4), 4)
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
        # Légo
        for l in list(self.legos):
            if joueur.rect.colliderect(l.rect):
                joueur.collecter_lego()
                l.kill()
        return super().update(joueur)

    def dessiner(self, ecran, cam_x, cam_y):
        super().dessiner(ecran, cam_x, cam_y)
        for e in self.ennemis:
            ecran.blit(e.image, (e.rect.x + cam_x, e.rect.y + cam_y))
