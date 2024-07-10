# routes.py
from flask import render_template, redirect, url_for, flash, request
from flask_login import login_user, current_user, logout_user
from sqlalchemy.orm import Session
from passlib.hash import pbkdf2_sha256
from forms import LoginForm, RegistrationForm
from config import app, db, login_manager, socketio
from utils import generate_code
from datetime import datetime
from flask_socketio import emit, send, join_room, leave_room
from time import gmtime, strftime
from typing import Any, Dict, TypedDict
from db_models import ChatUser, ChatMessage, ChatRoom



@login_manager.user_loader
def load_user(id):
    with Session(db.engine) as session:
        return session.get(ChatUser, int(id))


@app.route("/", methods=["POST", "GET"])
def index():
    reg_form = RegistrationForm()
    if reg_form.validate_on_submit():
        fullname = reg_form.fullname.data
        username = reg_form.username.data
        sex = reg_form.sex.data
        password = reg_form.password.data
        hashed_pswd = pbkdf2_sha256.hash(password)
        new_user = ChatUser(
            fullname=fullname, username=username, sex=sex, password=hashed_pswd
        )
        db.session.add(new_user)
        db.session.commit()
        flash("Registered Successfully! You will be redirected to Login!", "success")
        return redirect(url_for("login"))
    return render_template("index.html", form=reg_form)


@app.route("/login", methods=["POST", "GET"])
def login():
    login_form = LoginForm()
    if login_form.validate_on_submit():
        user_object = ChatUser.query.filter_by(
            username=login_form.username.data
        ).first()
        login_user(user_object, remember=False)
        if current_user.is_authenticated:
            return redirect(url_for("chat"))
        flash("Invalid Credentials", "danger")
    return render_template("login.html", form=login_form)


@app.route("/chat", methods=["POST", "GET"])
def chat():
    return render_template(
        "chat.html",
        username=current_user.username,
    )
@app.route("/private", methods=["POST", "GET"])
def private_msg():
    return render_template(
        "private_msg.html",
        username=current_user.username,
    )


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
        chat_message = ChatMessage(
            text=msg, user_id=user.id, created_at=created_at, room=room # type: ignore
        )  # type: ignore
        db.session.add(chat_message)
        db.session.commit()
        
        send(
            {"msg": msg, "username": username, "created_at": created_at}, # type: ignore
            room=room,
            broadcast=True,
        )
    except Exception as e:
        print(f"Error saving message: {e}")
        


@socketio.on("join")
def on_join(data: Dict[str, Any]):
    username = data.get("username")
    room = data.get("room")

    time = datetime.now()
    current_datetime = f"{time.hour:02d}:{time.minute:02d}"

    if room and username:
        join_room(room)

        # Load chat history from the database
        messages = (
            ChatMessage.query.filter_by(room=room)
            .order_by(ChatMessage.created_at)
            .all()
        )
        chat_history = [
            {
                "msg": message.text,
                "username": message.user.username,
                "created_at": message.created_at,
            }
            for message in messages
        ]

        # Get the current session id
        sid = request.sid  # type: ignore
        emit("chat_history", chat_history, to=sid)
        emit(
            "message",
            {"msg": f"{username} has joined the {room} room :{current_datetime}"},
            to=room,
        )
        
        chat_rooms = ChatRoom.query.all()
        room_names = [room.roomname for room in chat_rooms]
        emit("loaded", room_names)

        
@socketio.on("leave")
def on_leave(data: Dict[str, Any]):
    username = data.get("username")
    room = data.get("room")
    if room and username:
        leave_room(room)
        emit("message", {"msg": f"{username} has gone off the {room} room"}, to=room)


#### Create new Room ####
    

@app.route("/create_room", methods=["GET", "POST"])
def create_room():
    if request.method == "POST":
        roomname = request.form.get("roomname")
        code = request.form.get("code")

        if not roomname:
            return render_template(
                "create_room.html",
                error="Please enter a room name",
                random_code=generate_code(),
            )

        if not code:
            return render_template(
                "create_room.html",
                error="Please enter a room code",
                random_code=generate_code(),
            )

        existing_room = ChatRoom.query.filter_by(code=code).first()
        if existing_room:
            return render_template(
                "create_room.html",
                error="Room already exists",
                random_code=generate_code(),
            )

        new_room = ChatRoom(roomname=roomname, code=code)  # type: ignore
        
        db.session.add(new_room)
        db.session.commit()
        
        return redirect(url_for("chat"))

    return render_template("create_room.html", random_code=generate_code())
