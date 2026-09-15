from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import create_access_token
from models import db, User

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/register", methods=["POST"])
def register():
    data = request.get_json()

    if not data:
        return jsonify({"error": "request body is required"}), 400

    email = data.get("email")
    password = data.get("password")

    if not email:
        return jsonify({"error": "email is required"}), 400

    if not password:
        return jsonify({"error": "password is required"}), 400

    if len(password) < 6:
        return jsonify({"error": "password must be at least 6 characters"}), 400

    existing_user = User.query.filter_by(email=email).first()

    if existing_user:
        return jsonify({"error": "email already exists"}), 409

    user = User(
        email=email,
        password_hash=generate_password_hash(password)
    )

    db.session.add(user)
    db.session.commit()

    return jsonify({"message": "user created"}), 201


@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json()

    if not data:
        return jsonify({"error": "request body is required"}), 400

    email = data.get("email")
    password = data.get("password")

    if not email:
        return jsonify({"error": "email is required"}), 400

    if not password:
        return jsonify({"error": "password is required"}), 400

    user = User.query.filter_by(email=email).first()

    if not user or not check_password_hash(user.password_hash, password):
        return jsonify({"error": "invalid email or password"}), 401

    token = create_access_token(identity=str(user.id))

    return jsonify({"access_token": token}), 200