import os
from flask import Flask
from dotenv import load_dotenv, dotenv_values


def create_app():
    app = Flask(__name__)
    load_dotenv()
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
