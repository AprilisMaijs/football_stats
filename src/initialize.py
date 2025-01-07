import os
from database.database import init_db, SessionLocal, engine
from database.models import Base
from parsers.json_parser import MatchParser


def reset_database():
    """Drop all tables and recreate them"""
    print("Resetting database...")
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    print("Database reset complete")


def initialize_database():
    """Initialize the database and load match data"""
    print("Checking database...")

    # Reset database to ensure clean state
    reset_database()

    # Create database session
    db = SessionLocal()

    try:
        # Get path to data directory
        data_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data')

        if not os.path.exists(data_dir):
            print(f"Data directory not found at {data_dir}")
            return False

        # Create parser instance
        parser = MatchParser(db)

        # Get all JSON files sorted by name
        json_files = sorted([f for f in os.listdir(data_dir) if f.endswith('.json')])

        if not json_files:
            print("No JSON files found in data directory")
            return False

        print(f"Found {len(json_files)} match files to process")

        # Parse each file
        for filename in json_files:
            try:
                file_path = os.path.join(data_dir, filename)
                print(f"Processing {filename}...")
                parser.parse_file(file_path)
                db.commit()  # Commit after each successful file
                print(f"Successfully processed {filename}")
            except Exception as e:
                print(f"Error processing {filename}: {e}")
                db.rollback()  # Rollback on error
                continue  # Continue with next file

        print("\nData loading complete!")
        return True

    except Exception as e:
        print(f"An error occurred during initialization: {e}")
        return False
    finally:
        db.close()


if __name__ == "__main__":
    if initialize_database():
        print("Initialization completed successfully")
    else:
        print("Initialization failed")