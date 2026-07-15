import os

class Config:
    SECRET_KEY         = "arnaud_game_hub_secret_2026"
    JWT_SECRET_KEY     = "jwt_arnaud_secret_2026"
    SQLALCHEMY_DATABASE_URI = (
        "mysql+pymysql://game_user:GameHub_2026!@localhost/game_hub"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
