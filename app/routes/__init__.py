"""
Route Blueprints registration
"""

from app.routes.api_routes import api_bp
from app.routes.main_routes import main_bp

__all__ = ["api_bp", "main_bp"]
