from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import hashlib

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = "users"
    id         = db.Column(db.Integer, primary_key=True)
    username   = db.Column(db.String(50), unique=True, nullable=False)
    password   = db.Column(db.String(256), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    scores     = db.relationship("Score", backref="user", lazy=True)

    def set_password(self, mdp):
        self.password = hashlib.sha256(mdp.encode()).hexdigest()

    def check_password(self, mdp):
        return self.password == hashlib.sha256(mdp.encode()).hexdigest()

    def to_dict(self):
        return {"id": self.id, "username": self.username}


class Score(db.Model):
    __tablename__ = "scores"
    id         = db.Column(db.Integer, primary_key=True)
    user_id    = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    jeu        = db.Column(db.String(50), nullable=False)
    score      = db.Column(db.Integer, default=0)
    completion = db.Column(db.Integer, default=0)
    temps_jeu  = db.Column(db.Integer, default=0)
    date       = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id"        : self.id,
            "user_id"   : self.user_id,
            "jeu"       : self.jeu,
            "score"     : self.score,
            "completion": self.completion,
            "temps_jeu" : self.temps_jeu,
            "date"      : self.date.isoformat()
        }
