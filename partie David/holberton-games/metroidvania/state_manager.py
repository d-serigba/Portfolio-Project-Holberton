# ============================================================
#   METROIDVANIA — state_manager_web.py
#   Version WEB : sauvegarde de progression désactivée.
#
#   Remplace state_manager.py UNIQUEMENT pour le build pygbag.
#   Même interface publique que l'original (charger, sauvegarder,
#   appliquer, effacer, zone_depart, spawn_depart, etc.) donc
#   facade.py n'a besoin D'AUCUNE MODIFICATION : il continue
#   d'appeler exactement les mêmes méthodes.
#
#   Différence : tout reste en mémoire (dict Python), rien n'est
#   écrit sur disque. Le joueur recommence du début à chaque partie,
#   MAIS le score est bien calculé et envoyé au hub en fin de partie
#   (ça, c'est api_client_web.py qui s'en charge, pas ce fichier).
#
#   FICHIER_SAVE reste exporté (facade.py l'importe) mais pointe sur
#   une chaîne vide : os.path.exists("") vaut toujours False, donc
#   facade.py prend naturellement la branche "pas de sauvegarde" et
#   démarre une partie neuve, sans qu'on ait à modifier facade.py.
# ============================================================

FICHIER_SAVE = ""  # volontairement vide : jamais "existant" -> toujours une partie neuve

ETAT_DEFAUT = {
    "zone_actuelle"     : "zone_a",
    "spawn"             : None,
    "coeurs"            : None,
    "vies"              : None,
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
    "checkpoints_actifs": [],
    "zones_visitees"    : ["zone_a"],
}


class StateManager:
    def __init__(self):
        self.etat = dict(ETAT_DEFAUT)
        self.etat["capacites"] = dict(ETAT_DEFAUT["capacites"])

    def charger(self):
        """Web : rien à charger depuis le disque, on repart toujours de l'état par défaut."""
        self.etat = dict(ETAT_DEFAUT)
        self.etat["capacites"] = dict(ETAT_DEFAUT["capacites"])
        print("[SAVE-WEB] Nouvelle partie (pas de sauvegarde persistante en version web)")
        return self.etat

    def sauvegarder(self, arnaud, nom_zone, spawn=None, checkpoint_id=None):
        """
        Web : on met à jour l'état EN MÉMOIRE (utile pour le calcul du score
        en fin de partie : zones_visitees, legos_collectes, etc.), mais on
        n'écrit rien sur disque.
        """
        self.etat["zone_actuelle"]   = nom_zone
        self.etat["spawn"]           = spawn or [arnaud.rect.x, arnaud.rect.y]
        self.etat["coeurs"]          = arnaud.coeurs
        self.etat["vies"]            = arnaud.vies
        self.etat["missiles"]        = arnaud.missiles
        self.etat["legos_collectes"] = arnaud.legos_collectes
        self.etat["capacites"]       = dict(arnaud.capacites)

        if checkpoint_id and checkpoint_id not in self.etat["checkpoints_actifs"]:
            self.etat["checkpoints_actifs"].append(checkpoint_id)
        if nom_zone not in self.etat["zones_visitees"]:
            self.etat["zones_visitees"].append(nom_zone)

    def appliquer(self, arnaud):
        from settings import COEURS_MAX, VIES_MAX
        arnaud.coeurs = self.etat["coeurs"] or COEURS_MAX
        arnaud.vies   = self.etat["vies"]   or VIES_MAX
        arnaud.missiles        = self.etat.get("missiles", 0)
        arnaud.legos_collectes = self.etat.get("legos_collectes", 0)
        for cap, valeur in self.etat["capacites"].items():
            if valeur and cap in arnaud.capacites:
                arnaud.debloquer(cap)
        arnaud._recalculer_degats()
        print("[SAVE-WEB] État par défaut appliqué à Arnaud")

    def effacer(self):
        """Web : rien à effacer sur disque, on réinitialise juste la mémoire."""
        self.etat = dict(ETAT_DEFAUT)
        self.etat["capacites"] = dict(ETAT_DEFAUT["capacites"])

    def checkpoint_est_actif(self, checkpoint_id):
        return checkpoint_id in self.etat["checkpoints_actifs"]

    def zone_visitee(self, nom_zone):
        return nom_zone in self.etat["zones_visitees"]

    def enregistrer_visite(self, nom_zone):
        if nom_zone not in self.etat["zones_visitees"]:
            self.etat["zones_visitees"].append(nom_zone)

    @property
    def zone_depart(self):
        return self.etat["zone_actuelle"]

    @property
    def spawn_depart(self):
        return self.etat["spawn"]
