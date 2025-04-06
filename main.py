from backend.app import app

# The Flask application is imported from backend/app.py
# This file exists to make the app importable by gunicorn

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)