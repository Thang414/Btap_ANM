"""
Application Factory for Ransomware Attack & Defense Simulator
"""

from flask import Flask
from config import SANDBOX_DIR
from app.core.crypto_engine import CryptoEngine
from app.core.defense_engine import DefenseEngine
from app.core.seed_data import reset_sandbox_environment
from app.routes.main_routes import main_bp
from app.routes.api_routes import api_bp


def create_app() -> Flask:
    app = Flask(__name__)
    app.config["SECRET_KEY"] = "academic-cybersecurity-lab-key-2026"

    # Initialize Core Security Engines
    crypto_engine = CryptoEngine()
    defense_engine = DefenseEngine()

    app.extensions["crypto_engine"] = crypto_engine
    app.extensions["defense_engine"] = defense_engine

    # Seed sandbox dummy files if empty
    existing_files = [f for f in SANDBOX_DIR.iterdir() if f.is_file()] if SANDBOX_DIR.exists() else []
    if not existing_files:
        reset_sandbox_environment(defense_engine)

    # Register Blueprints
    app.register_blueprint(main_bp)
    app.register_blueprint(api_bp)

    return app
