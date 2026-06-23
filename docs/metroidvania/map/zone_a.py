# ============================================================
#  ARNAUD METROIDVANIA — zone_a.py
#
#  Zone A = tutoriel implicite, flow vers la gauche
#  Le level design enseigne sans texte :
#    1. Bordure haute       → apprend le SAUT
#    2. Ennemi basique      → apprend l'ATK
#    3. Tourelle (1.5s)     → apprend l'ESQUIVE
#    4. Checkpoint S        → sauvegarde
# ============================================================

import pygame
from settings import *


# ============================================================
#  TUILES
# ============================================================

class Plateforme(pygame.sprite.Sprite):
    """Sol et plateformes — Arnaud peut marcher dessus."""
    def __init__(self, x, y, largeur, hauteur, couleur=GRIS_PLATEFORME):
        super().__init__()
        self.image = self._dessiner(largeur, hauteur, couleur)
        self.rect  = self.image.get_rect(topleft=(x, y))

    def _dessiner(self, w, h, couleur):
        surf = pygame.Surface((w, h))
        surf.fill(couleur)
        # Bord supérieur plus clair — effet beton
        pygame.draw.rect(surf, (
            min(couleur[0] + 30, 255),
            min(couleur[1] + 30, 255),
            min(couleur[2] + 30, 255)
        ), (0, 0, w, 4))
        # Bord inférieur plus sombre
        pygame.draw.rect(surf, (
            max(couleur[0] - 20, 0),
            max(couleur[1] - 20, 0),
            max(couleur[2] - 20, 0)
        ), (0, h - 4, w, 4))
        # Joints horizontaux style béton
        for i in range(32, h, 32):
            pygame.draw.line(surf, (max(couleur[0]-10,0), max(couleur[1]-10,0), max(couleur[2]-10,0)),
                             (0, i), (w, i), 1)
        return surf


class Mur(pygame.sprite.Sprite):
    """Mur vertical — bloque le joueur horizontalement."""
    def __init__(self, x, y, largeur, hauteur):
        super().__init__()
        self.image = pygame.Surface((largeur, hauteur))
        self.image.fill(GRIS_MUR)
        # Brique verticale
        for i in range(0, hauteur, 16):
            pygame.draw.line(self.image, (50, 50, 60), (0, i), (largeur, i), 1)
        self.rect = self.image.get_rect(topleft=(x, y))


class BordureHaute(pygame.sprite.Sprite):
    """
    Bordure haute — premier obstacle de la zone A.
    Trop haute pour passer sans sauter.
    Enseigne le saut implicitement.
    """
    def __init__(self, x, y):
        super().__init__()
        # 3 tuiles de haut, 2 de large
        w, h = TAILLE_TUILE * 2, TAILLE_TUILE * 3
        self.image = pygame.Surface((w, h))
        self.image.fill(GRIS_MUR)
        # Détails visuels — béton urbain
        for i in range(0, h, 16):
            pygame.draw.line(self.image, (55, 55, 65), (0, i), (w, i), 1)
        pygame.draw.rect(self.image, (80, 80, 90), (0, 0, w, 4))
        self.rect = self.image.get_rect(topleft=(x, y))


class Checkpoint(pygame.sprite.Sprite):
    """
    Point de sauvegarde S — clignote doucement.
    Arnaud se sauvegarde en le touchant.
    """
    def __init__(self, x, y):
        super().__init__()
        self.rect      = pygame.Rect(x, y, TAILLE_TUILE, TAILLE_TUILE * 2)
        self.active    = False
        self.timer     = 0   # pour l'animation de clignotement

    def update(self):
        self.timer = (self.timer + 1) % 60

    def draw(self, ecran, offset_x, offset_y):
        """Dessine le checkpoint avec animation pulse."""
        x = self.rect.x + offset_x
        y = self.rect.y + offset_y

        # Poteau
        pygame.draw.rect(ecran, (60, 60, 70), (x + 14, y + 16, 4, 48))

        # Drapeau — pulse entre vert actif et gris inactif
        if self.active:
            import math
            pulse = int(180 + 75 * math.sin(self.timer * 0.2))
            couleur = (0, pulse, 80)
        else:
            couleur = (80, 80, 90)

        pygame.draw.polygon(ecran, couleur, [
            (x + 18, y + 16),
            (x + 18, y + 36),
            (x + 36, y + 26),
        ])


# ============================================================
#  ENNEMIS
# ============================================================

