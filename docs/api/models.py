from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import hashlib
import hmac
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()


class User(db.Model):
    __tablename__ = "users"
    id              = db.Column(db.Integer, primary_key=True)
    username        = db.Column(db.String(50), unique=True, nullable=False)
    password        = db.Column(db.String(256), nullable=False)
    # ID de la session active (une seule à la fois). NULL = déconnecté.
    current_session = db.Column(db.String(36), nullable=True)
    created_at      = db.Column(db.DateTime, default=datetime.utcnow)
    scores          = db.relationship("Score", backref="user", lazy=True)

    def set_password(self, mdp):
        # scrypt avec sel aléatoire (format "scrypt:N:r:p$sel$hash")
        self.password = generate_password_hash(mdp)

    def check_password(self, mdp):
        # Anciens comptes : SHA-256 sans sel (64 caractères hexa, sans "$")
        if "$" not in self.password:
            ancien = hashlib.sha256(mdp.encode()).hexdigest()
            if not hmac.compare_digest(self.password, ancien):
                return False
            # Bon mot de passe : on migre vers scrypt (commit fait par la route /login)
            self.set_password(mdp)
            return True
        return check_password_hash(self.password, mdp)

    def to_dict(self):
        return {
            "id"        : self.id,
            "username"  : self.username,
            "created_at": self.created_at.isoformat()
        }


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
