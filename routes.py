# routes.py
from flask import render_template, session, redirect, url_for, flash, request
from flask_login import login_user, current_user, logout_user, login_required
from sqlalchemy.orm import Session
from passlib.hash import pbkdf2_sha256
from forms import LoginForm, RegistrationForm
from config import app, db, login_manager, socketio
from utils import generate_code
from datetime import datetime
from flask_socketio import emit, send, join_room, leave_room
from time import gmtime, strftime
from typing import Any, Dict, TypedDict
from db_models import ChatUser, ChatMessage, ChatRoom, Friends


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
        login_user(user_object, remember=True)
        if current_user.is_authenticated:
            session.permanent = True
            return redirect(url_for("room_chat"))
        flash("Invalid Credentials", "danger")
    return render_template("login.html", form=login_form)


@app.route("/logout", methods=["GET"])
def logout():
    logout_user()
    flash("Logged out successfully", "warning")
    return redirect(url_for("login"))


@app.route("/room_chat", methods=["POST", "GET"])
@login_required
def room_chat():
    return render_template(
        "room_chat.html",
        username=current_user.username,
    )


class MessageData(TypedDict):
    msg: str
    username: str
    room: str


@socketio.on("message", namespace="/room_chat")
def handle_message(data: MessageData):
    if not all(key in data for key in ["msg", "username", "room"]):
        print("Invalid data received:", data)
        return

    try:
        msg = data["msg"]
        username = data["username"].strip()
        room = data["room"]
        created_at = strftime("%Y-%m-%d %H:%M:%S", gmtime())

        user = ChatUser.query.filter_by(username=username).first()
        if user is None:
            print(f"User not found for username: {username}")
            return  # or handle the error appropriately
        

        chat_message = ChatMessage(
            text=msg,
            user_id=user.id,  # type: ignore
            created_at=created_at,
            room=room,
        )  # type: ignore
        db.session.add(chat_message)
        db.session.commit()

        send(
            {"msg": msg, "username": username, "created_at": created_at},  # type: ignore
            room=room,
            broadcast=True,
        )
    except Exception as e:
        print(f"Error saving message: {e}")


@socketio.on("join", namespace="/room_chat")
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


@socketio.on("leave", namespace="/room_chat")
def on_leave(data: Dict[str, Any]):
    username = data.get("username")
    room = data.get("room")
    if room and username:
        leave_room(room)
        emit("message", {"msg": f"{username} has gone off the {room} room"}, to=room)


## Create new Room ##


@app.route("/create_room", methods=["GET", "POST"])
@login_required
def create_room():
    if request.method == "POST":
        roomname = request.form.get("roomname")
        code = request.form.get("code")

        if not roomname:
            return render_template(
                "create_room.html",
                error="Please enter a room name",
                random_code = generate_code(6),
            )

        if not code:
            return render_template(
                "create_room.html",
                error="Please enter a room code",
                random_code = generate_code(6),
            )

        existing_room = ChatRoom.query.filter_by(code=code).first()
        if existing_room:
            return render_template(
                "create_room.html",
                error="Room already exists",
                random_code=generate_code(6),
            )

        new_room = ChatRoom(roomname=roomname, code=code)  # type: ignore

        db.session.add(new_room)
        db.session.commit()

        return redirect(url_for("room_chat"))

    return render_template("create_room.html", random_code=generate_code(6))


## private_message.py

## Add/Chat a friend


@app.route("/add_friend", methods=["GET", "POST"])
@login_required
def add_friend():
    username = current_user.username
    session.clear()
    if request.method == "POST":
        code = request.form.get("code")
        friendname = request.form.get("friend-name")

        if not username:
            return render_template(
                "add_friend.html",
                error="Please enter a username",
                random_code=generate_code(10),
            )
        if not code:
            return render_template(
                "add_friend.html",
                error="Please enter a unique code",
                random_code=generate_code(10),
                username=username,
            )

        existing_friends = Friends.query.filter_by(code=code).first()
        if existing_friends:
            return render_template(
                "add_friend.html",
                error="User exists! Use another code",
                random_code=generate_code(10),
                username=username,
            )

        new_friend = Friends(friendname=friendname, code=code)  # type: ignore
        db.session.add(new_friend)
        db.session.commit()

        session["code"] = code

        return redirect(url_for("chat_now"))
    return render_template(
        "add_friend.html",
        random_code=generate_code(10),
        username=username,
        error="Nothing",
    )


@app.route("/chat_now")
@login_required
def chat_now():
    name = current_user.username
    code = session.get("code")

    if code is None or name is None:
        return redirect(url_for("add_friend"))

    return render_template("load.html", name=name, random_code=code)


@socketio.on("connect", namespace="/chat_now")
def on_connect():
    name = current_user.username
    chat_code = session.get("code")

    if not name or not chat_code:
        return

    existing_friends = Friends.query.all()
    friends = [friend.code for friend in existing_friends]
    
    if chat_code not in friends:
        leave_room(chat_code)
        return

    time = datetime.now()
    current_datetime = f"{time.hour:02d}:{time.minute:02d}"

    join_room(chat_code)
    send({"name": name, "msg": f"is online {current_datetime}"}, to=chat_code)  # type: ignore
    print(f"{name} joined room {chat_code}")
    

@socketio.on("disconnect", namespace="/chat_now")
def on_disconnect():
    name = session.get("name")
    chat_code = session.get("code")
    
    if chat_code and name:
        leave_room(chat_code)

    send({"name": name, "message": "has left the room"}, to=chat_code)  # type: ignore
    print(f"{name} left room {chat_code}")
    
    return redirect(url_for("add_friend"))


class MessageChat(TypedDict):
    msg: str
    friendname: str
    code: str


@socketio.on("sent_message", namespace="/chat_now")
def handle_private_message(data: MessageChat):
    try:
        msg = data["msg"]
        friendname = data["friendname"]
        chat_code = data["code"]
        created_at = strftime("%Y-%m-%d %H:%M:%S", gmtime())

        friend = Friends.query.filter_by(friendname=friendname).first()
        chat_message = ChatMessage(
            text=msg,
            user_id=friend.id,  # type: ignore
            created_at=created_at,
            room=chat_code,
        )
        
        db.session.add(chat_message)
        db.session.commit()
        
        emit("chat_message", {"msg":msg, "friendname":friendname, "created_at": created_at}, to=chat_code)
        
        
    except Exception as e:
        print(f"error saving message {e}")