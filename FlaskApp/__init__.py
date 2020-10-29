from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_user import SQLAlchemyAdapter, UserManager
from flask_bcrypt import Bcrypt
from flask import Flask
import os

app = Flask(__name__)


db = SQLAlchemy()
login_manager = LoginManager()
bcrypt = Bcrypt()

# Config
DATABASE_URL = os.environ['DATABASE_URL']

app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URL+"?sslmode=require"
app.config["SECRET_KEY"] = "A random key to use flask extensions that require encryption"

# Initialize other components
db.init_app(app)
login_manager.init_app(app)
login_manager.login_view = 'view.render_login_page'


bcrypt.init_app(app)
