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
from db_models import ChatUser, ChatMessage, ChatRoom


@login_manager.user_loader
def load_user(id):
    with Session(db.engine) as session:
        return session.get(ChatUser, int(id))


@app.route("/", methods=["POST", "GET"])
@app.route("/register", methods=["POST", "GET"])
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
    if current_user.is_authenticated:
        return redirect(url_for("private_chat"))

    login_form = LoginForm()
    if login_form.validate_on_submit():
        user = ChatUser.query.filter_by(
            username=login_form.username.data
        ).first()
        if user:
            login_user(user, remember=True)
            session.permanent = True
            return redirect(url_for("private_chat"))
        flash("Invalid username or password", "error")
    return render_template("login.html", form=login_form)

@login_manager.unauthorized_handler
def unauthorized():
    flash("You must be logged in to view this page.")
    return redirect(url_for("login", next=request.url))


@app.route("/logout", methods=["GET"])
def logout():
    logout_user()
    session.clear()
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


# Room chat ##
##############

@socketio.on("message", namespace='/room_chat')
def handle_message(data: MessageData):
    try:
        msg = data["msg"]
        username = data["username"]
        room = data["room"]
        created_at = strftime("%Y-%m-%d %H:%M:%S", gmtime())

        user = ChatUser.query.filter_by(username=username).first()
        chat_message = ChatMessage(
            text=msg,
            user_id=user.id,
            created_at=created_at,
            room=room,  # type: ignore
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


@socketio.on("join", namespace='/room_chat')
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


@socketio.on("leave", namespace='/room_chat')
def on_leave(data: Dict[str, Any]):
    username = data.get("username")
    room = data.get("room")
    if room and username:
        leave_room(room)
        emit("message", {"msg": f"{username} has gone off the {room} room"}, to=room)
        



## Create new Room ##

@app.route("/create_room", methods=["GET", "POST"])
def create_room():
    if request.method == "POST":
        roomname = request.form.get("roomname")
        code = request.form.get("code")

        if not roomname:
            return render_template(
                "create_room.html",
                error="Please enter a room name",
                random_code=generate_code(6),
            )

        if not code:
            return render_template(
                "create_room.html",
                error="Please enter a room code",
                random_code=generate_code(6),
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


# # private_message.py #

## Add/Chat a friend

rooms = {}
@app.route('/private_chat', methods=['GET', 'POST'])
@login_required
def private_chat():
    username = current_user.username
    session.clear()
    if request.method == 'POST':
        code = request.form.get("code")
        
        if not username:
            return render_template(
                "private_chat.html",
                error="Please enter a username",
                random_code=generate_code(10)
            )
        if not code:
            return render_template(
                "private_chat.html",
                error="Please enter a unique code",
                random_code=generate_code(10),
                name=username,
            )
        
        room = code
        rooms[room] = {"members": 0, "messages": []}
        if room not in rooms:
            return render_template(
                "private_chat.html",
                name=username,
                random_code=room,
                error="Room does not exist",
            )

        session['room'] = room
        
        return redirect(url_for("chat_now"))

    return render_template(
        "private_chat.html", random_code=generate_code(10), username=username
    )


@app.route('/chat_now')
@login_required
def chat_now():
    name = current_user.username
    room = session.get('room')
    
    code = room

    if room is None or name is None or room not in rooms:
        return redirect(url_for("private_chat"))

    return render_template('load.html', name=name, random_code=code, messages=rooms[room]['messages'])
    


@socketio.on('connect', namespace='/chat_now')
def on_connect(auth):
    print(f"\nConnected!!!!\n\n")

    name = current_user.username
    room = session.get('room')
    
    print(f"Room: \n\n{room}\n\n")
    print(f"Name: \n\n{name}\n\n")
    
    if not name or not room:
        return
    
    if room not in rooms:
        leave_room(room)
        return
    
    join_room(room)
    send({'name': name, "message": "has entered the room"}, to=room) # type: ignore
    rooms[room]['members'] += 1
    print(f"{name} joined room {room}")
    

@socketio.on('disconnect', namespace="/chat_now")
def on_disconnect():
    print(f"\n\n\ndiscConnected!!!!\n\n")

    name = session.get('name')
    room = session.get('room')
    
    if room and name:
        leave_room(room)
        
    if room in rooms:
        rooms[room]['members'] -= 1
        if rooms[room]['members'] <= 0:
            del rooms[room]
            send({"name": name, "message": "has left the room"}, to=room)  # type: ignore
            print(f"{name} left room {room}")
            return(url_for('private_chat'))
  

    return redirect(url_for('private_chat'))  

@socketio.on("message", namespace="/chat_now")
def message(data):
    room = session.get('room')
    if room not in rooms:
        return
    
    content = {
        "name": session.get('name'),
        "message": data['data']
    }
    send(content, to=room) # type: ignore
    rooms[room]['messages'].append(content)
    print(f"{session.get('name')} said: {data['data']}")


@socketio.on("message", namespace="/private_chat")
def handle_private_message(data: MessageData):
    try:
        msg = data["msg"]
        username = data["username"]
        room = data["room"]
        created_at = strftime("%Y-%m-%d %H:%M:%S", gmtime())

        user = ChatUser.query.filter_by(username=username).first()
        chat_message = ChatMessage(
            text=msg,
            user_id=user.id,
            created_at=created_at,
            room=room,  # type: ignore
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


@socketio.on("join", namespace="/private_chat")
def on_private_join(data: Dict[str, Any]):
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