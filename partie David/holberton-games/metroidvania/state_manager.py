import os
import json
from sqlalchemy import create_engine, Column, Integer, String, Boolean
from sqlalchemy.orm import declarative_base, sessionmaker

DOSSIER_SAVE = os.path.join(os.path.dirname(__file__), "save")
os.makedirs(DOSSIER_SAVE, exist_ok=True)
FICHIER_SAVE = os.path.join(DOSSIER_SAVE, "save.db")

Base = declarative_base()

class Sauvegarde(Base):
    __tablename__ = "sauvegardes"
    id               = Column(Integer, primary_key=True)
    zone_actuelle    = Column(String,  default="zone_a")
    spawn_x          = Column(Integer, nullable=True)
    spawn_y          = Column(Integer, nullable=True)
    coeurs           = Column(Integer, nullable=True)
    vies             = Column(Integer, nullable=True)
    missiles         = Column(Integer, default=0)
    legos_collectes  = Column(Integer, default=0)
    cap_double_saut  = Column(Boolean, default=False)
    cap_glissade     = Column(Boolean, default=False)
    cap_lego_sword   = Column(Boolean, default=False)
    cap_lego_blast   = Column(Boolean, default=False)
    cap_brise_mur    = Column(Boolean, default=False)
    cap_missiles     = Column(Boolean, default=False)
    checkpoints_actifs = Column(String, default="[]")
    zones_visitees      = Column(String, default='["zone_a"]')

ENGINE  = create_engine(f"sqlite:///{FICHIER_SAVE}", echo=False)
Session = sessionmaker(bind=ENGINE)
Base.metadata.create_all(ENGINE)

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
        session = Session()
        try:
            row = session.query(Sauvegarde).filter_by(id=1).first()
            if row is None:
                print("[SAVE] Aucune sauvegarde trouvée — nouvelle partie")
                self.etat = dict(ETAT_DEFAUT)
                self.etat["capacites"] = dict(ETAT_DEFAUT["capacites"])
                return self.etat
            self.etat = {
                "zone_actuelle"     : row.zone_actuelle,
                "spawn"             : [row.spawn_x, row.spawn_y] if row.spawn_x is not None else None,
                "coeurs"            : row.coeurs,
                "vies"              : row.vies,
                "missiles"          : row.missiles,
                "legos_collectes"   : row.legos_collectes,
                "capacites": {
                    "double_saut" : row.cap_double_saut,
                    "glissade"    : row.cap_glissade,
                    "lego_sword"  : row.cap_lego_sword,
                    "lego_blast"  : row.cap_lego_blast,
                    "brise_mur"   : row.cap_brise_mur,
                    "missiles"    : row.cap_missiles,
                },
                "checkpoints_actifs": json.loads(row.checkpoints_actifs),
                "zones_visitees"    : json.loads(row.zones_visitees),
            }
            print(f"[SAVE] Sauvegarde chargée — zone: {self.etat['zone_actuelle']}")
        finally:
            session.close()
        return self.etat

    def sauvegarder(self, arnaud, nom_zone, spawn=None, checkpoint_id=None):
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

        session = Session()
        try:
            row = session.query(Sauvegarde).filter_by(id=1).first()
            if row is None:
                row = Sauvegarde(id=1)
                session.add(row)
            row.zone_actuelle    = self.etat["zone_actuelle"]
            row.spawn_x          = self.etat["spawn"][0]
            row.spawn_y          = self.etat["spawn"][1]
            row.coeurs           = self.etat["coeurs"]
            row.vies             = self.etat["vies"]
            row.missiles         = self.etat["missiles"]
            row.legos_collectes  = self.etat["legos_collectes"]
            caps = self.etat["capacites"]
            row.cap_double_saut  = caps["double_saut"]
            row.cap_glissade     = caps["glissade"]
            row.cap_lego_sword   = caps["lego_sword"]
            row.cap_lego_blast   = caps["lego_blast"]
            row.cap_brise_mur    = caps["brise_mur"]
            row.cap_missiles     = caps["missiles"]
            row.checkpoints_actifs = json.dumps(self.etat["checkpoints_actifs"])
            row.zones_visitees      = json.dumps(self.etat["zones_visitees"])
            session.commit()
            print(f"[SAVE] Sauvegardé — zone: {nom_zone}  spawn: {self.etat['spawn']}")
        except Exception as e:
            session.rollback()
            print(f"[SAVE] Erreur écriture : {e}")
        finally:
            session.close()

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
        print(f"[SAVE] État appliqué à Arnaud")

    def effacer(self):
        session = Session()
        try:
            row = session.query(Sauvegarde).filter_by(id=1).first()
            if row is not None:
                session.delete(row)
                session.commit()
                print("[SAVE] Sauvegarde effacée")
        finally:
            session.close()
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
