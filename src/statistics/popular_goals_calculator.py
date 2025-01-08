from sqlalchemy.orm import Session
from typing import List, Dict
from src.database.models import Match, Goal, Player


class PopularGoalsCalculator:
    def __init__(self, db: Session):
        self.db = db

    def calculate_popular_goals(self, limit: int = 10) -> List[Dict]:
        """Calculate most-watched goals with venue and scorer information"""

        # Query to get goals with match attendance and venue info
        popular_goals = (
            self.db.query(
                Goal,
                Match.spectators,
                Match.venue,
                Player
            )
            .join(Match, Goal.match_id == Match.id)
            .join(Player, Goal.scorer_id == Player.id)
            .order_by(Match.spectators.desc())
            .limit(limit)
            .all()
        )

        goals = []
        for goal, spectators, venue, scorer in popular_goals:
            goals.append({
                'scorer_name': scorer.full_name(),
                'team_name': scorer.team.name,
                'spectators': spectators,
                'venue': venue,
                'time': goal.time,
                'is_penalty': goal.is_penalty
            })

        return goals

    def format_popular_goals_table(self, limit: int = 10) -> str:
        """Format popular goals as a pretty table string"""
        goals = self.calculate_popular_goals(limit)

        # Header
        header = f"{'Pos':>3} {'Scorer':<25} {'Team':<20} {'Venue':<25} {'Time':>5} {'Type':<8} {'Spectators':>10}"
        separator = "-" * len(header)

        # Format each row
        rows = []
        for i, goal in enumerate(goals, 1):
            goal_type = "Penalty" if goal['is_penalty'] else "Regular"
            row = (f"{i:>3} "
                   f"{goal['scorer_name']:<25} "
                   f"{goal['team_name']:<20} "
                   f"{goal['venue']:<25} "
                   f"{goal['time']:>5} "
                   f"{goal_type:<8} "
                   f"{goal['spectators']:>10,}")
            rows.append(row)

        return "\n".join([header, separator] + rows)