class EnnemBasique(pygame.sprite.Sprite):
    """
    Ennemi de mêlée simple — patrouille sur sa plateforme.
    Contact → dégâts. Se tue en 1 coup (pour le tutoriel).
    """
    PV          = 1
    DEGATS      = 1
    VITESSE     = 1
    DETECTION   = 120   # pixels

    def __init__(self, x, y, limite_gauche, limite_droite):
        super().__init__()
        self.rect         = pygame.Rect(x, y, 24, 32)
        self.hitbox       = self.rect.inflate(-4, 0)
        self.pv           = self.PV
        self.lim_g        = limite_gauche
        self.lim_d        = limite_droite
        self.direction    = -1   # commence par aller à gauche
        self.cooldown_atk = 0
        self.image        = self._dessiner()

    def _dessiner(self, touche=False):
        surf = pygame.Surface((24, 32), pygame.SRCALPHA)
        c = (255, 80, 80) if touche else (180, 40, 40)
        pygame.draw.rect(surf, c,           (4, 10, 16, 16))  # corps
        pygame.draw.rect(surf, (200,130,80),(6,  2, 12, 10))  # tête
        pygame.draw.rect(surf, (20, 20, 20),(4, 26,  6,  6))  # jambe g
        pygame.draw.rect(surf, (20, 20, 20),(14,26,  6,  6))  # jambe d
        # Yeux menaçants
        pygame.draw.rect(surf, BLANC, (8,  5, 3, 3))
        pygame.draw.rect(surf, BLANC, (14, 5, 3, 3))
        pygame.draw.rect(surf, NOIR,  (9,  6, 2, 2))
        pygame.draw.rect(surf, NOIR,  (15, 6, 2, 2))
        # Sourcils froncés
        pygame.draw.line(surf, NOIR, (7, 4), (10, 5), 2)
        pygame.draw.line(surf, (20,20,20), (14, 5), (17, 4), 2)
        return surf

    def update(self, joueur, plateformes):
        # Patrouille
        self.rect.x += self.direction * self.VITESSE
        if self.rect.left < self.lim_g:
            self.rect.left = self.lim_g
            self.direction = 1
        if self.rect.right > self.lim_d:
            self.rect.right = self.lim_d
            self.direction = -1

        # Détection du joueur → charge vers lui
        dx = joueur.rect.centerx - self.rect.centerx
        if abs(dx) < self.DETECTION:
            self.direction = 1 if dx > 0 else -1

        # Dégâts au contact
        if self.cooldown_atk == 0 and self.rect.colliderect(joueur.hitbox):
            joueur.recevoir_degats(self.DEGATS)
            self.cooldown_atk = 90

        if self.cooldown_atk > 0:
            self.cooldown_atk -= 1

        self.hitbox.center = self.rect.center

    def recevoir_degats(self, degats):
        self.pv -= degats
        self.image = self._dessiner(touche=True)

    def est_mort(self):
        return self.pv <= 0


class Tourelle(pygame.sprite.Sprite):
    """
    Tourelle fixe — tire un missile toutes les 1.5 secondes.
    Enseigne l'esquive grâce au timing régulier et prévisible.
    """
    INTERVALLE = 90   # frames = 1.5 secondes à 60 FPS

    def __init__(self, x, y, direction=-1):
        super().__init__()
        self.rect      = pygame.Rect(x, y, TAILLE_TUILE, TAILLE_TUILE)
        self.direction = direction   # -1 = tire à gauche, 1 = tire à droite
        self.timer     = 0
        self.pv        = 3           # plus résistante que l'ennemi basique
        self.image     = self._dessiner()

    def _dessiner(self, alerte=False):
        surf = pygame.Surface((TAILLE_TUILE, TAILLE_TUILE), pygame.SRCALPHA)
        # Corps de la tourelle
        couleur = (200, 100, 20) if alerte else (100, 100, 120)
        pygame.draw.rect(surf, couleur,     (4, 8, 24, 20))
        pygame.draw.rect(surf, (60, 60, 70),(4, 4,  24,  6))  # toit
        # Canon pointé dans la direction
        cx = 0 if self.direction < 0 else 24
        pygame.draw.rect(surf, (50, 50, 60), (cx, 14, 8, 6))
        # Voyant clignotant
        v = (220, 80, 40) if alerte else (60, 200, 60)
        pygame.draw.circle(surf, v, (16, 6), 4)
        return surf

    def update(self):
        self.timer += 1
        # Alerte visuelle 20 frames avant le tir
        alerte = self.timer > (self.INTERVALLE - 20)
        self.image = self._dessiner(alerte)

    def pret_a_tirer(self):
        if self.timer >= self.INTERVALLE:
            self.timer = 0
            return True
        return False

    def recevoir_degats(self, degats):
        self.pv -= degats

    def est_morte(self):
        return self.pv <= 0


