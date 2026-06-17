# ============================================================
#  ARNAUD METROIDVANIA — state_manager.py
#
#  Gère tout ce qui doit persister entre les sessions :
#    - Zone actuelle + position de spawn
#    - Vie, cœurs, missiles
#    - Capacités débloquées
#    - Légos collectés
#    - Checkpoints activés
#    - Zones visitées
#
#  Les données sont stockées dans save/sauvegarde.json
# ============================================================

import json
import os

DOSSIER_SAVE = os.path.join(os.path.dirname(__file__), "save")
FICHIER_SAVE = os.path.join(DOSSIER_SAVE, "sauvegarde.json")

# État par défaut — nouvelle partie
ETAT_DEFAUT = {
    "zone_actuelle"     : "zone_a",
    "spawn"             : None,        # None = utilise le spawn par défaut de la zone
    "coeurs"            : None,        # None = utilise COEURS_MAX de settings
    "vies"              : None,        # None = utilise VIES_MAX de settings
    "missiles"          : 0,
    "legos_collectes"   : 0,
    "capacites"         : {
        "double_saut"   : False,
        "glissade"      : False,
        "lego_sword"    : False,
        "lego_blast"    : False,
        "brise_mur"     : False,
        "missiles"      : False,
    },
    "checkpoints_actifs": [],          # liste des IDs de checkpoints activés
    "zones_visitees"    : ["zone_a"],
}


class StateManager:
    """
    Gestionnaire d'état centralisé.

    Usage dans facade.py :
        self.state = StateManager()
        self.state.charger()           # au lancement
        self.state.sauvegarder(arnaud, nom_zone, spawn)  # au checkpoint
        self.state.appliquer(arnaud)   # après avoir chargé une zone
    """

    def __init__(self):
        self.etat = dict(ETAT_DEFAUT)
        # Crée le dossier save s'il n'existe pas
        os.makedirs(DOSSIER_SAVE, exist_ok=True)

    # ==========================================================
    #  CHARGER
    # ==========================================================
    def charger(self):
        """
        Charge la sauvegarde depuis le fichier JSON.
        Si aucun fichier → repart de l'état par défaut.
        Retourne l'état chargé.
        """
        if not os.path.exists(FICHIER_SAVE):
            print("[SAVE] Aucune sauvegarde trouvée — nouvelle partie")
            self.etat = dict(ETAT_DEFAUT)
            self.etat["capacites"] = dict(ETAT_DEFAUT["capacites"])
            return self.etat

        try:
            with open(FICHIER_SAVE, "r") as f:
                self.etat = json.load(f)
            print(f"[SAVE] Sauvegarde chargée — zone: {self.etat['zone_actuelle']}")
        except (json.JSONDecodeError, KeyError) as e:
            print(f"[SAVE] Fichier corrompu ({e}) — nouvelle partie")
            self.etat = dict(ETAT_DEFAUT)
            self.etat["capacites"] = dict(ETAT_DEFAUT["capacites"])

        return self.etat

    # ==========================================================
    #  SAUVEGARDER
    # ==========================================================
    def sauvegarder(self, arnaud, nom_zone, spawn=None, checkpoint_id=None):
        """
        Sauvegarde l'état actuel d'Arnaud dans le fichier JSON.
        Appelée quand Arnaud touche un checkpoint.

        arnaud       — instance de la classe Arnaud
        nom_zone     — nom de la zone actuelle ("zone_1", etc.)
        spawn        — tuple (x, y) ou None (utilise position actuelle)
        checkpoint_id — identifiant unique du checkpoint (ex: "zone_1_cp1")
        """
        self.etat["zone_actuelle"]   = nom_zone
        self.etat["spawn"]           = spawn or [arnaud.rect.x, arnaud.rect.y]
        self.etat["coeurs"]          = arnaud.coeurs
        self.etat["vies"]            = arnaud.vies
        self.etat["missiles"]        = arnaud.missiles
        self.etat["legos_collectes"] = arnaud.legos_collectes
        self.etat["capacites"]       = dict(arnaud.capacites)

        # Enregistre le checkpoint comme activé
        if checkpoint_id and checkpoint_id not in self.etat["checkpoints_actifs"]:
            self.etat["checkpoints_actifs"].append(checkpoint_id)

        # Enregistre la zone comme visitée
        if nom_zone not in self.etat["zones_visitees"]:
            self.etat["zones_visitees"].append(nom_zone)

        try:
            with open(FICHIER_SAVE, "w") as f:
                json.dump(self.etat, f, indent=2)
            print(f"[SAVE] Sauvegardé — zone: {nom_zone}  spawn: {self.etat['spawn']}")
        except IOError as e:
            print(f"[SAVE] Erreur écriture : {e}")

    # ==========================================================
    #  APPLIQUER à Arnaud
    # ==========================================================
    def appliquer(self, arnaud):
        """
        Applique l'état sauvegardé à Arnaud.
        Appelée après avoir chargé une sauvegarde.
        """
        from settings import COEURS_MAX, VIES_MAX

        # Vie et cœurs
        arnaud.coeurs = self.etat["coeurs"] or COEURS_MAX
        arnaud.vies   = self.etat["vies"]   or VIES_MAX

        # Missiles et légos
        arnaud.missiles        = self.etat.get("missiles", 0)
        arnaud.legos_collectes = self.etat.get("legos_collectes", 0)

        # Capacités
        for cap, valeur in self.etat["capacites"].items():
            if valeur and cap in arnaud.capacites:
                arnaud.debloquer(cap)

        # Recalcule les dégâts selon les légos collectés
        arnaud._recalculer_degats()

        print(f"[SAVE] État appliqué à Arnaud")

    # ==========================================================
    #  EFFACER la sauvegarde
    # ==========================================================
    def effacer(self):
        """Supprime le fichier de sauvegarde — nouvelle partie."""
        if os.path.exists(FICHIER_SAVE):
            os.remove(FICHIER_SAVE)
            print("[SAVE] Sauvegarde effacée")
        self.etat = dict(ETAT_DEFAUT)
        self.etat["capacites"] = dict(ETAT_DEFAUT["capacites"])

    # ==========================================================
    #  UTILITAIRES
    # ==========================================================
    def checkpoint_est_actif(self, checkpoint_id):
        """Retourne True si ce checkpoint a déjà été activé."""
        return checkpoint_id in self.etat["checkpoints_actifs"]

    def zone_visitee(self, nom_zone):
        """Retourne True si cette zone a déjà été visitée."""
        return nom_zone in self.etat["zones_visitees"]

    def enregistrer_visite(self, nom_zone):
        """Marque une zone comme visitée sans sauvegarder."""
        if nom_zone not in self.etat["zones_visitees"]:
            self.etat["zones_visitees"].append(nom_zone)

    @property
    def zone_depart(self):
        """Zone où respawner au chargement."""
        return self.etat["zone_actuelle"]

    @property
    def spawn_depart(self):
        """Position de spawn au chargement (None = spawn par défaut de la zone)."""
        return self.etat["spawn"]
