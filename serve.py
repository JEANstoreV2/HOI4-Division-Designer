# Production entry point, separate from `app.py`'s own `python app.py`
# (which stays as the interactive dev workflow - Flask's built-in server,
# debug=True, auto-reloader). This one is what a persistent Windows
# service/scheduled task should point at instead: waitress is a real
# WSGI server (no "do not use in production" warning, no debug-mode
# in-browser code execution risk, no reloader spawning a second process
# under a service wrapper).
#
# Run directly with: .venv\Scripts\python.exe serve.py
from waitress import serve

from app import app

if __name__ == "__main__":
    serve(app, host="0.0.0.0", port=5000)
