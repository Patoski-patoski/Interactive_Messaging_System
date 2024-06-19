# app.py

from flask import Flask, render_template
from forms import *
from db_models import db, ChatUser 

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

@app.route('/', methods=['POST', 'GET'])
def index():
    # Instantiates the instance of the registration form
    form = RegistrationForm()
        
    if form.validate_on_submit():
        fullname = form.fullname.data
        username = form.username.data
        sex = form.sex.data
        password = form.confirm_password.data
        
        
        # Else Creates a new user 
        new_user = ChatUser(fullname=fullname, username=username, sex=sex, password=password)
        
        db.session.add(new_user)
        db.session.commit()
        
        return "Inserted into a database"
        
    return render_template('index.html', form=form)


if __name__ == "__main__":
    app.run(debug=True)
    