import requests
import json
import os

API_URL    = "http://localhost:5000"

# Ajustement du chemin pour viser le même "token.json" partagé dans /docs/
TOKEN_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "token.json")


class ApiClient:

    def __init__(self):
        self.token   = None
        self.user    = None
        self._charger_token()

    def _charger_token(self):
        """Charge le token sauvegardé s'il existe."""
        if os.path.exists(TOKEN_FILE):
            try:
                with open(TOKEN_FILE, "r") as f:
                    data = json.load(f)
                self.token = data.get("token")
                self.user  = data.get("user")
                print(f"[API Metroidvania] Session chargée pour : {self.user}")
            except Exception as e:
                print(f"[API Metroidvania] Échec lecture session : {e}")

    def _sauvegarder_token(self):
        """Sauvegarde le token localement dans l'espace partagé."""
        try:
            os.makedirs(os.path.dirname(TOKEN_FILE), exist_ok=True)
            with open(TOKEN_FILE, "w") as f:
                json.dump({"token": self.token, "user": self.user}, f)
        except Exception as e:
            print(f"[API Metroidvania] Échec sauvegarde session : {e}")

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
                self.user  = data["user"]["username"] if isinstance(data["user"], dict) else data["user"]
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
                    "jeu"       : "metroidvania",
                    "score"     : min(score, 9999),
                    "completion": completion,
                    "temps_jeu" : temps_jeu
                },
                headers={"Authorization": f"Bearer {self.token}"},
                timeout=3
            )
            if r.status_code == 201:
                print(f"[API] Score envoyé : {score} pts")
                return True
            print(f"[API] Échec envoi score, statut : {r.status_code}")
            return False
        except Exception as e:
            print(f"[API] Erreur lors de l'envoi du score : {e}")
            return False

    def classement(self):
        """Récupère le classement global pour le Metroidvania."""
        try:
            r = requests.get(f"{API_URL}/api/scores/classement/metroidvania", timeout=3)
            return r.json() if r.status_code == 200 else []
        except:
            return []

    def deconnecter(self):
        self.token = None
        self.user  = None
        if os.path.exists(TOKEN_FILE):
            try:
                os.remove(TOKEN_FILE)
            except:
                pass
