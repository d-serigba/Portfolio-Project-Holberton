# ============================================================
#  ARNAUD METROIDVANIA — zone_base.py
#
#  Classe parente de toutes les zones.
#  Gère automatiquement :
#    - Sol et plafond
#    - Murs avec trous aux bons endroits selon les sorties
#    - Spawns au sol selon le côté d'entrée
#    - Bidirectionnalité (retour vers zone précédente)
# ============================================================

import pygame
from settings import *


class ZoneBase:
    """
    Hériter de cette classe pour créer une zone.

    Dans __init__ de la zone fille, définir :
        self.LARGEUR_MONDE = X * TAILLE_TUILE
        self.HAUTEUR_MONDE = Y * TAILLE_TUILE

    Dans _construire() de la zone fille :
        1. Appeler super()._init_groupes()
        2. Définir self.sorties
        3. Ajouter les plateformes internes
        4. Appeler super()._finaliser() EN DERNIER

    Format d'une sortie :
        {
            "cote"       : "gauche" | "droite" | "haut" | "bas",
            "y"          : position y du trou (pour gauche/droite)
            "x"          : position x du trou (pour haut/bas)
            "taille"     : hauteur/largeur du trou en pixels
            "destination": "zone_x",
            "spawn"      : "gauche" | "droite" | "haut" | "bas" | "sol_gauche" | "sol_droite"
        }
    """

    def _init_groupes(self):
        """Initialise les groupes de sprites."""
        self.plateformes = pygame.sprite.Group()
        self.murs        = pygame.sprite.Group()
        self.ennemis     = pygame.sprite.Group()
        self.legos       = pygame.sprite.Group()
        self.checkpoints = []
        self.missiles    = pygame.sprite.Group()
        self.sorties     = []

    def _finaliser(self):
        """
        À appeler EN DERNIER dans _construire().
        Génère : sol, plafond, murs avec trous, spawns au sol.
        """
        T  = TAILLE_TUILE
        W  = self.LARGEUR_MONDE
        H  = self.HAUTEUR_MONDE

        # Sol et plafond
        self._plateforme(0, H - T*2, W, T*2)
        self._plateforme(0, 0, W, T*2, GRIS_MUR)

        # Générer les murs avec trous
        self._generer_mur_gauche(T, W, H)
        self._generer_mur_droite(T, W, H)

        # Spawns automatiques au sol selon le côté
        self.spawns = {
            "defaut"     : (W // 2,    H - T*3),
            "sol_gauche" : (T*3,       H - T*3),
            "sol_droite" : (W - T*4,   H - T*3),
            "gauche"     : (T*3,       H - T*3),   # toujours au sol
            "droite"     : (W - T*4,   H - T*3),   # toujours au sol
            "haut"       : (W // 2,    T*4),
            "bas"        : (W // 2,    H - T*3),
        }

    def _generer_mur_gauche(self, T, W, H):
        """Génère le mur gauche avec les trous pour les sorties gauche."""
        trous = sorted([
            (s["y"], s["y"] + s["taille"])
            for s in self.sorties if s["cote"] == "gauche"
        ])
        self._mur_avec_trous(0, T*2, T*2, H - T*2, trous)

    def _generer_mur_droite(self, T, W, H):
        """Génère le mur droit avec les trous pour les sorties droite."""
        trous = sorted([
            (s["y"], s["y"] + s["taille"])
            for s in self.sorties if s["cote"] == "droite"
        ])
        self._mur_avec_trous(W - T*2, T*2, T*2, H - T*2, trous)

    def _mur_avec_trous(self, x, y_debut, largeur, hauteur_totale, trous):
        """
        Génère un mur vertical avec des trous.
        trous = liste de (y_debut_trou, y_fin_trou)
        """
        y_courant = y_debut
        y_fin     = y_debut + hauteur_totale

        for (trou_debut, trou_fin) in trous:
            # Segment avant le trou
            if trou_debut > y_courant:
                self._mur(x, y_courant, largeur, trou_debut - y_courant)
            y_courant = trou_fin

        # Segment final après le dernier trou
        if y_courant < y_fin:
            self._mur(x, y_courant, largeur, y_fin - y_courant)

    def _sortie_rect(self, sortie):
        """Retourne le pygame.Rect de déclenchement d'une sortie."""
        T = TAILLE_TUILE
        W = self.LARGEUR_MONDE
        H = self.HAUTEUR_MONDE
        cote = sortie["cote"]

        if cote == "gauche":
            return pygame.Rect(0, sortie["y"], T*2, sortie["taille"])
        elif cote == "droite":
            return pygame.Rect(W - T*2, sortie["y"], T*2, sortie["taille"])
        elif cote == "haut":
            return pygame.Rect(sortie["x"], 0, sortie["taille"], T*2)
        elif cote == "bas":
            return pygame.Rect(sortie["x"], H - T*2, sortie["taille"], T*2)

    def ajouter_sortie_retour(self, zone_precedente, cote_retour):
        """
        Ajoute automatiquement une porte de retour.
        Appelée par la Facade quand on entre dans une zone.

        zone_precedente : nom de la zone d'où on vient ("zone_1")
        cote_retour     : côté par lequel on est entré ("gauche" → retour à droite)
        """
        T = TAILLE_TUILE
        W = self.LARGEUR_MONDE
        H = self.HAUTEUR_MONDE

        # Côté opposé = porte de retour
        oppose = {"gauche": "droite", "droite": "gauche",
                  "haut": "bas",      "bas": "haut"}
        cote_porte = oppose.get(cote_retour, "gauche")

        # Vérifier si une sortie vers cette zone existe déjà
        for s in self.sorties:
            if s["destination"] == zone_precedente:
                return   # déjà connecté

        # Position de la porte de retour — au niveau du sol
        if cote_porte in ("gauche", "droite"):
            y_porte = H - T*4
        else:
            y_porte = 0

        self.sorties.append({
            "cote"       : cote_porte,
            "y"          : y_porte,
            "taille"     : T*2,
            "destination": zone_precedente,
            "spawn"      : cote_retour,
        })

        # Régénérer les murs pour intégrer le nouveau trou
        self.murs.empty()
        self._finaliser_murs_seulement()

    def _finaliser_murs_seulement(self):
        """Regénère uniquement les murs (sans toucher sol/plafond/plateformes)."""
        T = TAILLE_TUILE
        W = self.LARGEUR_MONDE
        H = self.HAUTEUR_MONDE
        self._generer_mur_gauche(T, W, H)
        self._generer_mur_droite(T, W, H)

    # ── Helpers dessin ────────────────────────────────────────

    def _plateforme(self, x, y, w, h, couleur=None):
        if couleur is None:
            couleur = GRIS_PLATEFORME
        if w <= 0 or h <= 0:
            return
        s = pygame.sprite.Sprite()
        s.image = pygame.Surface((w, h))
        s.image.fill(couleur)
        pygame.draw.rect(s.image, (
            min(couleur[0]+30, 255),
            min(couleur[1]+30, 255),
            min(couleur[2]+30, 255)
        ), (0, 0, w, 4))
        s.rect = s.image.get_rect(topleft=(x, y))
        self.plateformes.add(s)

    def _mur(self, x, y, w, h):
        if w <= 0 or h <= 0:
            return
        s = pygame.sprite.Sprite()
        s.image = pygame.Surface((w, h))
        s.image.fill(GRIS_MUR)
        for i in range(0, h, 16):
            pygame.draw.line(s.image, (50, 50, 60), (0, i), (w, i), 1)
        s.rect = s.image.get_rect(topleft=(x, y))
        self.murs.add(s)

    # ── Update et dessin ──────────────────────────────────────

    def update(self, joueur):
        # Vérifier les sorties
        for sortie in self.sorties:
            rect = self._sortie_rect(sortie)
            if rect and joueur.rect.colliderect(rect):
                return sortie   # la Facade gère la transition
        return None

    def dessiner(self, ecran, cam_x, cam_y):
        for groupe in [self.plateformes, self.murs, self.ennemis, self.legos]:
            for s in groupe:
                ecran.blit(s.image, (s.rect.x + cam_x, s.rect.y + cam_y))

        # Dessiner les portes visuellement
        self._dessiner_portes(ecran, cam_x, cam_y)

        # Nom de la zone
        f = pygame.font.SysFont("monospace", 22, bold=True)
        t = f.render(getattr(self, 'NOM', ''), True, (60, 60, 80))
        ecran.blit(t, (ecran.get_width()//2 - t.get_width()//2, 40))

    def _dessiner_portes(self, ecran, cam_x, cam_y):
        """Dessine un rectangle vert sur chaque porte."""
        for sortie in self.sorties:
            rect = self._sortie_rect(sortie)
            if rect:
                r = pygame.Rect(
                    rect.x + cam_x, rect.y + cam_y,
                    rect.width, rect.height
                )
                pygame.draw.rect(ecran, (30, 180, 60), r)
                # Nom de la destination
                f = pygame.font.SysFont("monospace", 11, bold=True)
                t = f.render(sortie["destination"].replace("zone_", "Z"), True, (255,255,255))
                ecran.blit(t, (r.x + 2, r.y + 2))
