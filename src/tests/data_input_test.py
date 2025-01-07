import os
from pathlib import Path
from src.database.database import init_db, SessionLocal
from src.database.models import Team, Player, Match, Goal, Card, Substitution
from src.parsers.json_parser import MatchParser


def test_parser():
    # Get the project root directory and data directory
    root_dir = Path(__file__).parent.parent
    data_dir = root_dir / 'data'

    # Initialize database
    init_db()

    # Create database session
    db = SessionLocal()

    try:
        # Create parser instance
        parser = MatchParser(db)

        # Get list of all JSON files in data directory
        json_files = sorted([f for f in data_dir.glob('*.json')])

        if not json_files:
            print(f"No JSON files found in {data_dir}")
            return

        # Parse each file
        for json_file in json_files:
            print(f"\nParsing {json_file.name}...")
            parser.parse_file(json_file)

        # Verify the data was stored correctly
        print("\nVerifying stored data:")

        # Check teams
        teams = db.query(Team).all()
        print(f"\nTeams found: {len(teams)}")
        for team in teams:
            print(f"- {team.name}")

            # Check players for each team
            players = db.query(Player).filter_by(team_id=team.id).all()
            print(f"  Players: {len(players)}")
            for player in players:
                print(f"  - #{player.number} {player.full_name()} ({player.role})")

        # Check matches
        matches = db.query(Match).all()
        print(f"\nMatches found: {len(matches)}")
        for match in matches:
            print(f"\nMatch: {match.home_team.name} vs {match.away_team.name}")
            print(f"Date: {match.date}")
            print(f"Venue: {match.venue}")
            print(f"Spectators: {match.spectators}")

            # Check goals
            goals = db.query(Goal).filter_by(match_id=match.id).all()
            print(f"\nGoals: {len(goals)}")
            for goal in goals:
                assists = []
                if goal.assist1:
                    assists.append(goal.assist1.full_name())
                if goal.assist2:
                    assists.append(goal.assist2.full_name())
                assist_str = f" (Assists: {', '.join(assists)})" if assists else ""
                penalty_str = " (Penalty)" if goal.is_penalty else ""
                print(f"- {goal.time} - {goal.scorer.full_name()}{penalty_str}{assist_str}")

            # Check cards
            cards = db.query(Card).filter_by(match_id=match.id).all()
            print(f"\nCards: {len(cards)}")
            for card in cards:
                card_type = "Red" if card.is_red else "Yellow"
                print(f"- {card.time} - {card.player.full_name()} ({card_type})")

            # Check substitutions
            subs = db.query(Substitution).filter_by(match_id=match.id).all()
            print(f"\nSubstitutions: {len(subs)}")
            for sub in subs:
                print(f"- {sub.time} - {sub.player_out.full_name()} → {sub.player_in.full_name()}")

    except Exception as e:
        print(f"Error occurred: {str(e)}")
        raise e
    finally:
        db.close()


if __name__ == "__main__":
    test_parser()