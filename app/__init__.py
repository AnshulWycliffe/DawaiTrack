from flask import Flask
from app.config.settings import BaseConfig
from app.extensions.database import init_db
from app.extensions.login_manager import login_manager

from app.routes.auth_routes import auth_bp
from app.routes.main_routes import main_bp
from app.routes.pharmacy_routes import pharmacy_bp
from app.routes.admin_routes import admin_bp
from app.routes.cart_routes import cart_bp
from app.routes.order_routes import order_bp


def create_app():
    app = Flask(__name__)
    app.config.from_object(BaseConfig)

    init_db(app)
    login_manager.init_app(app)

    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(pharmacy_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(cart_bp)
    app.register_blueprint(order_bp)

    return app