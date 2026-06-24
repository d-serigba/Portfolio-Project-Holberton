# ============================================================
#  ARNAUD METROIDVANIA — zone_6.py
#  Mini-boss zone
# ============================================================

import pygame
import random
import math
from settings import *
from map.zone_base import ZoneBase


# ============================================================
#  ROCHER — tombe du plafond (pattern 2)
# ============================================================
class Rocher(pygame.sprite.Sprite):
    DEGATS  = 1
    VITESSE = 6

    def __init__(self, x):
        super().__init__()
        T = TAILLE_TUILE
        taille = random.randint(16, 32)
        self.image = pygame.Surface((taille, taille), pygame.SRCALPHA)
        # Dessin rocher pixel art
        couleur = (100, 90, 80)
        pygame.draw.polygon(self.image, couleur, [
            (taille//2, 0), (taille, taille//3),
            (taille, taille), (0, taille), (0, taille//3)
        ])
        pygame.draw.polygon(self.image, (130, 115, 100), [
            (taille//2, 2), (taille-4, taille//3),
            (taille//2, taille//2)
        ])
        self.rect     = self.image.get_rect(topleft=(x, 0))
        self.cooldown = 0

    def update(self, joueur, sol_y):
        self.rect.y += self.VITESSE
        if self.cooldown > 0:
            self.cooldown -= 1
        if self.rect.colliderect(joueur.hitbox) and self.cooldown == 0:
            joueur.recevoir_degats(self.DEGATS)
            self.cooldown = 60
        if self.rect.top > sol_y:
            self.kill()


# ============================================================
#  MINI-BOSS
# ============================================================
class MiniBoss(pygame.sprite.Sprite):
    PV_MAX          = 10
    VITESSE_NORMALE = 1
    VITESSE_RUSH    = 14
    DUREE_CLIGNO    = 78   # frames (~1.67s)
    DUREE_STUN      = 90    # frames (1.5s)
    DUREE_SAUT      = 40    # frames
    COOLDOWN_PATTERN = 180  # frames entre patterns

    ETATS = ["repos", "cligno", "rush", "stun", "saut"]

    def __init__(self, x, y):
        super().__init__()
        self.pv          = self.PV_MAX
        self.hitbox      = pygame.Rect(x, y, 64, 80)
        self.rect        = self.hitbox.copy()
        self.direction   = -1   # -1 = gauche, 1 = droite
        self.etat        = "repos"
        self.timer       = self.COOLDOWN_PATTERN
        self.cligno_vis  = True
        self.cligno_timer = 0
        self.vel_y       = 0
        self.au_sol      = True
        self.rochers     = pygame.sprite.Group()
        self.rocher_timer = 0
        self.image       = self._dessiner()
        self.mort        = False

    def _dessiner(self, cligno=False, stun=False):
        surf = pygame.Surface((64, 80), pygame.SRCALPHA)

        if stun:
            corps = (100, 80, 80)
            detail = (140, 100, 100)
        elif cligno:
            corps = (220, 80, 40)
            detail = (255, 140, 60)
        else:
            corps = (160, 30, 30)
            detail = (200, 60, 60)

        # Corps principal
        pygame.draw.rect(surf, corps,  (8, 20, 48, 50))
        # Tête
        pygame.draw.rect(surf, detail, (12, 4,  40, 22))
        # Yeux
        pygame.draw.rect(surf, (255, 220, 0), (18, 10, 8, 8))
        pygame.draw.rect(surf, (255, 220, 0), (38, 10, 8, 8))
        pygame.draw.rect(surf, (0, 0, 0),     (21, 12, 4, 4))
        pygame.draw.rect(surf, (0, 0, 0),     (41, 12, 4, 4))
        # Bras
        pygame.draw.rect(surf, corps, (0,  24, 10, 30))
        pygame.draw.rect(surf, corps, (54, 24, 10, 30))
        # Jambes
        pygame.draw.rect(surf, (100, 20, 20), (10, 68, 18, 12))
        pygame.draw.rect(surf, (100, 20, 20), (36, 68, 18, 12))
        # Sourcils froncés
        pygame.draw.line(surf, (0,0,0), (16, 8),  (26, 11), 3)
        pygame.draw.line(surf, (0,0,0), (48, 11), (38, 8),  3)
        # Stun — étoiles au-dessus
        if stun:
            for i in range(3):
                sx = 20 + i * 12
                pygame.draw.circle(surf, (255, 220, 0), (sx, 0), 4)

        return surf

    def update(self, joueur, plateformes, sol_y, largeur):
        T = TAILLE_TUILE

        # Gravité simple
        if not self.au_sol:
            self.vel_y += 0.8
            self.hitbox.y += int(self.vel_y)
            for p in plateformes:
                if self.hitbox.colliderect(p.rect) and self.vel_y > 0:
                    self.hitbox.bottom = p.rect.top
                    self.vel_y = 0
                    self.au_sol = True

        self.timer -= 1

        # ── Machine à états ──────────────────────────────────
        if self.etat == "repos":
            if self.timer <= 0:
                # Choisir pattern aléatoirement
                if random.random() < 0.5:
                    self.etat = "cligno"
                else:
                    self.etat = "saut"
                self.timer = self.DUREE_CLIGNO

        elif self.etat == "cligno":
            # Clignotement d'avertissement
            self.cligno_timer += 1
            if self.cligno_timer % 8 == 0:
                self.cligno_vis = not self.cligno_vis
            # Direction vers le joueur
            self.direction = 1 if joueur.rect.centerx > self.hitbox.centerx else -1
            if self.timer <= 0:
                self.etat  = "rush"
                self.timer = 30   # durée max du rush
                self.cligno_vis = True

        elif self.etat == "rush":
            self.hitbox.x += self.direction * self.VITESSE_RUSH
            # Collision murs
            if self.hitbox.left < T*2 or self.hitbox.right > largeur - T*2 or self.timer <= 0:
                self.hitbox.x = max(T*2, min(largeur - T*2 - 64, self.hitbox.x))
                self.etat  = "stun"
                self.timer = self.DUREE_STUN

        elif self.etat == "stun":
            if self.timer <= 0:
                self.etat  = "repos"
                self.timer = self.COOLDOWN_PATTERN

        elif self.etat == "saut":
            # Saute sur place
            if self.au_sol:
                self.vel_y  = -12
                self.au_sol = False
            # Fait tomber des rochers
            self.rocher_timer += 1
            if self.rocher_timer % 15 == 0:
                rx = random.randint(T*2, largeur - T*4)
                self.rochers.add(Rocher(rx))
            if self.timer <= 0:
                self.etat  = "repos"
                self.timer = self.COOLDOWN_PATTERN
                self.rocher_timer = 0

        # Rochers
        self.rochers.update(joueur, sol_y)

        # Dégâts au contact
        if self.hitbox.colliderect(joueur.hitbox) and self.etat == "rush":
            joueur.recevoir_degats(1)

        # Mise à jour image
        self.image = self._dessiner(
            cligno=self.etat == "cligno" and not self.cligno_vis,
            stun=self.etat == "stun"
        )
        self.rect = self.hitbox.copy()

    def recevoir_degats(self, degats):
        if self.etat == "stun":   # plus de dégâts pendant stun
            self.pv -= degats
            if self.pv < 0:
                self.pv = 0

    def est_mort(self):
        return self.pv <= 0

    def dessiner(self, ecran, cam_x, cam_y):
        if self.etat == "cligno" and not self.cligno_vis:
            return  # invisible pendant clignotement
        ecran.blit(self.image, (self.hitbox.x + cam_x, self.hitbox.y + cam_y))
        # Barre de vie
        bx = self.hitbox.x + cam_x
        by = self.hitbox.y + cam_y - 14
        bw = 64
        pygame.draw.rect(ecran, (60, 20, 20),  (bx, by, bw, 8))
        pygame.draw.rect(ecran, (220, 40, 40), (bx, by, int(bw * self.pv / self.PV_MAX), 8))
        pygame.draw.rect(ecran, BLANC,         (bx, by, bw, 8), 1)
        # Rochers
        for r in self.rochers:
            ecran.blit(r.image, (r.rect.x + cam_x, r.rect.y + cam_y))



class LegoBlastItem(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = self._dessiner()
        self.rect  = self.image.get_rect(topleft=(x, y))
        self.timer = 0

    def _dessiner(self):
        surf = pygame.Surface((24, 24), pygame.SRCALPHA)
        # Canon pixel art
        pygame.draw.rect(surf, (60, 60, 200),  (2, 8, 16, 10))   # corps
        pygame.draw.rect(surf, (40, 40, 160),  (14, 10, 8, 6))   # canon
        pygame.draw.rect(surf, (255, 220, 50), (0, 9, 6, 8))     # poignee
        pygame.draw.circle(surf, (100, 200, 255), (20, 6), 4)    # eclat
        return surf

    def update(self):
        import math
        self.timer += 1
        self.rect.y += int(math.sin(self.timer * 0.08) * 0.6)

# ============================================================
#  ZONE 6
# ============================================================
class Zone6(ZoneBase):
    NOM           = "Zone 6 — Mini Boss"
    LARGEUR_MONDE = 40 * TAILLE_TUILE
    HAUTEUR_MONDE = 15 * TAILLE_TUILE

    def __init__(self):
        self._init_groupes()
        self.mini_boss    = None
        self.boss_vaincu  = False
        self.items        = pygame.sprite.Group()
        self._construire()

    def _construire(self):
        T = TAILLE_TUILE
        W = self.LARGEUR_MONDE
        H = self.HAUTEUR_MONDE

        self.sorties = [
            {"cote": "droite", "y": H-T*4, "taille": T*2,
             "destination": "zone_1", "spawn": "depuis_z6"},
        ]

        # 2 plateformes au centre
        self._plateforme(T*4,      H - T*6, T*8, T)   # gauche
        self._plateforme(W - T*12, H - T*6, T*8, T)   # droite

        self._finaliser()

        self.spawns["droite"] = (W - T*4, H - T*3)

        # Mini-boss au centre
        self.mini_boss = MiniBoss(W//2 - 32, H - T*2 - 80)

    def update(self, joueur):
        if self.mini_boss and not self.boss_vaincu:
            self.mini_boss.update(
                joueur,
                self.plateformes.sprites(),
                self.HAUTEUR_MONDE - TAILLE_TUILE*2,
                self.LARGEUR_MONDE
            )

            # Attaque du joueur sur le boss
            zone_atk = joueur.get_zone_attaque()
            if zone_atk and zone_atk.colliderect(self.mini_boss.hitbox):
                self.mini_boss.recevoir_degats(joueur.degats)
                # Recul du joueur
                dx = 1 if joueur.rect.centerx > self.mini_boss.hitbox.centerx else -1
                joueur.hitbox.x += dx * 8
                joueur.vel_x     = dx * 4

            if self.mini_boss.est_mort():
                self.boss_vaincu = True
                # Drop le Légo Blast
                self.items.add(LegoBlastItem(
                    self.mini_boss.hitbox.centerx - 12,
                    self.mini_boss.hitbox.top - 30
                ))
                print("[BOSS] Mini-boss vaincu ! Légo Blast droppé !")

        # Items au sol
        self.items.update()
        for item in list(self.items):
            if joueur.rect.colliderect(item.rect):
                joueur.debloquer("lego_blast")
                item.kill()
                print("[ITEM] Légo Blast ramassé !")

        return super().update(joueur)

    def dessiner(self, ecran, cam_x, cam_y):
        super().dessiner(ecran, cam_x, cam_y)
        if self.mini_boss and not self.boss_vaincu:
            self.mini_boss.dessiner(ecran, cam_x, cam_y)
            for r in self.mini_boss.rochers:
                ecran.blit(r.image, (r.rect.x + cam_x, r.rect.y + cam_y))
        for item in self.items:
            ecran.blit(item.image, (item.rect.x + cam_x, item.rect.y + cam_y))
