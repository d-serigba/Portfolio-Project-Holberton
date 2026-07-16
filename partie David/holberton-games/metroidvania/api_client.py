# ============================================================
#   METROIDVANIA — api_client_web.py
#   Version WEB : remplace requests par le pont JS (postMessage).
#
#   Remplace api_client.py UNIQUEMENT pour le build pygbag.
#   Même interface publique (token, user, connecte(), envoyer_score(),
#   register(), login(), classement(), deconnecter()) donc facade.py
#   n'a besoin D'AUCUNE MODIFICATION.
#
#   register()/login()/classement() ne sont PAS utilisées par facade.py
#   (vérifié : seuls .token, .user et .envoyer_score() le sont), donc
#   elles restent ici en versions "désactivées" par sécurité, au cas où.
# ============================================================

import sys


class ApiClient:

    def __init__(self):
        self.token = None
        self.user = None
        # Web : pas de fichier token.json à lire ici. La session (pseudo +
        # token) est injectée depuis l'URL par main.py, puis affectée
        # directement sur self.token / self.user par facade.py, exactement
        # comme le fait déjà l'original avant l'appel à envoyer_score().

    def connecte(self):
        return self.token is not None

    def register(self, username, password):
        print("[API-WEB] register() non disponible dans le build web (géré par index.html)")
        return False, {"error": "Non disponible en version web"}

    def login(self, username, password):
        print("[API-WEB] login() non disponible dans le build web (géré par index.html)")
        return False, {"error": "Non disponible en version web"}

    def envoyer_score(self, score, completion, temps_jeu):
        """
        Remplace le POST HTTP par un postMessage vers la page parente
        (index.html), qui fait le vrai fetch() vers l'API Flask en JS
        (CORS géré côté JS, pas de `requests` possible en WASM).
        """
        if not self.connecte():
            print("[API-WEB] Pas connecté — score non envoyé")
            return False

        if sys.platform != "emscripten":
            print(f"[API-WEB local] Score simulé -> metroidvania: {score} pts "
                  f"(completion={completion}%, temps={temps_jeu}s)")
            return True

        try:
            import platform
            import json

            message = {
                "type": "GAME_SCORE",
                "jeu": "metroidvania",
                "score": min(score, 9999),
                "completion": completion,
                "temps_jeu": temps_jeu,
            }
            platform.window.parent.postMessage(json.dumps(message), "*")
            print(f"[API-WEB] Score envoyé au parent : {message}")
            return True
        except Exception as e:
            print(f"[API-WEB] Erreur lors de l'envoi du score : {e}")
            return False

    def classement(self):
        print("[API-WEB] classement() non disponible dans le build web (utilisez le classement du hub)")
        return []

    def deconnecter(self):
        self.token = None
        self.user = None
