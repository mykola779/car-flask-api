from flask import Blueprint, request, jsonify, abort
from flask_jwt_extended import (
    JWTManager, jwt_required, create_access_token, get_jwt, get_jwt_identity
)
from werkzeug.security import generate_password_hash, check_password_hash
from models import db, Car, User, RevokedToken
from flask_jwt_extended import JWTManager

jwt = JWTManager()


__all__ = ["cars_bp", "auth_bp", "jwt"]


auth_bp = Blueprint("auth", __name__, url_prefix="/auth")


cars_bp = Blueprint("cars", __name__, url_prefix="/cars")


# ---------- Authentication Routes ----------

@auth_bp.route("/login", methods=["POST"])
def login():
    """Login and generate JWT token."""
    data = request.json
    username = data.get("username")
    password = data.get("password")

    if not username or not password:
        return jsonify({"message": "Username and password are required"}), 400

    user = User.query.filter_by(username=username).first()
    if not user or not check_password_hash(user.password, password):
        return jsonify({"message": "Invalid credentials"}), 401

    access_token = create_access_token(identity=user.id)
    return jsonify({"access_token": access_token})


@auth_bp.route("/logout", methods=["POST"])
@jwt_required()
def logout():
    """Logout by revoking the JWT token."""
    jti = get_jwt()["jti"]
    revoked_token = RevokedToken(jti=jti)
    db.session.add(revoked_token)
    db.session.commit()
    return jsonify({"message": "Access token revoked"}), 200


@jwt.token_in_blocklist_loader
def check_if_token_revoked(jwt_header, jwt_payload):
    """Check if the JWT token has been revoked."""
    jti = jwt_payload["jti"]
    token = RevokedToken.query.filter_by(jti=jti).first()
    return token is not None


@auth_bp.route("/register", methods=["POST"])
def register():
    """Register a new user."""
    data = request.json
    username = data.get("username")
    password = data.get("password")

    if not username or not password:
        return jsonify({"message": "Username and password are required"}), 400

    if User.query.filter_by(username=username).first():
        return jsonify({"message": "User already exists"}), 400

    hashed_password = generate_password_hash(password)
    new_user = User(username=username, password=hashed_password)
    db.session.add(new_user)
    db.session.commit()
    return jsonify({"message": "User registered successfully"}), 201


# ---------- Cars Routes (CRUD) ----------

@cars_bp.route("/", methods=["GET"])
@jwt_required()
def get_all_cars():
    """Get all cars."""
    cars = Car.query.all()
    return jsonify([car.to_dict() for car in cars])


@cars_bp.route("/<int:car_id>", methods=["GET"])
@jwt_required()
def get_car(car_id):
    """Get a single car by ID."""
    car = Car.query.get_or_404(car_id)
    return jsonify(car.to_dict())


@cars_bp.route("/", methods=["POST"])
@jwt_required()
def create_car():
    """Create a new car."""
    data = request.json
    if not data:
        return jsonify({"message": "No data provided"}), 400

    try:
        new_car = Car(**data)
        db.session.add(new_car)
        db.session.commit()
        return jsonify(new_car.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": f"Error creating car: {str(e)}"}), 400


@cars_bp.route("/<int:car_id>", methods=["PUT"])
@jwt_required()
def update_car(car_id):
    """Update an existing car."""
    car = Car.query.get_or_404(car_id)
    data = request.json
    if not data:
        return jsonify({"message": "No data provided"}), 400

    try:
        for key, value in data.items():
            setattr(car, key, value)
        db.session.commit()
        return jsonify(car.to_dict())
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": f"Error updating car: {str(e)}"}), 400


@cars_bp.route("/<int:car_id>", methods=["DELETE"])
@jwt_required()
def delete_car(car_id):
    """Delete a car."""
    car = Car.query.get_or_404(car_id)
    try:
        db.session.delete(car)
        db.session.commit()
        return jsonify({"message": "Car deleted"})
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": f"Error deleting car: {str(e)}"}), 400


@cars_bp.route("/protected", methods=["GET"])
@jwt_required()
def protected():
    """Example protected route."""
    current_user_id = get_jwt_identity()
    return jsonify({"message": f"Hello, user {current_user_id}!"})
