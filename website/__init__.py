import os
from flask import Flask
from flask_login import LoginManager
from flask_mail import Mail
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv, dotenv_values
from os import path
from .email import mail

resetDB = True

db = SQLAlchemy()
DB_NAME = "db.sqlite"

def create_app():
    app = Flask(__name__)
    load_dotenv()
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_NAME}'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['MAIL_SUPPRESS_SEND'] = False
    app.config['MAIL_SERVER'] = "smtp.gmail.com"
    app.config['MAIL_PORT'] = 465
    app.config['MAIL_USERNAME'] = "noreplycs261@gmail.com"
    app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')
    app.config['MAIL_USE_TLS'] = False
    app.config['MAIL_USE_SSL'] = True

    db.init_app(app)
    mail.init_app(app)

    login_manager = LoginManager()
    login_manager.login_view = "auth.login"
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(userID):
        return User.query.get(int(userID))

    from .views import views
    from .auth import auth
    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(auth, url_prefix='/')

    from .models import User
    with app.app_context():
        if resetDB or (not path.exists('instance/' + DB_NAME)):
            reset_database()

    return app

def reset_database():
    db.drop_all()
    db.create_all()
    print('Reset')