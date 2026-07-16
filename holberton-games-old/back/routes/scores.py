from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import Score, User
from models import db

scores_bp = Blueprint("scores", __name__)

@scores_bp.route("/submit", methods=["POST"])
@jwt_required()
def submit_score():
    user_id = int(get_jwt_identity())
    data    = request.get_json()
    score   = Score(
        user_id    = user_id,
        jeu        = data.get("jeu", "inconnu"),
        score      = data.get("score", 0),
        completion = data.get("completion", 0),
        temps_jeu  = data.get("temps_jeu", 0)
    )
    db.session.add(score)
    db.session.commit()
    return jsonify({"message": "Score enregistré", "score": score.to_dict()}), 201

@scores_bp.route("/classement/<jeu>", methods=["GET"])
def classement(jeu):
    scores = (Score.query
              .filter_by(jeu=jeu)
              .order_by(Score.score.desc())
              .limit(10)
              .all())
    result = []
    for s in scores:
        user = User.query.get(s.user_id)
        result.append({
            "username"  : user.username,
            "score"     : s.score,
            "completion": s.completion,
        })
    return jsonify(result), 200

@scores_bp.route("/classement", methods=["GET"])
def classement_global():
    from sqlalchemy import func
    top = (db.session.query(
                User.username,
                func.sum(Score.score).label("total")
           )
           .join(Score, User.id == Score.user_id)
           .group_by(User.id)
           .order_by(func.sum(Score.score).desc())
           .limit(10)
           .all())
    return jsonify([{"username": r[0], "total": r[1]} for r in top]), 200
