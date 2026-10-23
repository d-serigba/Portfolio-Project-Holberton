import subprocess
import os
from flask import Flask, render_template
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from models import db
from config import Config

jwt = JWTManager()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    CORS(app)

    db.init_app(app)
    jwt.init_app(app)

    from routes.auth   import auth_bp
    from routes.scores import scores_bp
    from routes.jeux   import jeux_bp

    app.register_blueprint(auth_bp,   url_prefix="/api/auth")
    app.register_blueprint(scores_bp, url_prefix="/api/scores")
    app.register_blueprint(jeux_bp,   url_prefix="/api/jeux")

    # ==================== ROUTES DU FRONT-END ====================

    @app.route("/")
    def home():
        return render_template("index.html")

    @app.route("/<jeu_id>.html")
    def page_jeu(jeu_id):
        try:
            return render_template(f"{jeu_id}.html")
        except:
            return "Page de jeu non trouvée", 404

    @app.route("/lancer/<jeu_id>")
    def lancer_jeu_local(jeu_id):
        # Remonte jusqu'à la racine Portfolio-Project-Holberton/
        BASE = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        jeux = {
            "fighting"    : os.path.join(BASE, "docs", "fighter_games", "main.py"),
            "metroidvania": os.path.join(BASE, "docs", "metroidvania", "main.py"),
            "arnaud"      : os.path.join(BASE, "docs", "zelda-like", "arnaud bizarre adventure", "main.py"),
        }
        chemin = jeux.get(jeu_id)
        if not chemin or not os.path.exists(chemin):
            return {"error": f"Jeu non trouvé : {chemin}"}, 404
        try:
            dossier = os.path.dirname(chemin)
            subprocess.Popen(["python3", chemin], cwd=dossier)
            return {"status": "lancé"}, 200
        except Exception as e:
            return {"error": str(e)}, 500

    # ==============================================================

    with app.app_context():
        db.create_all()

    return app

if __name__ == "__main__":
    app = create_app()
    app.run(debug=True, port=5000)
