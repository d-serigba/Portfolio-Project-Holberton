# ============================================================
#  ARNO'S BIZARRE ADVENTURE — player.py
#  Gère tout ce qui concerne Arno : mouvement, combat, vie
# ============================================================

import pygame
from settings import *


class Joueur(pygame.sprite.Sprite):
    """
    Le personnage principal : Arno.

    Attributs importants :
        rect        — position et taille dans le monde
        pv          — points de vie actuels
        direction   — vecteur de déplacement (pygame.math.Vector2)
        attaque_active — True pendant le frame d'attaque
    """

    def __init__(self, x, y):
        super().__init__()

        # --- Sprite visuel (dessiné en pixel art via du code) ---
        self.image_normale = self._dessiner_arno(False)
        self.image_attaque = self._dessiner_arno(True)
        self.image = self.image_normale

        # --- Position ---
        self.rect = self.image.get_rect(topleft=(x, y))
        self.hitbox = self.rect.inflate(-8, -8)   # hitbox plus petite que le sprite

        # --- Mouvement ---
        self.direction    = pygame.math.Vector2(0, 0)
        self.derniere_dir = pygame.math.Vector2(0, 1)   # regarde vers le bas par défaut

        # --- Combat ---
        self.pv              = PV_JOUEUR_MAX
        self.pv_max          = PV_JOUEUR_MAX
        self.attaque_active  = False
        self.cooldown_attaque    = 0    # compteur frames avant prochaine attaque
        self.cooldown_invincible = 0    # compteur frames d'invincibilité

        # --- Animation ---
        self.timer_attaque = 0          # frames d'affichage du sprite attaque

    # ----------------------------------------------------------
    #  DESSIN DU SPRITE EN PIXEL ART (sans image externe)
    # ----------------------------------------------------------
    def _dessiner_arno(self, en_attaque=False):
        """Dessine Arno pixel par pixel — style banlieue."""
        surf = pygame.Surface((32, 32), pygame.SRCALPHA)

        # Corps — veste bleue
        couleur_veste = (255, 200, 0) if en_attaque else COULEUR_ARNO
        pygame.draw.rect(surf, couleur_veste,       (8, 14, 16, 14))   # corps
        pygame.draw.rect(surf, COULEUR_ARNO_SKIN,   (11, 6, 10, 10))   # tête
        pygame.draw.rect(surf, (20, 20, 20),         (8, 28,  6,  4))  # jambe gauche
        pygame.draw.rect(surf, (20, 20, 20),         (18, 28, 6,  4))  # jambe droite
        pygame.draw.rect(surf, (15, 70, 140),        (8, 14,  4, 10))  # bras gauche
        pygame.draw.rect(surf, (15, 70, 140),        (20, 14, 4, 10))  # bras droit

        # Yeux
        pygame.draw.rect(surf, NOIR, (13, 10, 2, 2))
        pygame.draw.rect(surf, NOIR, (17, 10, 2, 2))

        # Casquette
        pygame.draw.rect(surf, (20, 20, 20), (9, 4, 14, 4))
        pygame.draw.rect(surf, (20, 20, 20), (7, 6, 4,  2))  # visière

        if en_attaque:
            # Bras tendu vers la droite
            pygame.draw.rect(surf, (15, 70, 140), (24, 14, 6, 4))
            # Flash autour du poing
            pygame.draw.rect(surf, COULEUR_ATTAQUE, (28, 12, 4, 8))

        return surf

    # ----------------------------------------------------------
    #  MISE À JOUR — appelée chaque frame
    # ----------------------------------------------------------
    def update(self, touches, obstacles, ennemis):
        self._gerer_input(touches)
        self._deplacer(obstacles)
        self._gerer_attaque(touches, ennemis)
        self._mettre_a_jour_cooldowns()
        self._mettre_a_jour_sprite()

    # ----------------------------------------------------------
    #  INPUT CLAVIER
    # ----------------------------------------------------------
    def _gerer_input(self, touches):
        self.direction.x = 0
        self.direction.y = 0

        if touches[pygame.K_LEFT]  or touches[pygame.K_q]:
            self.direction.x = -1
            self.derniere_dir = pygame.math.Vector2(-1, 0)
        if touches[pygame.K_RIGHT] or touches[pygame.K_d]:
            self.direction.x = 1
            self.derniere_dir = pygame.math.Vector2(1, 0)
        if touches[pygame.K_UP]    or touches[pygame.K_z]:
            self.direction.y = -1
            self.derniere_dir = pygame.math.Vector2(0, -1)
        if touches[pygame.K_DOWN]  or touches[pygame.K_s]:
            self.direction.y = 1
            self.derniere_dir = pygame.math.Vector2(0, 1)

        # Normalisation diagonale (évite d'aller plus vite en diagonale)
        if self.direction.length() > 0:
            self.direction = self.direction.normalize()

    # ----------------------------------------------------------
    #  DÉPLACEMENT + COLLISIONS AVEC OBSTACLES
    # ----------------------------------------------------------
    def _deplacer(self, obstacles):
        # Axe X
        self.hitbox.x += int(self.direction.x * VITESSE_JOUEUR)
        self._corriger_collision_x(obstacles)

        # Axe Y
        self.hitbox.y += int(self.direction.y * VITESSE_JOUEUR)
        self._corriger_collision_y(obstacles)

        # Synchronise le rect visuel avec la hitbox
        self.rect.center = self.hitbox.center

    def _corriger_collision_x(self, obstacles):
        for obstacle in obstacles:
            if self.hitbox.colliderect(obstacle.rect):
                if self.direction.x > 0:
                    self.hitbox.right = obstacle.rect.left
                elif self.direction.x < 0:
                    self.hitbox.left = obstacle.rect.right

    def _corriger_collision_y(self, obstacles):
        for obstacle in obstacles:
            if self.hitbox.colliderect(obstacle.rect):
                if self.direction.y > 0:
                    self.hitbox.bottom = obstacle.rect.top
                elif self.direction.y < 0:
                    self.hitbox.top = obstacle.rect.bottom

    # ----------------------------------------------------------
    #  ATTAQUE
    # ----------------------------------------------------------
    def _gerer_attaque(self, touches, ennemis):
        # Déclencher l'attaque avec ESPACE ou J
        if (touches[pygame.K_SPACE] or touches[pygame.K_j]) and self.cooldown_attaque == 0:
            self.attaque_active = True
            self.cooldown_attaque = COOLDOWN_ATTAQUE
            self.timer_attaque   = 15   # durée du sprite attaque en frames
            self._appliquer_degats(ennemis)

    def _appliquer_degats(self, ennemis):
        """Touche les ennemis dans la direction d'Arno."""
        # Zone d'attaque : rectangle devant Arno
        zone = pygame.Rect(0, 0, PORTEE_ATTAQUE, PORTEE_ATTAQUE)
        zone.center = (
            self.rect.centerx + int(self.derniere_dir.x * PORTEE_ATTAQUE),
            self.rect.centery + int(self.derniere_dir.y * PORTEE_ATTAQUE)
        )
        for ennemi in ennemis:
            if zone.colliderect(ennemi.rect) and not ennemi.est_mort():
                ennemi.recevoir_degats(DEGATS_JOUEUR)

    # ----------------------------------------------------------
    #  RECEVOIR DES DÉGÂTS
    # ----------------------------------------------------------
    def recevoir_degats(self, degats):
        """Appelée par les ennemis quand ils touchent Arno."""
        if self.cooldown_invincible == 0:
            self.pv -= degats
            self.cooldown_invincible = COOLDOWN_INVINCIBLE
            if self.pv < 0:
                self.pv = 0

    def est_mort(self):
        return self.pv <= 0

    # ----------------------------------------------------------
    #  COOLDOWNS & SPRITE
    # ----------------------------------------------------------
    def _mettre_a_jour_cooldowns(self):
        if self.cooldown_attaque    > 0: self.cooldown_attaque    -= 1
        if self.cooldown_invincible > 0: self.cooldown_invincible -= 1
        if self.timer_attaque       > 0:
            self.timer_attaque -= 1
        else:
            self.attaque_active = False

    def _mettre_a_jour_sprite(self):
        # Clignotement pendant invincibilité
        if self.cooldown_invincible > 0 and self.cooldown_invincible % 6 < 3:
            self.image = self._dessiner_arno_transparent()
        elif self.attaque_active:
            self.image = self.image_attaque
        else:
            self.image = self.image_normale

    def _dessiner_arno_transparent(self):
        surf = self.image_normale.copy()
        surf.set_alpha(120)
        return surf

    # ----------------------------------------------------------
    #  AFFICHAGE UI — barre de vie
    # ----------------------------------------------------------
    def dessiner_ui(self, ecran):
        """Dessine les cœurs de vie en haut à gauche."""
        for i in range(self.pv_max):
            couleur = COULEUR_PV_PLEIN if i < self.pv else COULEUR_PV_VIDE
            x = 16 + i * 28
            self._dessiner_coeur(ecran, x, 16, couleur)

    def _dessiner_coeur(self, ecran, x, y, couleur):
        """Dessine un cœur pixel art."""
        coeur = [
            (1,0),(2,0),(4,0),(5,0),
            (0,1),(1,1),(2,1),(3,1),(4,1),(5,1),(6,1),
            (0,2),(1,2),(2,2),(3,2),(4,2),(5,2),(6,2),
            (1,3),(2,3),(3,3),(4,3),(5,3),
            (2,4),(3,4),(4,4),
            (3,5),
        ]
        taille = 4
        for px, py in coeur:
            pygame.draw.rect(ecran, couleur, (x + px*taille, y + py*taille, taille, taille))