class MissileTourelle(pygame.sprite.Sprite):
    """Projectile tiré par la tourelle."""
    VITESSE = 5
    DEGATS  = 1

    def __init__(self, x, y, direction):
        super().__init__()
        self.rect      = pygame.Rect(x, y, 12, 6)
        self.direction = direction
        self.image     = self._dessiner()

    def _dessiner(self):
        surf = pygame.Surface((12, 6), pygame.SRCALPHA)
        pygame.draw.rect(surf, (220, 140, 30), (0, 1, 10, 4))  # corps
        pygame.draw.rect(surf, (255, 220, 80), (8, 0, 4, 6))   # pointe
        return surf

    def update(self, murs, limite_gauche, limite_droite):
        self.rect.x += self.direction * self.VITESSE
        # Disparaît si hors zone ou touche un mur
        if self.rect.right < limite_gauche or self.rect.left > limite_droite:
            self.kill()
        for mur in murs:
            if self.rect.colliderect(mur.rect):
                self.kill()


# ============================================================
#  LEGO (collectible)
# ============================================================

class Lego(pygame.sprite.Sprite):
    """
    Brique Légo collectible cachée dans la zone secrète.
    Augmente les dégâts d'Arnaud quand ramassée.
    """
    def __init__(self, x, y, couleur_idx=0):
        super().__init__()
        from settings import COULEURS_LEGO
        self.couleur_idx = couleur_idx
        couleur = COULEURS_LEGO[couleur_idx % len(COULEURS_LEGO)]
        if couleur is None:
            couleur = (255, 100, 255)  # multicolore → magenta par défaut
        self.image = self._dessiner(couleur)
        self.rect  = self.image.get_rect(topleft=(x, y))
        self.timer = 0   # pour l'animation de flottement

    def _dessiner(self, couleur):
        surf = pygame.Surface((16, 16), pygame.SRCALPHA)
        # Corps de la brique
        pygame.draw.rect(surf, couleur, (0, 4, 16, 12))
        # Plots sur le dessus (style Légo)
        sombre = (max(couleur[0]-50,0), max(couleur[1]-50,0), max(couleur[2]-50,0))
        pygame.draw.rect(surf, sombre, (0, 0, 16, 4))
        pygame.draw.circle(surf, sombre, (5, 4), 3)
        pygame.draw.circle(surf, sombre, (11, 4), 3)
        return surf

    def update(self):
        import math
        # Flottement vertical léger
        self.timer += 1
        self.rect.y += int(math.sin(self.timer * 0.1) * 0.5)


# ============================================================
#  ZONE A — assemblage complet
# ============================================================

