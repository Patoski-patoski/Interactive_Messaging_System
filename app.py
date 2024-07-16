# app.py
from config import app, db, socketio, init_app
import routes  # Import routes to register them with the app
# import socket_events
import utils

init_app(app)

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    socketio.run(app, debug=True, use_reloader=True, log_output=True)
