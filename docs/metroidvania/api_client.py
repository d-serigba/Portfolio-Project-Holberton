import requests
import json
import os

API_URL = "http://127.0.0.1:5000"

# Un seul fichier de session partagé : docs/token.json
TOKEN_FILE = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "token.json"
)


class ApiClient:

    def __init__(self, nom_jeu="metroidvania"):
        self.nom_jeu = nom_jeu
        self.token = None
        self.user = None
        self._charger_token()

    def _headers(self):
        return {"Authorization": f"Bearer {self.token}"}

    def _charger_token(self):
        if os.path.exists(TOKEN_FILE):
            try:
                with open(TOKEN_FILE, "r") as f:
                    data = json.load(f)
                self.token = data.get("token")
                self.user = data.get("user")
                print(f"[API {self.nom_jeu}] Session chargée pour : {self.user}")
            except (OSError, json.JSONDecodeError) as e:
                print(f"[API {self.nom_jeu}] Échec lecture session : {e}")

    def _sauvegarder_token(self):
        try:
            os.makedirs(os.path.dirname(TOKEN_FILE), exist_ok=True)
            with open(TOKEN_FILE, "w") as f:
                json.dump({"token": self.token, "user": self.user}, f)
        except OSError as e:
            print(f"[API {self.nom_jeu}] Échec sauvegarde session : {e}")

    def _supprimer_token_local(self):
        self.token = None
        self.user = None
        if os.path.exists(TOKEN_FILE):
            try:
                os.remove(TOKEN_FILE)
            except OSError:
                pass

    def connecte(self):
        return self.token is not None

    def register(self, username, password):
        try:
            r = requests.post(f"{API_URL}/api/auth/register",
                              json={"username": username, "password": password}, timeout=3)
            return r.status_code == 201, r.json()
        except requests.RequestException:
            return False, {"error": "API non disponible"}

    def login(self, username, password):
        try:
            r = requests.post(f"{API_URL}/api/auth/login",
                              json={"username": username, "password": password}, timeout=3)
            if r.status_code == 200:
                data = r.json()
                self.token = data["token"]
                u = data["user"]
                self.user = u["username"] if isinstance(u, dict) else u
                self._sauvegarder_token()
                return True, data
            return False, r.json()
        except requests.RequestException:
            return False, {"error": "API non disponible"}

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
                    "temps_jeu": temps_jeu
                },
                headers=self._headers(),
                timeout=3
            )
            if r.status_code == 201:
                print(f"[API] Score envoyé : {score} pts")
                return True
            print(f"[API] Échec envoi score, statut : {r.status_code}")
            return False
        except requests.RequestException as e:
            print(f"[API] Erreur lors de l'envoi du score : {e}")
            return False

    def classement(self):
        try:
            r = requests.get(f"{API_URL}/api/scores/classement/{self.nom_jeu}", timeout=3)
            return r.json() if r.status_code == 200 else []
        except requests.RequestException:
            return []

    def deconnecter(self):
        if self.token:
            try:
                requests.post(f"{API_URL}/api/auth/logout", headers=self._headers(), timeout=2)
            except requests.RequestException:
                pass
        self._supprimer_token_local()
