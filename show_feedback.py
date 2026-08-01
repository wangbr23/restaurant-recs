import json
import os

from src.feedback import list_feedback
from web_app import app


def main():
    database_path = app.config["DATABASE_PATH"]
    os.makedirs(os.path.dirname(database_path), exist_ok=True)
    print(json.dumps(list_feedback(database_path), indent=2))


if __name__ == "__main__":
    main()
