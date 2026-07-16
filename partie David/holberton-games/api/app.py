from flask import Flask, render_template  # Ajout de render_template pour servir le HTML
from flask_jwt_extended import JWTManager
from flask_cors import CORS  # Import de CORS
from models import db
from config import Config

jwt = JWTManager()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Activation de CORS pour autoriser ton frontend à requêter l'API
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
    
    # Route racine : affiche ton menu rétro (index.html)
    @app.route("/")
    def home():
        return render_template("index.html")

    # Route dynamique : redirige vers les fichiers metroidvania.html et fighting.html
    @app.route("/<jeu_id>.html")
    def lancer_jeu(jeu_id):
        try:
            return render_template(f"{jeu_id}.html")
        except:
            return "Page de jeu non trouvée", 404

    # ==============================================================

    with app.app_context():
        db.create_all()

    return app

if __name__ == "__main__":
    app = create_app()
    app.run(debug=True, port=5000)
