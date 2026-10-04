"""Application entry point for Flask."""

import os
from app import create_app
from config import config_by_name

env = os.getenv("FLASK_ENV", "development")
app = create_app(config_by_name.get(env))

if __name__ == "__main__":
    app.run(debug=app.config.get("DEBUG", False))
