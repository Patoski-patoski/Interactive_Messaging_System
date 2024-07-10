# db_models.py
from flask_login import UserMixin
from config import db

# db = SQLAlchemy()


class ChatUser(db.Model, UserMixin):
    """
    A class that represents a chat user in the database.

    This class inherits from the `db.Model` and `UserMixin` classes, which provide the necessary
    functionality for working with SQLAlchemy and Flask-Login, respectively.

    Attributes:
        id (int): The unique identifier for the chat user.
        fullname (str): The full name of the chat user.
        username (str): The unique username of the chat user.
        sex (str): The sex of the chat user.
        password (str): The hashed password of the chat user.

    Methods:
        __init__(self, fullname: str, username: str, sex: str, password: str):
            Initializes a new `ChatUser` instance with the provided attributes.
    """

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
    """
    A class that represents a chat message in the database.

    This class inherits from the `db.Model` and `UserMixin` classes, which provide the necessary
    functionality for working with SQLAlchemy and Flask-Login, respectively.

    Attributes:
        id (int): The unique identifier for the chat message.
        text (str): The text content of the chat message.
        user_id (int): The ID of the user who sent the message.
        room (str): The name of the chat room where the message was sent.
        created_at (str): The timestamp of when the message was created.
        user (ChatUser): The user object associated with the message.
    """

    __tablename__ = "chat_messages"

    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("chat_users.id"), nullable=False)
    room = db.Column(db.String(50), nullable=True)
    created_at = db.Column(db.String(50), nullable=False)
    user = db.relationship("ChatUser", foreign_keys=[user_id], backref="sent_messages")
    recipient_id = db.Column(db.Integer, db.ForeignKey("chat_users.id"), nullable=True)
    recipient = db.relationship(
        "ChatUser", foreign_keys=[recipient_id], backref="received_messages"
    )


class ChatRoom(db.Model):
    """
    A class that represents a chat room in the database.

    This class inherits from the `db.Model` class, which provides the necessary
    functionality for working with SQLAlchemy.

    Attributes:
        id (int): The unique identifier for the chat room.
        name (str): The name of the chat room.
        code (str): The unique code for the chat room.

    Methods:
        __init__(self, name: str):
            Initializes a new `ChatRoom` instance with the provided name.
    """
    __tablename__ = "chat_rooms"

    id = db.Column(db.Integer, primary_key=True)
    roomname = db.Column(db.String(50), nullable=False)
    code = db.Column(db.String(7), unique=True, nullable=False)

    def __init__(self, roomname: str, code: str):
        self.roomname = roomname
        self.code = code
