import uuid
from flask import Blueprint, request, jsonify
from flask_jwt_extended import (
    create_access_token,
    jwt_required,
    get_jwt_identity,
    get_jwt,
    decode_token,
)
from models import User, db

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/register", methods=["POST"])
def register():
    data = request.get_json(silent=True) or {}
    username = (data.get("username") or "").strip()
    password = data.get("password") or ""

    if not username or not password:
        return jsonify({"error": "username et password requis"}), 400
    if User.query.filter_by(username=username).first():
        return jsonify({"error": "username déjà pris"}), 409

    user = User(username=username)
    user.set_password(password)

    session_id = str(uuid.uuid4())
    user.current_session = session_id

    db.session.add(user)
    db.session.commit()

    token = create_access_token(
        identity=str(user.id),
        additional_claims={"sid": session_id}
    )
    return jsonify({"message": "Compte créé", "token": token, "user": user.to_dict()}), 201


@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json(silent=True) or {}
    username = (data.get("username") or "").strip()
    password = data.get("password") or ""

    user = User.query.filter_by(username=username).first()
    if not user or not user.check_password(password):
        return jsonify({"error": "Identifiants incorrects"}), 401

    # Session unique : une nouvelle connexion invalide automatiquement l'ancienne
    session_id = str(uuid.uuid4())
    user.current_session = session_id
    db.session.commit()

    token = create_access_token(
        identity=str(user.id),
        additional_claims={"sid": session_id}
    )
    return jsonify({"token": token, "user": user.to_dict()}), 200


@auth_bp.route("/logout", methods=["POST"])
@jwt_required()
def logout():
    user = User.query.get(int(get_jwt_identity()))
    if user:
        user.current_session = None
        db.session.commit()
    return jsonify({"message": "Déconnecté"}), 200


@auth_bp.route("/logout-beacon", methods=["POST"])
def logout_beacon():
    """Logout appelé par sendBeacon à la fermeture : token dans le body."""
    data = request.get_json(silent=True) or {}
    token = data.get("token")
    if not token:
        return jsonify({"error": "token requis"}), 400
    try:
        decoded = decode_token(token)
        user = User.query.get(int(decoded["sub"]))
        if user and user.current_session == decoded.get("sid"):
            user.current_session = None
            db.session.commit()
    except Exception:
        pass  # token expiré ou invalide : rien à libérer
    return jsonify({"message": "ok"}), 200


@auth_bp.route("/verify", methods=["GET"])
@jwt_required()
def verify():
    """Vérifie qu'un token est encore la session active de l'utilisateur."""
    user = User.query.get(int(get_jwt_identity()))
    sid = get_jwt().get("sid")
    if not user or user.current_session != sid:
        return jsonify({"error": "Session expirée ou ouverte ailleurs"}), 401
    return jsonify({"user": user.to_dict()}), 200
