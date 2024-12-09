from flask import Flask
from flask_jwt_extended import JWTManager
from models import db
from routes import cars_bp, auth_bp, jwt 
from config import Config

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    db.init_app(app)
    jwt.init_app(app)

    with app.app_context():
        db.create_all()

    app.register_blueprint(cars_bp)
    app.register_blueprint(auth_bp)
    return app


if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)
