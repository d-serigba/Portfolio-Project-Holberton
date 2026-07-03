# ============================================================
#   GAME HUB — api_client.py
#   Gère la communication avec l'API Game Hub
# ============================================================

import requests
import json
import os

API_URL    = "http://localhost:5000"
TOKEN_FILE = os.path.join(os.path.dirname(__file__), "save", "token.json")


class ApiClient:

    def __init__(self, nom_jeu="brawler"):
        self.nom_jeu = nom_jeu  # Permet d'identifier dynamiquement le jeu
        self.token   = None
        self.user    = None
        self._charger_token()

    def _charger_token(self):
        """Charge le token sauvegardé si il existe."""
        if os.path.exists(TOKEN_FILE):
            try:
                with open(TOKEN_FILE) as f:
                    data = json.load(f)
                self.token = data.get("token")
                self.user  = data.get("user")
            except:
                pass

    def _sauvegarder_token(self):
        """Sauvegarde le token localement et crée le dossier save si nécessaire."""
        try:
            dossier_save = os.path.dirname(TOKEN_FILE)
            if not os.path.exists(dossier_save):
                os.makedirs(dossier_save)
                
            with open(TOKEN_FILE, "w") as f:
                json.dump({"token": self.token, "user": self.user}, f)
        except Exception as e:
            print(f"[API] Impossible de sauvegarder le token localement : {e}")

    def connecte(self):
        return self.token is not None

    def register(self, username, password):
        try:
            r = requests.post(f"{API_URL}/api/auth/register",
                json={"username": username, "password": password}, timeout=3)
            return r.status_code == 201, r.json()
        except:
            return False, {"error": "API non disponible"}

    def login(self, username, password):
        try:
            r = requests.post(f"{API_URL}/api/auth/login",
                json={"username": username, "password": password}, timeout=3)
            if r.status_code == 200:
                data = r.json()
                self.token = data["token"]
                self.user  = data["user"]
                self._sauvegarder_token()
                return True, data
            return False, r.json()
        except:
            return False, {"error": "API non disponible"}

    def envoyer_score(self, score, completion, temps_jeu):
        """Envoie le score à l'API à la fin de la session."""
        if not self.connecte():
            print("[API] Pas connecté — score non envoyé")
            return False
        try:
            r = requests.post(
                f"{API_URL}/api/scores/submit",
                json={
                    "jeu"       : self.nom_jeu,  # Utilise le nom défini à l'initialisation
                    "score"     : min(score, 9999),
                    "completion": completion,
                    "temps_jeu" : temps_jeu
                },
                headers={"Authorization": f"Bearer {self.token}"},
                timeout=3
            )
            if r.status_code == 201:
                print(f"[API] Score envoyé pour {self.nom_jeu} : {score} pts")
                return True
            return False
        except:
            print("[API] Erreur envoi score")
            return False

    def classement(self):
        """Récupère le classement global."""
        try:
            r = requests.get(f"{API_URL}/api/scores/classement", timeout=3)
            return r.json() if r.status_code == 200 else []
        except:
            return []

    def deconnecter(self):
        self.token = None
        self.user  = None
        if os.path.exists(TOKEN_FILE):
            os.remove(TOKEN_FILE)
