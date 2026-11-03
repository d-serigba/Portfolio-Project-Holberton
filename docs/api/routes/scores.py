from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from sqlalchemy import func
from models import db, Score, User

scores_bp = Blueprint("scores", __name__)


@scores_bp.route("/submit", methods=["POST"])
@jwt_required()
def submit_score():
    user = db.session.get(User, int(get_jwt_identity()))
    sid = get_jwt().get("sid")

    # Refuse les tokens dont la session n'est plus active
    if not user or user.current_session != sid:
        return jsonify({"error": "Session expirée ou ouverte ailleurs"}), 401

    data = request.get_json(silent=True) or {}
    jeu = (data.get("jeu") or "").strip()
    if not jeu:
        return jsonify({"error": "jeu requis"}), 400

    score = Score(
        user_id=user.id,
        jeu=jeu,
        score=min(int(data.get("score", 0)), 9999),
        completion=int(data.get("completion", 0)),
        temps_jeu=int(data.get("temps_jeu", 0)),
    )
    db.session.add(score)
    db.session.commit()
    return jsonify({"message": "Score enregistré", "score": score.to_dict()}), 201


@scores_bp.route("/classement/<jeu>", methods=["GET"])
def classement(jeu):
    scores = (
        Score.query.filter_by(jeu=jeu)
        .order_by(Score.score.desc())
        .limit(10)
        .all()
    )
    result = []
    for s in scores:
        user = db.session.get(User, s.user_id)
        result.append({
            "username": user.username if user else "?",
            "score": s.score,
            "completion": s.completion,
            "temps_jeu": s.temps_jeu,
            "date": s.date.isoformat(),
        })
    return jsonify(result), 200


@scores_bp.route("/classement", methods=["GET"])
def classement_global():
    top = (
        db.session.query(
            User.username,
            func.sum(Score.score).label("total"),
        )
        .join(Score, User.id == Score.user_id)
        .group_by(User.id, User.username)
        .order_by(func.sum(Score.score).desc())
        .limit(10)
        .all()
    )
    return jsonify([{"username": r[0], "total": r[1]} for r in top]), 200
