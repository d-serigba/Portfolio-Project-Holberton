from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()


class User(db.Model):
    __tablename__ = "users"
    id            = db.Column(db.Integer, primary_key=True)
    username      = db.Column(db.String(50), unique=True, nullable=False)
    password      = db.Column(db.String(256), nullable=False)
    # Token de la session active (une seule à la fois). NULL = déconnecté.
    session_token = db.Column(db.String(512), nullable=True)
    created_at    = db.Column(db.DateTime, default=datetime.utcnow)
    scores        = db.relationship("Score", backref="user", lazy=True)


class Score(db.Model):
    __tablename__ = "scores"
    id         = db.Column(db.Integer, primary_key=True)
    user_id    = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    jeu        = db.Column(db.String(50), nullable=False)
    score      = db.Column(db.Integer, default=0)
    completion = db.Column(db.Integer, default=0)
    temps_jeu  = db.Column(db.Integer, default=0)
    date       = db.Column(db.DateTime, default=datetime.utcnow)
