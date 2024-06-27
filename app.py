# app.py
from datetime import datetime
from db_models import db, ChatUser, ChatMessage
from flask import Flask, render_template, redirect, url_for, flash, request
from flask_login import LoginManager, login_user, current_user, logout_user
from flask_socketio import SocketIO, emit, send, join_room, leave_room
from forms import LoginForm, RegistrationForm
from json import JSONEncoder
from sqlalchemy.orm import Session
from passlib.hash import pbkdf2_sha256
from typing import Any, Dict, TypedDict
from time import gmtime, strftime
import yaml

class CustomJSONEncoder(JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        return super().default(obj)

        
        
app = Flask(__name__)
app.secret_key = "supersecretkey"
app.json_encoder = CustomJSONEncoder # type: ignore

# Configure db
with open("db.yaml") as db_file:
    db_config = yaml.safe_load(db_file)


# Establish connection between (flask)app and MySQL database
user = db_config["mysql_user"]
passwd = db_config["mysql_password"]
host = db_config["mysql_host"]
database = db_config["mysql_db"]
port = db_config["mysql_port"]

app.config["SQLALCHEMY_DATABASE_URI"] = (
    f"mysql://{user}:{passwd}@{host}:{port}/{database}"
)

db.init_app(app)
socketio = SocketIO(app)
ROOMS = ["memes", "coding", "football", "philosphy"]

# configure flask login
login_manager = LoginManager()
login_manager.init_app(app)


@login_manager.user_loader
def load_user(id):
    with Session(db.engine) as session:
        return session.get(ChatUser, int(id))


@app.route("/", methods=["POST", "GET"])
def index():
    """Route for the registration page."""
    reg_form = RegistrationForm()

    # update database if validation successful
    if reg_form.validate_on_submit():
        fullname = reg_form.fullname.data
        username = reg_form.username.data
        sex = reg_form.sex.data
        password = reg_form.password.data

        # hash and encrypt password
        hashed_pswd = pbkdf2_sha256.hash(password)

        new_user = ChatUser(
            fullname=fullname,
            username=username,
            sex=sex,
            password=hashed_pswd,
        )

        db.session.add(new_user)
        db.session.commit()

        flash("Registered Successfully! You will be redirected to Login!", "success")
        return redirect(url_for("login"))

    return render_template("index.html", form=reg_form)


@app.route("/login", methods=["POST", "GET"])
def login():
    """Instantiates the instance of the login form"""
    login_form = LoginForm()

    if login_form.validate_on_submit():
        user_object = ChatUser.query.filter_by(
            username=login_form.username.data
        ).first()

        login_user(user_object, remember=False)
        if current_user.is_authenticated:
            return redirect(url_for("chat"))
        else:
            return "Not logged In"

    return render_template("login.html", form=login_form)


@app.route("/chat", methods=["POST", "GET"])
def chat():
    # if not current_user.is_authenticated:
    #     flash('Please login!', 'danger')
    #     return redirect(url_for('login'))

    # return "Ready to chat"
    return render_template("chat.html", username=current_user.username, rooms=ROOMS)


@app.route("/logout", methods=["GET"])
def logout():
    logout_user()
    flash("Logged out successfully", "warning")
    return redirect(url_for("login"))


class MessageData(TypedDict):
    msg: str
    username: str
    room: str


@socketio.on("message")
def handle_message(data: MessageData):
    try:
        msg = data["msg"]
        username = data["username"]
        room = data["room"]
        created_at = strftime("%Y-%m-%d %H:%M:%S", gmtime())
        
        user = ChatUser.query.filter_by(username=username).first()
        

        # Find user in the database
        user = ChatUser.query.filter_by(username=username).first()

        chat_message = ChatMessage(text=msg, user_id=user.id, created_at=created_at, room=room)  # type: ignore
        db.session.add(chat_message)
        db.session.commit()

        # Broadcast the message to the room
        send(
            {
                "msg": msg,
                "username": username,
                "created_at": created_at,
            },  # type: ignore
            room=room,
            broadcast=True,
        )
    except Exception as e:
        print(f"Error saving message: {e}")


@socketio.on("join")
def on_join(data: Dict[str, Any]):
    username = data.get("username")
    room = data.get("room")
    if room and username:
        join_room(room)

        # Load chat history from the database
        messages = (ChatMessage.query.filter_by(room=room).order_by(ChatMessage.created_at).all())
        chat_history = []
        for message in messages:
            chat_history.append({
                "msg": message.text,
                "username": message.user.username,
                "created_at": message.created_at,
            })
            
        # Get the current session id
        sid = request.sid # type: ignore
        
        # Send chat history to the user
        emit("chat_history", chat_history, to=sid)

        # Notify the room that the user has joined
        emit("message", {"msg": f"{username} has joined the {room} room "}, to=room)


@socketio.on("leave")
def on_leave(data: Dict[str, Any]):
    username = data.get("username")
    room = data.get("room")
    if room and username:
        leave_room(room)
        emit("message", {"msg": f"{username} has left the {room} room "}, to=room)


if __name__ == "__main__":
     with app.app_context():
        db.create_all()
     socketio.run(app, debug=True, use_reloader=True, log_output=True)
