import sys
import os

# Add the parent directory to sys.path so we can import from sibling directories
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.database.database import SessionLocal
from src.statistics.standings_calculator import StandingsCalculator
from src.statistics.scorers_calculator import TopScorersCalculator


def main():
    db = SessionLocal()

    try:
        # Show tournament standings
        print("\nTournament Standings")
        print("===================")
        standings_calc = StandingsCalculator(db)
        print(standings_calc.format_standings_table())

        # Show top scorers
        print("\nTop Scorers")
        print("===========")
        scorers_calc = TopScorersCalculator(db)
        print(scorers_calc.format_top_scorers_table())

    finally:
        db.close()


if __name__ == "__main__":
    main()