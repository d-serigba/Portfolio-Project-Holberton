# ============================================================
#  map/__init__.py — FACADE
#  Import unique pour toutes les zones.
#  Si tu renommes une zone, tu modifies SEULEMENT ici.
#
#  Usage dans main.py :
#    from map import ZoneA, Zone1, Zone2, ..., ZoneB
#    from map import GestionnaireZones
# ============================================================

from map.zone_a  import ZoneA
from map.zone_1  import Zone1
from map.zone_2  import Zone2
from map.zone_3  import Zone3
from map.zone_4  import Zone4
from map.zone_5  import Zone5
from map.zone_6  import Zone6
from map.zone_7  import Zone7
from map.zone_8  import Zone8
from map.zone_9  import Zone9
from map.zone_10 import Zone10
from map.zone_11 import Zone11
from map.zone_12 import Zone12
from map.zone_13 import Zone13
from map.zone_14 import Zone14
from map.zone_15 import Zone15
from map.zone_16 import Zone16
from map.zone_b  import ZoneB
from map.zone_s2 import ZoneS2
from map.zone_s1 import ZoneS1


class GestionnaireZones:
    """
    Gère le chargement et les transitions entre zones.

    Usage dans main.py :
        gestionnaire = GestionnaireZones()
        pos = gestionnaire.charger("zone_a")
        arnaud.rect.topleft = pos

        # Quand Arnaud touche une sortie :
        pos = gestionnaire.changer("zone_1", "haut")
        arnaud.rect.topleft = pos
    """

    ZONES = {
        "zone_a"  : ZoneA,
        "zone_1"  : Zone1,
        "zone_2"  : Zone2,
        "zone_3"  : Zone3,
        "zone_4"  : Zone4,
        "zone_5"  : Zone5,
        "zone_6"  : Zone6,
        "zone_7"  : Zone7,
        "zone_8"  : Zone8,
        "zone_9"  : Zone9,
        "zone_10" : Zone10,
        "zone_11" : Zone11,
        "zone_12" : Zone12,
        "zone_13" : Zone13,
        "zone_14" : Zone14,
        "zone_15" : Zone15,
        "zone_16" : Zone16,
        "zone_b"  : ZoneB,
        "zone_s2" : ZoneS2,
        "zone_s1" : ZoneS1,
    }

    def __init__(self):
        self.zone_active = None
        self.nom_actuel  = None

    def charger(self, nom, spawn="defaut"):
        """Charge une zone et retourne la position de spawn d'Arnaud."""
        self.nom_actuel  = nom
        self.zone_active = self.ZONES[nom]()
        return self.zone_active.spawns[spawn]

    def changer(self, nom, spawn="defaut"):
        """Transition vers une nouvelle zone."""
        return self.charger(nom, spawn)

    @property
    def zone(self):
        """Raccourci : gestionnaire.zone au lieu de gestionnaire.zone_active."""
        return self.zone_active
