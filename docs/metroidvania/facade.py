# ============================================================
#   ARNAUD METROIDVANIA — facade.py
#
#   Point d'entrée unique pour toute la logique du jeu.
#   main.py ne fait que la boucle pygame — tout le reste est ici.
# ============================================================

import pygame
from settings import *
from player   import Arnaud
from map      import GestionnaireZones
from map.zone_a import MissileTourelle
from state_manager import StateManager
from api_client import ApiClient


class Facade:
    """
    Façade globale — main.py l'instancie et l'appelle,
    sans jamais toucher directement player, map ou world.
    """

    ZONE_DEPART = "zone_a"

    def __init__(self):
        self._historique = []  # pile des zones visitées
        # ── Gestionnaire de zones ──────────────────────────────
        self.zones      = GestionnaireZones()
        spawn           = self.zones.charger(self.ZONE_DEPART)

        # ── Joueur ────────────────────────────────────────────
        self.arnaud     = Arnaud(*spawn)

        self.state      = StateManager()
        self.state.charger()
        self.state.appliquer(self.arnaud)

        # ── Caméra ────────────────────────────────────────────
        self._cam_x     = 0
        self._cam_y     = 0

        # ── États ─────────────────────────────────────────────
        self.game_over      = False
        self.en_transition  = False   # True pendant un fondu (plus tard)
        self.debug_mode     = True

        # ── Coyote time ───────────────────────────────────────
        self._coyote_frames = 0
        self._COYOTE_MAX    = 8

        # Initialisation de l'API dédiée au Metroidvania (Correction du TypeError ici)
        self.api            = ApiClient()
        self.token_joueur   = None
        self.pseudo_joueur  = None

        self.score          = 0
        self.ennemis_tues   = 0
        self.debut_temps    = __import__("time").time()
        self.projectiles    = pygame.sprite.Group()
        self._cooldown_transition = 0  # frames de grâce

    # ==========================================================
    #  UPDATE — appelé chaque frame depuis main.py
    # ==========================================================
    def update(self, touches, events):
        if self.game_over:
            return

        zone = self.zones.zone

        if self._cooldown_transition > 0:
            self._cooldown_transition -= 1

        # ── Physique & input ───────────────────────────────────
        plateformes = zone.plateformes.sprites()
        murs        = zone.murs.sprites()
        self.arnaud.update(touches, plateformes, murs)

        # ── Coyote time ───────────────────────────────────────
        if self.arnaud.au_sol or self.arnaud.au_sol_precedent:
            self._coyote_frames = self._COYOTE_MAX
        elif self._coyote_frames > 0:
            self._coyote_frames -= 1

        # ── Tracking des ennemis éliminés ──────────────────────
        nb_ennemis_avant = len(zone.ennemis.sprites()) if hasattr(zone, 'ennemis') else 0

        # ── Zone update ───────────────────────────────────────
        if hasattr(zone, 'update'):
            zone.update(self.arnaud)

        nb_ennemis_apres = len(zone.ennemis.sprites()) if hasattr(zone, 'ennemis') else 0
        if nb_ennemis_avant > nb_ennemis_apres:
            diff = nb_ennemis_avant - nb_ennemis_apres
            self.ennemis_tues += diff
            print(f"[TRACKING] Ennemi éliminé ! Total tués : {self.ennemis_tues}")

        # Verif drapeau de sauvegarde
        if hasattr(zone, 'verifier_save'):
            zone.verifier_save(self.arnaud, self.state)

        # ── Vérif transitions ─────────────────────────────────
        self._verifier_sorties()

        # ── Caméra ────────────────────────────────────────────
        self._mettre_a_jour_camera()

        # ── Perte de vie simple — respawn au checkpoint ────────
        if self.arnaud.respawn_demande:
            self.arnaud.respawn_demande = False
            self._respawn_checkpoint()

        # ── Game over — plus de vies, reset complet ────────────
        if self.arnaud.est_mort():
            self.game_over = True
            self.state.effacer()

    # ==========================================================
    #  SAUT — appelé sur KEYDOWN depuis main.py
    # ==========================================================
    def trigger_saut(self):
        if self.arnaud.au_sol or self._coyote_frames > 0:
            self.arnaud.trigger_saut()
            self._coyote_frames = 0   # consomme le coyote time
        elif self.arnaud.a_double_saut and self.arnaud.sauts_restants > 0:
            self.arnaud.trigger_saut()

    # ==========================================================
    #  TRANSITIONS ENTRE ZONES
    # ==========================================================
    def _verifier_sorties(self):
        if self._cooldown_transition > 0:
            return
        zone = self.zones.zone
        if not hasattr(zone, 'sorties'):
            return
        for sortie in zone.sorties:
            if "rect" in sortie:
                rect = sortie["rect"]
            elif hasattr(zone, "_sortie_rect"):
                rect = zone._sortie_rect(sortie)
            else:
                continue
            if rect and self.arnaud.rect.colliderect(rect):
                self.changer_zone(sortie["destination"], sortie["spawn"])
                return

    def _respawn_checkpoint(self):
        import os
        from state_manager import FICHIER_SAVE

        vies_actuelles = self.arnaud.vies
        if os.path.exists(FICHIER_SAVE):
            self.state.charger()
            zone_save  = self.state.zone_depart
            spawn_save = self.state.spawn_depart
            pos = self.zones.changer(zone_save)
            if spawn_save:
                pos = tuple(spawn_save)
        else:
            pos = self.zones.changer(self.ZONE_DEPART)

        self.arnaud.rect.topleft   = pos
        self.arnaud.hitbox.topleft = (pos[0]+2, pos[1])
        self.arnaud.vel_x = 0
        self.arnaud.vel_y = 0
        self.arnaud.vies  = vies_actuelles
        print(f"[RESPAWN] Vie perdue — retour au checkpoint ({self.arnaud.vies} vies restantes)")

    def changer_zone(self, nom, spawn="defaut"):
        pos = self.zones.changer(nom, spawn)
        self.arnaud.rect.topleft     = pos
        self.arnaud.hitbox.topleft   = (pos[0] + 2, pos[1])
        self.arnaud.vel_x            = 0
        self.arnaud.vel_y            = 0
        self._cooldown_transition    = 90  # 1.5 sec
        self._historique.append(self.zones.nom_actuel or nom)
        print(f"[ZONE] → {nom} (spawn: {spawn})")

    # ==========================================================
    #  CAMÉRA
    # ==========================================================
    def _mettre_a_jour_camera(self):
        zone = self.zones.zone
        cx = LARGEUR  // 2 - self.arnaud.rect.centerx
        cy = HAUTEUR  // 2 - self.arnaud.rect.centery
        cx = min(0, max(LARGEUR  - zone.LARGEUR_MONDE, cx))
        cy = min(0, max(HAUTEUR - zone.HAUTEUR_MONDE, cy))
        self._cam_x = cx
        self._cam_y = cy

    @property
    def cam_x(self): return self._cam_x
    @property
    def cam_y(self): return self._cam_y

    # ==========================================================
    #  DESSIN — appelé chaque frame depuis main.py
    # ==========================================================
    def dessiner(self, ecran):
        zone = self.zones.zone
        zone.dessiner(ecran, self._cam_x, self._cam_y)

        if self.debug_mode:
            zone_atk = self.arnaud.get_zone_attaque()
            if zone_atk:
                s = pygame.Surface((zone_atk.width, zone_atk.height), pygame.SRCALPHA)
                s.fill((255, 220, 0, 100))
                ecran.blit(s, (zone_atk.x + self._cam_x, zone_atk.y + self._cam_y))

        for p in self.projectiles:
            ecran.blit(p.image, (p.rect.x + self._cam_x, p.rect.y + self._cam_y))

        ecran.blit(
            self.arnaud.image,
            (self.arnaud.rect.x + self._cam_x, self.arnaud.rect.y + self._cam_y)
        )

        if self.debug_mode:
            hb = self.arnaud.hitbox
            pygame.draw.rect(ecran, (0, 255, 100), (
                hb.x + self._cam_x, hb.y + self._cam_y,
                hb.width, hb.height
            ), 1)

        self.arnaud.dessiner_ui(ecran)

    def dessiner_debug(self, ecran, police):
        infos = [
            f"zone : {self.zones.nom_actuel}",
            f"vel_x={self.arnaud.vel_x:.1f}  vel_y={self.arnaud.vel_y:.1f}",
            f"au_sol={self.arnaud.au_sol}  coyote={self._coyote_frames}",
            f"sauts={self.arnaud.sauts_restants}  esquive={self.arnaud.en_esquive}",
            f"accroupi={self.arnaud.accroupi}",
            f"tués={self.ennemis_tues}",
            f"caps: {[k for k,v in self.arnaud.capacites.items() if v] or 'aucune'}",
            "F1=dbl_saut  F2=tout  F3=debug  F4=zone suiv",
        ]
        for i, ligne in enumerate(infos):
            t = police.render(ligne, True, (100, 200, 100))
            ecran.blit(t, (LARGEUR - t.get_width() - 10, 10 + i * 18))

    # ==========================================================
    #  ACTIONS DEBUG
    # ==========================================================
    def debug_debloquer_tout(self):
        for map in self.arnaud.capacites:
            self.arnaud.debloquer(map)
        print("[DEBUG] Toutes capacités débloquées")

    def debug_zone_suivante(self):
        ordre = [
            "zone_a", "zone_1", "zone_2", "zone_3", "zone_4",
            "zone_5", "zone_6", "zone_7", "zone_8", "zone_9",
            "zone_10", "zone_11", "zone_12", "zone_13", "zone_14",
            "zone_15", "zone_16", "zone_b",
        ]
        actuel = self.zones.nom_actuel
        if actuel in ordre:
            idx = ordre.index(actuel)
            suivante = ordre[min(idx + 1, len(ordre) - 1)]
            self.changer_zone(suivante)

    def debug_zone_precedente(self):
        ordre = [
            "zone_a", "zone_1", "zone_2", "zone_3", "zone_4",
            "zone_5", "zone_6", "zone_7", "zone_8", "zone_9",
            "zone_10", "zone_11", "zone_12", "zone_13", "zone_14",
            "zone_15", "zone_16", "zone_b",
        ]
        actuel = self.zones.nom_actuel
        if actuel in ordre:
            idx = ordre.index(actuel)
            prec = ordre[max(idx - 1, 0)]
            self.changer_zone(prec)

    # ==========================================================
    #  RECOMMENCER
    # ==========================================================
    def recommencer(self):
        import os
        from state_manager import FICHIER_SAVE

        if os.path.exists(FICHIER_SAVE):
            self.state.charger()
            zone_save   = self.state.zone_depart
            spawn_save  = self.state.spawn_depart
            spawn = self.zones.charger(zone_save)
            if spawn_save:
                spawn = tuple(spawn_save)
        else:
            spawn = self.zones.charger(self.ZONE_DEPART)

        self.arnaud         = Arnaud(*spawn)
        self.game_over      = False
        self._coyote_frames = 0
        print(f"[JEU] Recommencé — zone: {self.zones.nom_actuel}")

    # ==========================================================
    #  ENVOI DU SCORE SECURISE
    # ==========================================================
    def calculer_et_envoyer_score(self):
        """Calcule le score final et l'envoie à l'API."""
        import time

        # Synchronisation forcée des tokens récupérés au login
        self.api.token = self.token_joueur
        self.api.user  = self.pseudo_joueur

        zones_visitees = len(self.state.etat.get("zones_visitees", []))
        legos          = self.arnaud.legos_collectes
        ennemis        = self.ennemis_tues

        score = (zones_visitees * 100) + (ennemis * 50) + (legos * 200)
        score = min(score, 9999)
        completion = int((zones_visitees / 18) * 100)
        temps_jeu  = int(time.time() - self.debut_temps)

        # L'envoi prend en compte le Token JWT
        self.api.envoyer_score(score, completion, temps_jeu)
        return score
