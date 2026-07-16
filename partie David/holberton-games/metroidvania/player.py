# ============================================================
#  ARNAUD METROIDVANIA — player.py
#
#  Moteur physique complet :
#    - Gravité réaliste
#    - Saut + double saut (débloquable)
#    - Esquive (dash) avec invincibilité
#    - Accroupissement (passe sous les obstacles)
#    - Attaque épée directionnelle
# ============================================================

import pygame
from settings import *


class Arnaud(pygame.sprite.Sprite):

    def __init__(self, x, y):
        super().__init__()

        # --- Taille normale et accroupi ---
        self.taille_normale   = (28, 48)
        self.taille_accroupi  = (28, 28)

        self.rect   = pygame.Rect(x, y, 28, 48)
        self.hitbox = pygame.Rect(x + 2, y, 24, 48)   # hitbox fine

        # ── Physique ──────────────────────────────────────────
        self.vel_x = 0       # vitesse horizontale
        self.vel_y = 0       # vitesse verticale (+ = vers le bas)
        self.au_sol = False  # True si Arnaud touche un sol
        self.au_sol_precedent = False  # buffer pour coyote time
        self.respawn_demande  = False  # True = perte de vie simple (pas game over)
        self.saut_demande = False  # flag anti re-saut

        # ── État ──────────────────────────────────────────────
        self.face_a_droite  = True
        self.accroupi       = False

        # ── Sauts ─────────────────────────────────────────────
        # sauts_restants : 1 = un saut dispo, 0 = plus de saut
        # Le double saut ajoute +1 saut supplémentaire en l'air
        self.sauts_max       = 1   # 1 = saut simple, 2 = double saut
        self.sauts_restants  = 1
        self.a_double_saut   = False

        # ── Esquive ───────────────────────────────────────────
        self.en_esquive          = False
        self.timer_esquive       = 0     # frames restantes d'esquive active
        self.cooldown_esquive    = 0     # frames avant prochain esquive dispo
        self.dir_esquive         = 1     # direction au moment du déclenchement
        self.invincible_esquive  = False # pendant l'esquive = invincible

        # ── Combat ────────────────────────────────────────────
        self.degats          = DEGATS_BASE
        self.timer_attaque   = 0         # frames d'animation d'attaque
        self.cooldown_attaque = 0
        self.dir_attaque     = (1, 0)    # direction du coup

        # ── Stats ─────────────────────────────────────────────
        self.vies            = VIES_MAX
        self.coeurs          = COEURS_MAX
        self.coeurs_max      = COEURS_MAX
        self.missiles        = MISSILES_DEPART
        self.missiles_max    = MISSILES_DEPART
        self.legos_collectes = 0

        # ── Invincibilité après dégâts ────────────────────────
        self.cooldown_invincible = 0

        # ── Capacités débloquées ──────────────────────────────
        self.capacites = {
            "double_saut"  : False,
            "glissade"     : False,
            "lego_sword"   : False,
            "lego_blast"   : False,
            "brise_mur"    : False,
            "missiles"     : False,
        }

        # Dessin initial — doit être en dernier car _dessiner lit self.cooldown_invincible
        self.image = self._dessiner(False, False, None)

    # ==========================================================
    #  UPDATE — appelé 60x/seconde depuis main.py
    # ==========================================================
    def update(self, touches, plateformes, murs):
        self._gerer_input(touches)
        self._appliquer_gravite()
        self._deplacer(plateformes, murs)
        self._mettre_a_jour_timers()
        self.image = self._dessiner(
            self.accroupi,
            self.en_esquive,
            self.dir_attaque if self.timer_attaque > 0 else None
        )

    # ==========================================================
    #  INPUT
    # ==========================================================
    def _gerer_input(self, touches):
        # Pas d'input pendant une esquive active
        if self.en_esquive:
            return

        # --- Mouvement horizontal ---
        if touches[pygame.K_RIGHT] or touches[pygame.K_d]:
            self.vel_x      = VITESSE_JOUEUR
            self.face_a_droite = True
        elif touches[pygame.K_LEFT] or touches[pygame.K_q]:
            self.vel_x      = -VITESSE_JOUEUR
            self.face_a_droite = False
        else:
            # Friction — arrêt rapide au sol, glissement léger en l'air
            self.vel_x = int(self.vel_x * (0.6 if self.au_sol else 0.85))

        # --- Accroupissement ---
        accroupi_demande = touches[pygame.K_DOWN] or touches[pygame.K_s]
        if accroupi_demande and self.au_sol:
            self._s_accroupir()
        elif not accroupi_demande and self.accroupi:
            self._se_relever()

        # --- Saut ---
        saut_touche = touches[pygame.K_z] or touches[pygame.K_UP] or touches[pygame.K_SPACE]
        if saut_touche and self.au_sol and not self.accroupi and self.sauts_restants > 0:
            self.vel_y = FORCE_SAUT
            self.au_sol = False
            self.sauts_restants -= 1

        # --- Attaque ---
        if (touches[pygame.K_x] or touches[pygame.K_k]) and self.cooldown_attaque == 0:
            self._declencher_attaque()

    def trigger_saut(self):
        """
        Appelée sur KEYDOWN seulement (pas sur maintien).
        - Au sol          → saut normal (toujours dispo, inné)
        - En l'air        → double saut si débloqué ET pas encore utilisé
        """
        if self.accroupi:
            return

        if self.au_sol:
            # Saut depuis le sol — toujours possible (inné)
            self.vel_y = FORCE_SAUT
            self.au_sol = False
            self.sauts_restants = 1 if self.a_double_saut else 0
            # sauts_restants représente ici les sauts EN L'AIR encore dispo

        elif self.sauts_restants > 0 and self.a_double_saut:
            # Double saut en l'air
            self.vel_y = FORCE_DOUBLE_SAUT
            self.sauts_restants -= 1

    def trigger_esquive(self):
        """Appelée par main.py sur KEYDOWN K_LSHIFT."""
        if self.cooldown_esquive > 0 or self.accroupi:
            return
        self.en_esquive         = True
        self.timer_esquive      = DUREE_ESQUIVE
        self.cooldown_esquive   = COOLDOWN_ESQUIVE
        self.invincible_esquive = True
        self.dir_esquive        = 1 if self.face_a_droite else -1

    # ==========================================================
    #  PHYSIQUE
    # ==========================================================
    def _appliquer_gravite(self):
        if not self.au_sol:
            self.vel_y += GRAVITE
            if self.vel_y > VITESSE_MAX_CHUTE:
                self.vel_y = VITESSE_MAX_CHUTE

    def _deplacer(self, plateformes, murs):
        self.au_sol_precedent = self.au_sol
        # ── Esquive : remplace le mouvement normal ─────────────
        if self.en_esquive:
            self.hitbox.x += int(self.dir_esquive * VITESSE_ESQUIVE)
            self._collision_horizontale(murs)
            # Pendant l'esquive on ignore la gravité (dash horizontal pur)
            self.rect.center = self.hitbox.center
            return

        # ── Horizontal ────────────────────────────────────────
        self.hitbox.x += int(self.vel_x)
        self._collision_horizontale(murs)

        # ── Vertical ──────────────────────────────────────────
        self.au_sol = False
        self.hitbox.y += int(self.vel_y)
        self._collision_verticale(plateformes + murs)

        self.rect.center = self.hitbox.center

    def _collision_horizontale(self, murs):
        for mur in murs:
            if self.hitbox.colliderect(mur.rect):
                if self.vel_x > 0 or (self.en_esquive and self.dir_esquive > 0):
                    self.hitbox.right = mur.rect.left
                else:
                    self.hitbox.left  = mur.rect.right
                self.vel_x = 0
                if self.en_esquive:
                    self._stopper_esquive()

    def _collision_verticale(self, solides):
        self.au_sol = False
        for sol in solides:
            if self.hitbox.colliderect(sol.rect):
                if self.vel_y > 0:   # tombe → atterrit
                    self.hitbox.bottom = sol.rect.top
                    self.vel_y  = 0
                    self.au_sol = True
                    self.sauts_restants = self.sauts_max
                    if self.saut_demande:
                        self.saut_demande = False
                        self.vel_y = FORCE_SAUT
                        self.au_sol = False
                elif self.vel_y < 0: # monte → tape un plafond
                    self.hitbox.top = sol.rect.bottom
                    self.vel_y = 0

    # ==========================================================
    #  ACCROUPISSEMENT
    # ==========================================================
    def _s_accroupir(self):
        if self.accroupi:
            return
        self.accroupi = True
        # Rétrécit la hitbox par le haut, les pieds restent en place
        ancien_bas = self.hitbox.bottom
        self.hitbox.height = 28
        self.hitbox.bottom = ancien_bas
        # Sync rect
        self.rect.size   = (32, 28)
        self.rect.bottom = self.hitbox.bottom

    def _se_relever(self):
        if not self.accroupi:
            return
        # Vérifie qu'il y a de la place au-dessus avant de se relever
        self.accroupi = False
        ancien_bas = self.hitbox.bottom
        self.hitbox.height = 48
        self.hitbox.bottom = ancien_bas
        self.hitbox.x = self.rect.x + 2
        # Sync rect
        self.rect.size   = (32, 48)
        self.rect.bottom = self.hitbox.bottom

    # ==========================================================
    #  ATTAQUE
    # ==========================================================
    def _declencher_attaque(self):
        self.timer_attaque    = 15
        self.cooldown_attaque = 25
        self.dir_attaque = (1 if self.face_a_droite else -1, 0)

    def trigger_lego_blast(self):
        """
        Tire un projectile Légo Blast.
        Retourne un dict avec les infos du projectile, géré dans main.py.
        """
        if not self.capacites["lego_blast"]:
            return None
        dx = 1 if self.face_a_droite else -1
        return {
            "x"    : self.rect.centerx + dx * 20,
            "y"    : self.rect.centery,
            "dx"   : dx,
            "degats": DEGATS_LEGO_BLAST * self.degats,
        }

    def get_zone_attaque(self):
        """Retourne le Rect de la zone d'attaque, ou None si pas en train d'attaquer."""
        if self.timer_attaque <= 0:
            return None
        dx, dy = self.dir_attaque
        zone = pygame.Rect(0, 0, PORTEE_EPEE, 32)
        zone.centery = self.hitbox.centery
        if dx > 0:
            zone.left = self.hitbox.right
        else:
            zone.right = self.hitbox.left
        return zone

    # ==========================================================
    #  DÉGÂTS REÇUS
    # ==========================================================
    def recevoir_degats(self, degats):
        if self.cooldown_invincible > 0 or self.invincible_esquive:
            return
        self.coeurs -= degats
        if self.coeurs <= 0:
            self.coeurs = 0
            self._perdre_une_vie()
        self.cooldown_invincible = COOLDOWN_INVINCIBLE

    def _perdre_une_vie(self):
        self.vies -= 1
        self.respawn_demande = False
        if self.vies > 0:
            self.coeurs = self.coeurs_max  # recharge les cœurs pour la prochaine vie
            self.respawn_demande = True   # respawn au checkpoint, pas game over

    def est_mort(self):
        return self.vies <= 0

    # ==========================================================
    #  PROGRESSION — légos et dégâts
    # ==========================================================
    def collecter_lego(self):
        self.legos_collectes += 1
        self._recalculer_degats()

    def _recalculer_degats(self):
        """
        +0.25 dégâts tous les 2 légos collectés.
        Cap à DEGATS_BASE + DEGATS_MAX_BONUS si 8 légos cachés collectés.
        """
        bonus = (self.legos_collectes // 2) * 0.25
        base  = DEGATS_LEGO_SWORD_BASE if self.capacites["lego_sword"] else DEGATS_BASE
        self.degats = min(base + bonus, DEGATS_BASE + DEGATS_MAX_BONUS)

    def debloquer(self, capacite):
        """Débloque une capacité. Appelée quand le joueur ramasse un power-up."""
        if capacite in self.capacites:
            self.capacites[capacite] = True
            if capacite == "double_saut":
                self.a_double_saut = True
                self.sauts_max = 2
                self.sauts_restants = 2
            elif capacite == "missiles":
                self.missiles_max = MISSILES_MAX

    # ==========================================================
    #  TIMERS
    # ==========================================================
    def _mettre_a_jour_timers(self):
        if self.timer_esquive > 0:
            self.timer_esquive -= 1
            if self.timer_esquive == 0:
                self._stopper_esquive()

        if self.cooldown_esquive    > 0: self.cooldown_esquive    -= 1
        if self.cooldown_attaque    > 0: self.cooldown_attaque    -= 1
        if self.timer_attaque       > 0: self.timer_attaque       -= 1
        if self.cooldown_invincible > 0: self.cooldown_invincible -= 1

    def _stopper_esquive(self):
        self.en_esquive         = False
        self.timer_esquive      = 0
        # L'invincibilité reste encore quelques frames après l'esquive
        # pour couvrir la fin du déplacement (évite le hit au dernier pixel)
        if self.invincible_esquive:
            self.cooldown_invincible = max(self.cooldown_invincible, 8)
        self.invincible_esquive = False

    def appliquer_recul(self, cible, force=5):
        """
        Donne un recul à une cible (ennemi) dans la direction de l'attaque.
        Appelée depuis main.py quand un coup touche.
        """
        dx = self.dir_attaque[0]
        cible.rect.x += dx * force
        if hasattr(cible, 'hitbox'):
            cible.hitbox.x += dx * force

    # ==========================================================
    #  DESSIN PIXEL ART
    # ==========================================================
    def _dessiner(self, accroupi, en_esquive, dir_attaque):
        h = 28 if accroupi else 48
        surf = pygame.Surface((32, h), pygame.SRCALPHA)

        # Couleur selon état
        if en_esquive:
            alpha = 160
        elif self.cooldown_invincible > 0 and self.cooldown_invincible % 6 < 3:
            alpha = 80
        else:
            alpha = 255

        skin  = COULEUR_ARNAUD_SKIN
        habit = COULEUR_ARNAUD  # blanc/clair

        if accroupi:
            # Version accroupie — plus basse
            pygame.draw.rect(surf, habit, (6, 8, 20, 14))   # corps
            pygame.draw.rect(surf, skin,  (10, 0, 10,  10)) # tête
            pygame.draw.rect(surf, BLANC, (10, 0, 10,   4)) # cheveux blancs
            pygame.draw.rect(surf, (30, 30, 30), (6, 22, 8, 6))   # jambe g
            pygame.draw.rect(surf, (30, 30, 30), (18, 22, 8, 6))  # jambe d
        else:
            # Version debout
            pygame.draw.rect(surf, habit, (8, 18, 16, 18))   # corps
            pygame.draw.rect(surf, skin,  (10, 6,  12, 13))  # tête
            pygame.draw.rect(surf, BLANC, (9,  4,  14,  6))  # cheveux blancs
            pygame.draw.rect(surf, (30, 30, 30), (8, 36, 6, 12))  # jambe g
            pygame.draw.rect(surf, (30, 30, 30), (18, 36, 6, 12)) # jambe d
            pygame.draw.rect(surf, habit, (2, 18,  8, 10))   # bras g
            pygame.draw.rect(surf, habit, (22, 18, 8, 10))   # bras d

        # Yeux
        ey = 4 if accroupi else 11
        pygame.draw.rect(surf, NOIR, (12, ey, 2, 2))
        pygame.draw.rect(surf, NOIR, (18, ey, 2, 2))

        # Épée (si attaque)
        if dir_attaque is not None:
            dx = dir_attaque[0]
            ey2 = 14 if accroupi else 22
            if dx > 0:
                pygame.draw.rect(surf, (200, 200, 220), (26, ey2, 16, 4))  # épée droite
                pygame.draw.rect(surf, (220, 220, 100), (38, ey2-2, 4, 8)) # pointe
            else:
                pygame.draw.rect(surf, (200, 200, 220), (-10, ey2, 16, 4)) # épée gauche
                pygame.draw.rect(surf, (220, 220, 100), (-10, ey2-2, 4, 8))

        surf.set_alpha(alpha)
        return surf

    # ==========================================================
    #  UI — dessin des cœurs, vies, missiles
    # ==========================================================
    def dessiner_ui(self, ecran):
        self._dessiner_coeurs(ecran)
        self._dessiner_vies(ecran)
        if self.capacites["missiles"]:
            self._dessiner_missiles(ecran)

    def _dessiner_coeurs(self, ecran):
        for i in range(self.coeurs_max):
            c = COULEUR_COEUR_PLEIN if i < self.coeurs else COULEUR_COEUR_VIDE
            x = 16 + i * 22
            self._coeur(ecran, x, 16, c, 3)

    def _dessiner_vies(self, ecran):
        police = pygame.font.SysFont("monospace", 16, bold=True)
        txt = police.render(f"Vies : {self.vies}", True, COULEUR_VIE_PLEIN)
        ecran.blit(txt, (16, 46))

    def _dessiner_missiles(self, ecran):
        police = pygame.font.SysFont("monospace", 16, bold=True)
        txt = police.render(f"M : {self.missiles}/{self.missiles_max}", True, COULEUR_MISSILE)
        ecran.blit(txt, (16, 66))

    def _coeur(self, ecran, x, y, couleur, taille):
        pixels = [
            (1,0),(2,0),(4,0),(5,0),
            (0,1),(1,1),(2,1),(3,1),(4,1),(5,1),(6,1),
            (0,2),(1,2),(2,2),(3,2),(4,2),(5,2),(6,2),
            (1,3),(2,3),(3,3),(4,3),(5,3),
            (2,4),(3,4),(4,4),
            (3,5),
        ]
        for px, py in pixels:
            pygame.draw.rect(ecran, couleur,
                             (x + px*taille, y + py*taille, taille, taille))
