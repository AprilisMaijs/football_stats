import os
import pathlib


def create_project_structure():
    # Define the base directory for the project
    base_dir = pathlib.Path.cwd()

    # Define directories to create
    directories = [
        'football_stats',
        'football_stats/database',
        'football_stats/parsers',
        'football_stats/statistics',
        'football_stats/utils',
        'football_stats/data'  # Directory for JSON files
    ]

    # Create directories
    for dir_path in directories:
        full_path = base_dir / dir_path
        full_path.mkdir(parents=True, exist_ok=True)
        print(f"Created directory: {full_path}")

    # Create __init__.py files
    init_dirs = [
        'football_stats',
        'football_stats/database',
        'football_stats/parsers',
        'football_stats/statistics',
        'football_stats/utils'
    ]

    for dir_path in init_dirs:
        init_file = base_dir / dir_path / '__init__.py'
        init_file.touch()
        print(f"Created file: {init_file}")

    # Create other necessary files
    files = {
        'football_stats/config.py': '# Configuration settings\nDATABASE_URL = "sqlite:///football_stats.db"\nDATA_DIR = "data"',
        'football_stats/main.py': '# Main entry point\n',
        'football_stats/database/models.py': '# Database models\n',
        'football_stats/database/database.py': '# Database connection\n',
        'football_stats/parsers/json_parser.py': '# JSON parsing logic\n',
        'football_stats/statistics/calculator.py': '# Statistics calculation\n',
        'football_stats/utils/helpers.py': '# Helper functions\n'
    }

    for file_path, content in files.items():
        full_path = base_dir / file_path
        with open(full_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Created file: {full_path}")


if __name__ == "__main__":
    create_project_structure()
    print("\nProject structure created successfully!")