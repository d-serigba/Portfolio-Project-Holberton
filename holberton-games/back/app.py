from flask import Flask
from flask_jwt_extended import JWTManager
from models import db
from config import Config
from flask_cors import CORS

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

    with app.app_context():
        db.create_all()

    return app

if __name__ == "__main__":
    app = create_app()
    app.run(debug=True, port=5000)
