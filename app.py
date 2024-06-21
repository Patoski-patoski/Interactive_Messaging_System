# app.py
from flask import Flask, render_template, redirect, url_for
from flask_login import LoginManager, login_user, current_user, login_required, logout_user
from forms import *
from db_models import db, ChatUser 
from sqlalchemy.orm import Session



import yaml


app = Flask(__name__)
app.secret_key = "supersecretkey"

# Configure db
with open('db.yaml') as db_file:
    db_config = yaml.safe_load(db_file)


# Establish connection between (flask)app and MySQL database
user = db_config['mysql_user']
passwd = db_config['mysql_password']
host = db_config['mysql_host']
database = db_config['mysql_db']
port = db_config['mysql_port']

app.config['SQLALCHEMY_DATABASE_URI'] = f"mysql://{user}:{passwd}@{host}:{port}/{database}"

db.init_app(app)

# configure flask login
login = LoginManager(app)
login.init_app(app)

@login.user_loader
def load_user(id):
    with Session(db.engine) as session:
        return session.get(ChatUser, int(id))


@app.route('/', methods=['POST', 'GET'])
def index():
    """Route for the registration page."""
    reg_form = RegistrationForm()
    
    # update database if validation successful
    if reg_form.validate_on_submit():
        
         fullname = reg_form.fullname.data
         username = reg_form.username.data
         sex      = reg_form.sex.data
         password = reg_form.password.data
         
         # hash and encrypt password
         hashed_pswd = pbkdf2_sha256.hash(password)
        
         new_user = ChatUser(
            fullname=fullname,
            username = username,
            sex = sex,
            password = hashed_pswd,
        )
        
         db.session.add(new_user)
         db.session.commit()
        
         return redirect(url_for('login'))
        
    return render_template('index.html', form=reg_form)

@app.route('/login', methods=['POST', 'GET'])
def login():
    """Instantiates the instance of the login form"""
    login_form = LoginForm()
        
    if login_form.validate_on_submit():
        user_object = ChatUser.query.filter_by(
            username=login_form.username.data).first()
        
        login_user(user_object)
        if current_user.is_authenticated:
            return redirect(url_for('chat'))
        else:
            return "Not logged In"
    
    return render_template('login.html', form=login_form)


@app.route('/chat', methods=['POST', 'GET'])
# @login_required
def chat():
    
    if not current_user.is_authenticated:
        return "You must register/login to access chat"
    
    return "Ready to chat"


@app.route('/logout', methods=['GET'])
def logout():
    
    logout_user()
    return "Logged out using flask_login"

if __name__ == "__main__":
    app.run(debug=True)