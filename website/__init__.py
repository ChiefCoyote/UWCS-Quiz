import os
from flask import Flask
from dotenv import load_dotenv, dotenv_values


def create_app():
    app = Flask(__name__)
    load_dotenv()
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')

    from .views import views
    from .auth import auth
    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(auth, url_prefix='/')

    return app
