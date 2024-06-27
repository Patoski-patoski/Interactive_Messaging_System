# db_models.py
from flask_login import UserMixin
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import func

db = SQLAlchemy()


class ChatUser(db.Model, UserMixin):
    __tablename__ = "chat_users"

    id = db.Column(db.Integer, primary_key=True)
    fullname = db.Column(db.String(75), nullable=False)
    username = db.Column(db.String(75), unique=True, nullable=False)
    sex = db.Column(db.String(6), nullable=False)
    password = db.Column(db.String(255), nullable=False)

    def __init__(self, fullname: str, username: str, sex: str, password: str):
        self.fullname = fullname
        self.username = username
        self.sex = sex
        self.password = password

class ChatMessage(db.Model, UserMixin):
    __tablename__ = "messages"
    
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('chat_users.id'), nullable=False)
    room = db.Column(db.String(50), nullable=False)
    created_at = db.Column(db.String, nullable=False)
    user = db.relationship('ChatUser', backref="messages")