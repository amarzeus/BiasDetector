from app import app
import logging
import os

# Configure logging
logging.basicConfig(level=logging.DEBUG)

if __name__ == "__main__":
    # Run the Flask application
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
