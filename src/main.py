from database.database import database_exists
from initialize import initialize_database
from src.interface.app import app


def main():
    # Initialize database only if it doesn't exist
    if not database_exists():
        initialize_database()

    # Start Flask app
    app.run(debug=True)


if __name__ == "__main__":
    main()