class ZoneA:
    """
    Zone A : tutoriel implicite.

    Layout (vue de côté, → = droite, joueur part du bas à droite) :

    SPAWN (droite) → bordure haute → ennemi basique → tourelle → sortie (gauche)

    Détail vertical :
    - Sol principal tout en bas
    - Plateforme haute à gauche (zone secrète avec Légo)
    - Puits central (tombe pour apprendre la chute)

    Largeur totale : 60 tuiles × 32 = 1920 px
    Hauteur totale : 20 tuiles × 32 = 640 px
    """

    LARGEUR_MONDE = 60 * TAILLE_TUILE   # 1920 px
    HAUTEUR_MONDE = 20 * TAILLE_TUILE   # 640 px

    def __init__(self):
        # Groupes de sprites
        self.plateformes  = pygame.sprite.Group()
        self.murs         = pygame.sprite.Group()
        self.ennemis      = pygame.sprite.Group()
        self.tourelles    = pygame.sprite.Group()
        self.missiles     = pygame.sprite.Group()
        self.legos        = pygame.sprite.Group()
        self.checkpoints  = []

        self._construire()


    def _t(self, col, ligne):
        """Convertit col/ligne en pixels."""
        return col * TAILLE_TUILE, ligne * TAILLE_TUILE

    def _construire(self):
        T = TAILLE_TUILE
        W = self.LARGEUR_MONDE
        H = self.HAUTEUR_MONDE

        # ── SOL PRINCIPAL
        Plateforme(0, H - T*2, W, T*2).add(self.plateformes)

        # ── PLAFOND
        Plateforme(0, 0, W, T*2, GRIS_MUR).add(self.plateformes)

        # ── MUR GAUCHE (ferme)
        Mur(0, 0, T*2, H).add(self.murs)

        # ── MUR DROIT avec ouverture pour la porte
        Mur(W - T*2, 0, T*2, H - T*4).add(self.murs)

        # ── SPAWNS
        self.spawns = {
            "defaut" : (T*3, H - T*3),
            "gauche" : (T*3, H - T*3),
            "droite" : (W - T*5, H - T*3),
            "depuis_z1" : (W - T*5, H - T*3),
        }

        # ── BORDURE HAUTE - apprend le SAUT
        bx = T * 8
        by = H - T*2 - T*3
        BordureHaute(bx, by).add(self.murs)

        # ── PLATEFORME INTERMEDIAIRE
        Plateforme(T*12, H - T*6, T*6, T).add(self.plateformes)

        # ── ENNEMI BASIQUE - apprend ATK
        EnnemBasique(T*14, H - T*6 - 32, T*12, T*18).add(self.ennemis)

        # ── PLATEFORME AVANT TOURELLE
        Plateforme(T*20, H - T*2, T*10, T*2).add(self.plateformes)

        # ── TOURELLE - apprend ESQUIVE
        Tourelle(T*22, H - T*2 - T, direction=-1).add(self.tourelles)

        # ── CHECKPOINT
        # checkpoint supprimé — le drapeau sera dans les zones save

        # ── ZONE SECRETE
        Plateforme(T*26, H - T*10, T*6, T).add(self.plateformes)
        Lego(T*28, H - T*11, couleur_idx=0).add(self.legos)

        # ── PORTE DROITE vers Zone 1
        self.sorties = [{
            "rect"        : pygame.Rect(W - T*2, H - T*4, T*2, T*4),
            "destination" : "zone_1",
            "spawn"       : "gauche",
        }]

    # ──────────────────────────────────────────────────────────
    #  UPDATE
    # ──────────────────────────────────────────────────────────
    def update(self, joueur):
        # Ennemis
        for ennemi in list(self.ennemis):
            ennemi.update(joueur, self.plateformes.sprites())
            if ennemi.est_mort():
                ennemi.kill()

        # Tourelles
        for tourelle in list(self.tourelles):
            tourelle.update()
            if tourelle.pret_a_tirer():
                m = MissileTourelle(
                    tourelle.rect.centerx,
                    tourelle.rect.centery,
                    tourelle.direction
                )
                self.missiles.add(m)
            if tourelle.est_morte():
                tourelle.kill()

        # Missiles
        for missile in list(self.missiles):
            missile.update(
                self.murs.sprites(),
                0,
                self.LARGEUR_MONDE
            )
            # Touche le joueur
            if missile.rect.colliderect(joueur.hitbox):
                joueur.recevoir_degats(MissileTourelle.DEGATS)
                missile.kill()

        # Légos
        self.legos.update()

        # Checkpoints
        for cp in self.checkpoints:
            cp.update()
            if joueur.rect.colliderect(cp.rect) and not cp.active:
                cp.active = True   # sauvegarde (géré dans main.py)

        # Attaque du joueur → ennemis et tourelles
        zone_atk = joueur.get_zone_attaque()
        if zone_atk:
            for ennemi in list(self.ennemis):
                if zone_atk.colliderect(ennemi.rect):
                    ennemi.recevoir_degats(joueur.degats)
                    joueur.appliquer_recul(ennemi)
            for tourelle in list(self.tourelles):
                if zone_atk.colliderect(tourelle.rect):
                    tourelle.recevoir_degats(joueur.degats)

        # Joueur ramasse un Légo
        for lego in list(self.legos):
            if joueur.rect.colliderect(lego.rect):
                joueur.collecter_lego()
                lego.kill()

    # ──────────────────────────────────────────────────────────
    #  DESSIN
    # ──────────────────────────────────────────────────────────
    def dessiner(self, ecran, camera_x, camera_y):
        ox, oy = camera_x, camera_y   # offset caméra

        # Sol et plateformes
        for sprite in self.plateformes:
            ecran.blit(sprite.image, (sprite.rect.x + ox, sprite.rect.y + oy))

        # Murs
        for sprite in self.murs:
            ecran.blit(sprite.image, (sprite.rect.x + ox, sprite.rect.y + oy))

        # Checkpoints
        for cp in self.checkpoints:
            cp.draw(ecran, ox, oy)

        # Tourelles
        for t in self.tourelles:
            ecran.blit(t.image, (t.rect.x + ox, t.rect.y + oy))

        # Missiles
        for m in self.missiles:
            ecran.blit(m.image, (m.rect.x + ox, m.rect.y + oy))

        # Ennemis
        for e in self.ennemis:
            ecran.blit(e.image, (e.rect.x + ox, e.rect.y + oy))

        # Légos
        for l in self.legos:
            ecran.blit(l.image, (l.rect.x + ox, l.rect.y + oy))

        # Zone secrète — hachures légères pour indiquer visuellement
        self._dessiner_zone_secrete(ecran, ox, oy)

    def _dessiner_zone_secrete(self, ecran, ox, oy):
        """Hachures discrètes sur la plateforme secrète."""
        T = TAILLE_TUILE
        H = self.HAUTEUR_MONDE
        x = T * 5 + ox
        y = H - T * 10 + oy
        w, h = T * 8, T * 2
        for i in range(0, w + h, 12):
            x1 = max(x, x + i - h)
            y1 = min(y + h, y + i)
            x2 = min(x + w, x + i)
            y2 = max(y, y + i - w)
            pygame.draw.line(ecran, (50, 50, 65), (x1, y1), (x2, y2), 1)
