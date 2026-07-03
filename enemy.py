# ============================================================
#  ARNO'S BIZARRE ADVENTURE — enemy.py
#  Les ennemis qui patrouillent dans la banlieue
# ============================================================

import pygame
import math
from settings import *


class Ennemi(pygame.sprite.Sprite):
    """
    Ennemi de base : patrouille sur une ligne,
    fonce sur Arno quand il s'approche.
    """

    DISTANCE_DETECTION = 150   # pixels — distance à laquelle il voit Arno
    DISTANCE_ATTAQUE   = 28    # pixels — distance à laquelle il frappe

    def __init__(self, x, y, patrouille_x1, patrouille_x2, patrouille_y1=None, patrouille_y2=None):
        super().__init__()

        self.image = self._dessiner_ennemi()
        self.rect  = self.image.get_rect(topleft=(x, y))
        self.hitbox = self.rect.inflate(-6, -6)

        # Points de patrouille
        self.pat_x1 = patrouille_x1
        self.pat_x2 = patrouille_x2
        self.pat_y1 = patrouille_y1 if patrouille_y1 is not None else y
        self.pat_y2 = patrouille_y2 if patrouille_y2 is not None else y
        self.direction_pat = 1   # 1 ou -1

        # Stats
        self.pv             = PV_ENNEMI
        self.cooldown_degats = 0
        self.cooldown_attaque = 0

        # État
        self.etat = "patrouille"   # "patrouille" ou "chasse"

    # ----------------------------------------------------------
    def _dessiner_ennemi(self):
        surf = pygame.Surface((32, 32), pygame.SRCALPHA)
        # Corps rouge
        pygame.draw.rect(surf, COULEUR_ENNEMI,      (8, 14, 16, 14))
        pygame.draw.rect(surf, (200, 130, 80),       (11, 6, 10, 10))  # tête
        pygame.draw.rect(surf, (100, 20, 20),        (8, 28,  6,  4))  # jambe g
        pygame.draw.rect(surf, (100, 20, 20),        (18, 28, 6,  4))  # jambe d
        pygame.draw.rect(surf, (140, 30, 30),        (4, 14,  6, 10))  # bras g
        pygame.draw.rect(surf, (140, 30, 30),        (22, 14, 6, 10))  # bras d
        # Yeux menaçants
        pygame.draw.rect(surf, BLANC, (13, 9, 3, 3))
        pygame.draw.rect(surf, BLANC, (17, 9, 3, 3))
        pygame.draw.rect(surf, NOIR,  (14, 10, 2, 2))
        pygame.draw.rect(surf, NOIR,  (18, 10, 2, 2))
        # Sourcils froncés
        pygame.draw.line(surf, NOIR, (12, 8), (15, 9), 2)
        pygame.draw.line(surf, NOIR, (17, 9), (20, 8), 2)
        return surf

    # ----------------------------------------------------------
    def update(self, joueur, obstacles):
        distance = self._distance(joueur)

        if distance < self.DISTANCE_DETECTION:
            self.etat = "chasse"
        else:
            self.etat = "patrouille"

        if self.etat == "chasse":
            self._chasser(joueur, obstacles)
            self._attaquer(joueur)
        else:
            self._patrouiller(obstacles)

        if self.cooldown_degats  > 0: self.cooldown_degats  -= 1
        if self.cooldown_attaque > 0: self.cooldown_attaque -= 1

    def _distance(self, joueur):
        dx = self.rect.centerx - joueur.rect.centerx
        dy = self.rect.centery - joueur.rect.centery
        return math.sqrt(dx*dx + dy*dy)

    # ----------------------------------------------------------
    def _patrouiller(self, obstacles):
        self.hitbox.x += self.direction_pat * VITESSE_ENNEMI

        # --- Rebond sur les bornes de patrouille ---
        # On compare le CENTRE de la hitbox pour éviter les décalages
        if self.hitbox.centerx > self.pat_x2:
            self.hitbox.centerx = self.pat_x2
            self.direction_pat = -1          # force la direction, sans multiplier
        elif self.hitbox.centerx < self.pat_x1:
            self.hitbox.centerx = self.pat_x1
            self.direction_pat = 1

        # --- Collision avec les murs (séparée du rebond) ---
        for obs in obstacles:
            if self.hitbox.colliderect(obs.rect):
                # Repousse l'ennemi hors du mur selon sa direction actuelle
                if self.direction_pat > 0:
                    self.hitbox.right = obs.rect.left
                    self.direction_pat = -1
                else:
                    self.hitbox.left = obs.rect.right
                    self.direction_pat = 1
                break

        self.rect.center = self.hitbox.center

    def _chasser(self, joueur, obstacles):
        """Se déplace vers Arno axe par axe pour éviter les murs."""
        dx = joueur.rect.centerx - self.rect.centerx
        dy = joueur.rect.centery - self.rect.centery
        dist = max(1, math.sqrt(dx*dx + dy*dy))

        # Axe X
        self.hitbox.x += int(dx / dist * VITESSE_ENNEMI)
        for obs in obstacles:
            if self.hitbox.colliderect(obs.rect):
                if dx > 0:
                    self.hitbox.right = obs.rect.left
                else:
                    self.hitbox.left = obs.rect.right
                break

        # Axe Y
        self.hitbox.y += int(dy / dist * VITESSE_ENNEMI)
        for obs in obstacles:
            if self.hitbox.colliderect(obs.rect):
                if dy > 0:
                    self.hitbox.bottom = obs.rect.top
                else:
                    self.hitbox.top = obs.rect.bottom
                break

        self.rect.center = self.hitbox.center

    def _attaquer(self, joueur):
        if self._distance(joueur) < self.DISTANCE_ATTAQUE and self.cooldown_attaque == 0:
            joueur.recevoir_degats(DEGATS_ENNEMI)
            self.cooldown_attaque = 60

    # ----------------------------------------------------------
    def recevoir_degats(self, degats):
        self.pv -= degats
        # Flash rouge
        surf = self._dessiner_ennemi()
        surf.fill((255, 100, 100, 150), special_flags=pygame.BLEND_RGBA_ADD)
        self.image = surf

    def est_mort(self):
        return self.pv <= 0
