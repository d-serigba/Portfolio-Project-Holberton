import os

class Config:
    SECRET_KEY     = os.environ.get("SECRET_KEY", "arnaud_game_hub_secret_2026")
    JWT_SECRET_KEY = os.environ.get("JWT_SECRET_KEY", "jwt_arnaud_secret_2026")
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL",
        "sqlite:///game_hub.db"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
