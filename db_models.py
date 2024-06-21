# models.py
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin

db = SQLAlchemy()

class ChatUser(UserMixin, db.Model):
    """ChatUser Model"""
    __tablename__ = "chat_users"
    id       = db.Column(db.Integer, nullable=False, primary_key=True)
    fullname = db.Column(db.String(75))
    username = db.Column(db.String(15), nullable=False, unique=True)
    sex      = db.Column(db.String(10), nullable=False)
    password = db.Column(db.String(255), nullable=False)
    