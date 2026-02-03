# app.py - Entry point for the Flask application

from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin
from routes import auth_bp, dashboard_bp, error_bp, reports_bp
from config import Config
from utils import create_app, db, login_manager
from models import User, MentalHealthQuizResult, Message
from flask_migrate import Migrate

app = create_app()
migrate = Migrate(app, db)
app.config.from_object(Config)

login_manager.login_view = 'auth.login'

@login_manager.user_loader
def load_user(user_id):
    user = db.session.get(User, int(user_id))
    return user

@app.route('/')
def home():
    return render_template('home.html')

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
