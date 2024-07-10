# config.py
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_socketio import SocketIO
from flask_login import LoginManager
from json import JSONEncoder
from datetime import datetime
import yaml


class CustomJSONEncoder(JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        return super().default(obj)


app = Flask(__name__)
app.secret_key = "supersecretkey"
app.json_encoder = CustomJSONEncoder  # type: ignore

# Configure db
with open("db.yaml") as db_file:
    db_config = yaml.safe_load(db_file)

user = db_config["mysql_user"]
passwd = db_config["mysql_password"]
host = db_config["mysql_host"]
database = db_config["mysql_db"]
port = db_config["mysql_port"]

app.config["SQLALCHEMY_DATABASE_URI"] = (
    f"mysql://{user}:{passwd}@{host}:{port}/{database}"
)

db = SQLAlchemy()
socketio = SocketIO()
login_manager = LoginManager()


def init_app(app):
    db.init_app(app)
    socketio.init_app(app)
    login_manager.init_app(app)
