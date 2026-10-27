import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

class Config:
    SECRET_KEY     = os.environ.get("SECRET_KEY", "arnaud_game_hub_secret_2026")
    JWT_SECRET_KEY = os.environ.get("JWT_SECRET_KEY", "jwt_arnaud_secret_2026")
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL",
        "sqlite:///" + os.path.join(BASE_DIR, "instance", "game_hub.db")
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
