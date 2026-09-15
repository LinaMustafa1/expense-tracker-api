from flask import Flask, jsonify
from flask_jwt_extended import JWTManager
from config import Config
from models import db
from auth import auth_bp
from expenses import expenses_bp


def create_app():
    app = Flask(__name__)

    app.config.from_object(Config)

    db.init_app(app)
    JWTManager(app)

    app.register_blueprint(auth_bp)
    app.register_blueprint(expenses_bp)

    with app.app_context():
        db.create_all()

    @app.route("/")
    def home():
        return jsonify({"message": "Expense Tracker API is running"})

    return app


app = create_app()


if __name__ == "__main__":
    app.run(debug=True)