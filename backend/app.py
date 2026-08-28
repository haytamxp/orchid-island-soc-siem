"""
Orchid Island SOC/SIEM
Flask backend entry point.
"""

from flask import Flask, jsonify
from flask_cors import CORS

from backend.routes.auth import auth_bp


def create_app() -> Flask:
    """
    Application factory.

    Creates and configures the Flask application.
    """

    app = Flask(__name__)

    CORS(
        app,
        resources={
            r"/api/*": {
                "origins": "*"
            }
        }
    )

    app.register_blueprint(auth_bp)

    @app.route(
        "/",
        methods=["GET"]
    )
    def index():
        return jsonify({
            "service": "Orchid Island SOC/SIEM",
            "status": "running",
            "version": "1.0.0"
        })

    @app.route(
        "/api/health",
        methods=["GET"]
    )
    def health():
        return jsonify({
            "status": "ok"
        })

    return app


app = create_app()


if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=5000,
        debug=False
    )