# ============================================================
#  ARNAUD METROIDVANIA — zone_3.py
# ============================================================

import pygame
from settings import *
from map.zone_base import ZoneBase
from map.zone_a import Tourelle, EnnemBasique, MissileTourelle


class Pique(pygame.sprite.Sprite):
    DEGATS = 1
    def __init__(self, x, y, largeur):
        super().__init__()
        T = TAILLE_TUILE
        self.image = pygame.Surface((largeur, T), pygame.SRCALPHA)
        nb = largeur // (T // 2)
        for i in range(nb):
            px = i * (T // 2)
            pygame.draw.polygon(self.image, (140, 140, 150), [
                (px, T), (px + T//4, 4), (px + T//2, T)
            ])
        self.rect = self.image.get_rect(topleft=(x, y))
        self.cooldown = 0

    def update(self, joueur):
        if self.cooldown > 0:
            self.cooldown -= 1
        elif self.rect.colliderect(joueur.hitbox):
            joueur.recevoir_degats(self.DEGATS)
            self.cooldown = 60


class PowerUpDoubleSaut(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = self._dessiner()
        self.rect  = self.image.get_rect(topleft=(x, y))
        self.timer = 0

    def _dessiner(self):
        T = TAILLE_TUILE
        surf = pygame.Surface((T, T), pygame.SRCALPHA)
        pygame.draw.rect(surf, (90, 60, 40),   (6, 6, 16, 10))
        pygame.draw.rect(surf, (60, 40, 25),   (4, 16, 24, 8))
        pygame.draw.rect(surf, (200, 170, 80), (8, 8, 12, 3))
        pygame.draw.circle(surf, (80, 200, 255), (16, 4), 3)
        return surf

    def update(self, joueur):
        import math
        self.timer += 1
        self.rect.y += int(math.sin(self.timer * 0.08) * 0.6)
        if self.rect.colliderect(joueur.rect):
            joueur.debloquer("double_saut")
            self.kill()


class Zone3(ZoneBase):
    NOM           = "Zone 3"
    LARGEUR_MONDE = 50 * TAILLE_TUILE
    HAUTEUR_MONDE = 18 * TAILLE_TUILE

    def __init__(self):
        self._init_groupes()
        self.piques    = pygame.sprite.Group()
        self.powerups  = pygame.sprite.Group()
        self.tourelles = pygame.sprite.Group()
        self._construire()

    def _construire(self):
        T = TAILLE_TUILE
        W = self.LARGEUR_MONDE
        H = self.HAUTEUR_MONDE

        # Sortie droite vers Z1
        self.sorties = [
            {"cote": "droite", "y": H-T*4, "taille": T*2,
             "destination": "zone_1", "spawn": "depuis_z3"},
        ]

        # Plateforme centrale surélevée avec tourelle
        plat_x = W//2 - T*3
        plat_y = H - T*6
        self._plateforme(plat_x, plat_y, T*6, T)
        self._mur(plat_x,       plat_y+T, T, T*4)
        self._mur(plat_x + T*3, plat_y+T, T, T*4)

        # Tourelle sur la plateforme — tire vers la gauche
        Tourelle(plat_x + T*2, plat_y - T, direction=-1).add(self.tourelles)

        # Deuxième tourelle — tire vers la droite (vers la porte)
        Tourelle(W - T*8, H - T*2 - T*2, direction=1).add(self.tourelles)

        # Ennemi basique
        EnnemBasique(plat_x + T*8, H - T*2 - 32, plat_x + T*6, plat_x + T*14).add(self.ennemis)

        # Piques au sol
        self.piques.add(Pique(T*14, H - T*2 - T, T*3))
        self.piques.add(Pique(T*19, H - T*2 - T, T*3))

        # Power-up double saut
        self.powerups.add(PowerUpDoubleSaut(T*3, H - T*4))

        self._finaliser()

        # Spawn depuis Z1 — au sol à droite
        self.spawns["droite"] = (W - T*4, H - T*3)

    def update(self, joueur):
        sortie = super().update(joueur)
        for e in list(self.ennemis):
            e.update(joueur, self.plateformes.sprites())
            if e.est_mort(): e.kill()
        for t in list(self.tourelles):
            t.update()
            if t.pret_a_tirer():
                self.missiles.add(MissileTourelle(t.rect.centerx, t.rect.centery, t.direction))
            if t.est_morte(): t.kill()
        for m in list(self.missiles):
            m.update(self.murs.sprites(), 0, self.LARGEUR_MONDE)
            if m.rect.colliderect(joueur.hitbox):
                joueur.recevoir_degats(MissileTourelle.DEGATS)
                m.kill()
        self.piques.update(joueur)
        self.powerups.update(joueur)
        zone_atk = joueur.get_zone_attaque()
        if zone_atk:
            for e in list(self.ennemis):
                if zone_atk.colliderect(e.rect): e.recevoir_degats(joueur.degats)
            for t in list(self.tourelles):
                if zone_atk.colliderect(t.rect): t.recevoir_degats(joueur.degats)
        return sortie

    def dessiner(self, ecran, cam_x, cam_y):
        super().dessiner(ecran, cam_x, cam_y)
        for groupe in [self.piques, self.powerups, self.tourelles, self.missiles, self.ennemis]:
            for s in groupe:
                ecran.blit(s.image, (s.rect.x + cam_x, s.rect.y + cam_y))
