import subprocess
import os
import json
from flask import Flask, render_template, request, jsonify
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from jinja2 import TemplateNotFound
from models import db
from config import Config

jwt = JWTManager()

BASE = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Chemin de chaque jeu et de son fichier de session
JEUX = {
    "fighting": {
        "main"  : os.path.join(BASE, "docs", "fighter_games", "main.py"),
        "token" : os.path.join(BASE, "docs", "fighter_games", "save", "token.json"),
    },
    "metroidvania": {
        "main"  : os.path.join(BASE, "docs", "metroidvania", "main.py"),
        "token" : os.path.join(BASE, "docs", "metroidvania", "save", "token.json"),
    },
    "arnaud": {
        "main"  : os.path.join(BASE, "docs", "zelda-like", "arnaud_bizarre_adventure", "main.py"),
        "token" : None,  # ce jeu ne lit pas encore le token
    },
}


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

    # ==================== FRONT-END ====================

    @app.route("/")
    def home():
        return render_template("index.html")

    @app.route("/<jeu_id>.html")
    def page_jeu(jeu_id):
        try:
            return render_template(f"{jeu_id}.html")
        except TemplateNotFound:
            return "Page de jeu non trouvée", 404

    @app.route("/lancer/<jeu_id>")
    def lancer_jeu_local(jeu_id):
        jeu = JEUX.get(jeu_id)
        if not jeu or not os.path.exists(jeu["main"]):
            return jsonify({"error": f"Jeu non trouvé : {jeu_id}"}), 404

        token  = request.args.get("token")
        pseudo = request.args.get("player")

        try:
            # Écrit la session pour que le jeu la récupère au démarrage
            if token and pseudo and jeu["token"]:
                os.makedirs(os.path.dirname(jeu["token"]), exist_ok=True)
                with open(jeu["token"], "w", encoding="utf-8") as f:
                    json.dump({"token": token, "user": pseudo}, f)

            dossier = os.path.dirname(jeu["main"])
            subprocess.Popen(["py", "-3.12", jeu["main"]], cwd=dossier)
            return jsonify({"status": "lancé"}), 200
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    # ==============================================================

    with app.app_context():
        db.create_all()

    return app


app = create_app()

if __name__ == "__main__":
    app.run(debug=True, port=5000)
