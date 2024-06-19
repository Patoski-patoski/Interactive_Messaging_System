# models.py

from flask import Flask, redirect, render_template, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import IntegrityError
from app import app

import yaml


# Configure db
with open('db.yaml') as db_file:
    db_config = yaml.safe_load(db_file)


# Establish connection between (flask)app and MySQL database
user = db_config['mysql_user']
passwd = db_config['mysql_password']
host = db_config['mysql_host']
database = db_config['mysql_db']
port = db_config['mysql_port']

app.config['SQLALCHEMY_DATABASE_URI'] = f"mysql://{user}:{passwd}@{host:port}/{database}"

# Instantiate the SQLALchemy object
db = SQLAlchemy(app)

class ChatUser(db.Model):
    """ChatUser Model"""
    __tablename__ = "chat_users"
    id               = db.Column(db.Integer, nullable=False, primary_key=True)
    fullname             = db.Column(db.String(75))
    username         = db.Column(db.String(15), nullable=False, unique=True)
    password = db.Column(db.String(60), nullable=False)
    




