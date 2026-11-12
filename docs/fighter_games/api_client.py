# ============================================================
#   GAME HUB — api_client.py (fighter_games)
#   Aligné sur metroidvania/api_client.py
# ============================================================

import requests
import os

API_URL = "http://127.0.0.1:5000"


class ApiClient:

    def __init__(self, nom_jeu="brawler"):
        self.nom_jeu = nom_jeu
        self.token = None
        self.user = None
        self._charger_session()

    # ------------------------------------------------------------------
    # Session (en mémoire uniquement, transmise par le site au lancement)
    # ------------------------------------------------------------------

    def _headers(self):
        return {"Authorization": f"Bearer {self.token}"}

    def _charger_session(self):
        env_token = os.environ.get("GAME_TOKEN")
        env_user = os.environ.get("GAME_USER")
        if env_token and env_user:
            self.token = env_token
            self.user = env_user
            print(f"[API {self.nom_jeu}] Session reçue du site pour : {self.user}")
        else:
            print(f"[API {self.nom_jeu}] Aucune session, connexion requise")

    def _effacer_session(self):
        self.token = None
        self.user = None

    def connecte(self):
        return self.token is not None

    # ------------------------------------------------------------------
    # Authentification
    # ------------------------------------------------------------------

    def register(self, username, password):
        try:
            r = requests.post(
                f"{API_URL}/api/auth/register",
                json={"username": username, "password": password},
                timeout=3,
            )
            return r.status_code == 201, r.json()
        except requests.RequestException:
            return False, {"error": "API non disponible"}
        except ValueError:
            return False, {"error": "Réponse invalide du serveur"}

    def login(self, username, password):
        try:
            r = requests.post(
                f"{API_URL}/api/auth/login",
                json={"username": username, "password": password},
                timeout=3,
            )
            if r.status_code == 200:
                data = r.json()
                self.token = data["token"]
                u = data["user"]
                self.user = u["username"] if isinstance(u, dict) else u
                return True, data
            return False, r.json()
        except requests.RequestException:
            return False, {"error": "API non disponible"}
        except (ValueError, KeyError):
            return False, {"error": "Réponse invalide du serveur"}

    def deconnecter(self):
        if self.token:
            try:
                requests.post(
                    f"{API_URL}/api/auth/logout",
                    headers=self._headers(),
                    timeout=2,
                )
            except requests.RequestException:
                pass
        self._effacer_session()

    # ------------------------------------------------------------------
    # Scores
    # ------------------------------------------------------------------

    def envoyer_score(self, score, completion, temps_jeu):
        if not self.connecte():
            print("[API] Pas connecté, score non envoyé")
            return False
        try:
            r = requests.post(
                f"{API_URL}/api/scores/submit",
                json={
                    "jeu": self.nom_jeu,
                    "score": min(score, 9999),
                    "completion": completion,
                    "temps_jeu": temps_jeu,
                },
                headers=self._headers(),
                timeout=3,
            )
            if r.status_code == 201:
                print(f"[API {self.nom_jeu}] Score envoyé : {score} pts")
                return True
            if r.status_code == 401:
                print("[API] Session expirée, reconnexion nécessaire")
                self._effacer_session()
                return False
            print(f"[API] Échec envoi score, statut : {r.status_code}")
            return False
        except requests.RequestException as e:
            print(f"[API] Erreur lors de l'envoi du score : {e}")
            return False

    def classement(self):
        try:
            r = requests.get(
                f"{API_URL}/api/scores/classement/{self.nom_jeu}",
                timeout=3,
            )
            return r.json() if r.status_code == 200 else []
        except (requests.RequestException, ValueError):
            return []
