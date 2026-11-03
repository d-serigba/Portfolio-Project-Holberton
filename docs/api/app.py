import subprocess
import os
from flask import Flask, render_template, request, jsonify
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from jinja2 import TemplateNotFound
from models import db
from config import Config

jwt = JWTManager()

BASE = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Chemin de chaque jeu (la session est transmise par variables d'environnement)
JEUX = {
    "fighting": {
        "main": os.path.join(BASE, "docs", "fighter_games", "main.py"),
    },
    "metroidvania": {
        "main": os.path.join(BASE, "docs", "metroidvania", "main.py"),
    },
    "arnaud": {
        "main": os.path.join(BASE, "docs", "zelda-like", "arnaud_bizarre_adventure", "main.py"),
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
        # Liste blanche : seules les pages des jeux connus sont servies
        if jeu_id not in JEUX:
            return "Page de jeu non trouvée", 404
        try:
            return render_template(f"{jeu_id}.html")
        except TemplateNotFound:
            return "Page de jeu non trouvée", 404

    @app.route("/lancer/<jeu_id>")
    def lancer_jeu_local(jeu_id):
        # Lancement autorisé uniquement depuis la machine locale
        if request.remote_addr not in ("127.0.0.1", "::1"):
            return jsonify({"error": "Accès refusé"}), 403

        jeu = JEUX.get(jeu_id)
        if not jeu or not os.path.exists(jeu["main"]):
            return jsonify({"error": f"Jeu non trouvé : {jeu_id}"}), 404

        token  = request.args.get("token")
        pseudo = request.args.get("player")

        try:
            # Session transmise au jeu par l'environnement du processus :
            # chaque lancement a sa propre session, rien n'est stocké sur disque
            env = os.environ.copy()
            env.pop("GAME_TOKEN", None)
            env.pop("GAME_USER", None)
            if token and pseudo:
                env["GAME_TOKEN"] = token
                env["GAME_USER"]  = pseudo

            dossier = os.path.dirname(jeu["main"])
            subprocess.Popen(["py", "-3.12", jeu["main"]], cwd=dossier, env=env)
            return jsonify({"status": "lancé"}), 200
        except Exception as e:
            app.logger.exception("Erreur au lancement du jeu %s", jeu_id)
            return jsonify({"error": "Impossible de lancer le jeu"}), 500

    # ==============================================================

    with app.app_context():
        db.create_all()

    return app


app = create_app()

if __name__ == "__main__":
    app.run(debug=True, port=5000)
