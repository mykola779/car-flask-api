from flask import Blueprint, request, jsonify, abort
from models import db, Car

bp = Blueprint("cars", __name__, url_prefix="/cars")

@bp.route("/", methods=["GET"])
def get_all_cars():
    cars = Car.query.all()
    return jsonify([car.to_dict() for car in cars])

@bp.route("/<int:car_id>", methods=["GET"])
def get_car(car_id):
    car = Car.query.get_or_404(car_id)
    return jsonify(car.to_dict())

@bp.route("/", methods=["POST"])
def create_car():
    data = request.json
    new_car = Car(**data)
    db.session.add(new_car)
    db.session.commit()
    return jsonify(new_car.to_dict()), 201

@bp.route("/<int:car_id>", methods=["PUT"])
def update_car(car_id):
    car = Car.query.get_or_404(car_id)
    data = request.json
    for key, value in data.items():
        setattr(car, key, value)
    db.session.commit()
    return jsonify(car.to_dict())

@bp.route("/<int:car_id>", methods=["DELETE"])
def delete_car(car_id):
    car = Car.query.get_or_404(car_id)
    db.session.delete(car)
    db.session.commit()
    return jsonify({"message": "Car deleted"})
