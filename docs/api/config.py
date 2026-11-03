import os

from dotenv import load_dotenv

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Charge docs/api/.env (non versionné) dans les variables d'environnement
load_dotenv(os.path.join(BASE_DIR, ".env"))


def _secret_obligatoire(nom):
    """Lit un secret dans l'environnement. Refuse de démarrer s'il est absent ou trop court."""
    valeur = os.environ.get(nom)
    if not valeur or len(valeur) < 32:
        raise RuntimeError(
            f"{nom} manquant ou trop court (32 caractères minimum). "
            f"Génère-le avec : python -c \"import secrets; print(secrets.token_hex(32))\" "
            f"puis ajoute-le dans docs/api/.env (voir .env.example)."
        )
    return valeur


class Config:
    SECRET_KEY     = _secret_obligatoire("SECRET_KEY")
    JWT_SECRET_KEY = _secret_obligatoire("JWT_SECRET_KEY")
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL",
        "sqlite:///" + os.path.join(BASE_DIR, "instance", "game_hub.db")
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
