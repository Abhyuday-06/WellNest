from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_mail import Mail
import logging

db = SQLAlchemy()
login_manager = LoginManager()
mail = Mail()

def create_app():
    app = Flask(__name__)
    app.config.from_object("config.Config")

    db.init_app(app)
    login_manager.init_app(app)
    mail.init_app(app)

    # Logging configuration
    logging.basicConfig(filename="logs/app.log", level=logging.INFO)


    # Register blueprints
    from routes import auth_bp, dashboard_bp, error_bp, reports_bp, chat_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(error_bp)
    app.register_blueprint(reports_bp)
    app.register_blueprint(chat_bp)

    return app
