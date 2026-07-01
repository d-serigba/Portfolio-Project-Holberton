from flask import Blueprint, jsonify

jeux_bp = Blueprint("jeux", __name__)

JEUX = [
    {
        "id"         : "metroidvania",
        "nom"        : "Arnaud's Bizarre Adventure",
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
        "id"         : "platformer",
        "nom"        : "City Runner",
        "description": "Platformer 2D urbain",
        "status"     : "coming_soon",
        "image"      : "/static/platformer.png"
    },
    {
        "id"         : "zelda",
        "nom"        : "Urban Explorer",
        "description": "Zelda-like urbain",
        "status"     : "coming_soon",
        "image"      : "/static/zelda.png"
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
