from flask import Blueprint, jsonify

jeux_bp = Blueprint("jeux", __name__)

JEUX = [
    {
        "id"         : "metroidvania",
        "nom"        : "Arnaud Metroidvania",
        "description": "Metroidvania pixel art — banlieue urbaine",
        "status"     : "available",
        "image"      : "/static/metroidvania.png"
    },
    {
        "id"         : "fighting",
        "nom"        : "Versus Fighting",
        "description": "Jeu de combat 2D style Street Fighter",
        "status"     : "available",
        "image"      : "/static/fighting.png"
    },
    {
        "id"         : "arnaud",
        "nom"        : "Arnaud's Bizarre Adventure",
        "description": "Zelda-like urbain",
        "status"     : "available",
        "image"      : "/static/zelda.png"
    },
    {
        "id"         : "platformer",
        "nom"        : "City Runner",
        "description": "Platformer 2D urbain",
        "status"     : "coming_soon",
        "image"      : "/static/platformer.png"
    },
]

@jeux_bp.route("/", methods=["GET"])
def liste_jeux():
    return jsonify(JEUX), 200

@jeux_bp.route("/<jeu_id>", methods=["GET"])
def detail_jeu(jeu_id):
    jeu = next((j for j in JEUX if j["id"] == jeu_id), None)
    if not jeu:
        return jsonify({"error": "Jeu non trouvé"}), 404
    return jsonify(jeu), 200
