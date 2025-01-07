from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Dict
from src.database.models import Player, Team, Goal


class TopScorersCalculator:
    def __init__(self, db: Session):
        self.db = db

    def calculate_top_scorers(self, limit: int = 10) -> List[Dict]:
        """
        Calculate top scorers including both goals and assists.
        Returns them sorted by goals (primary) and assists (secondary).
        """
        # Calculate goals and assists separately to avoid incorrect counting
        scorers = {}

        # Count goals
        goals_query = (
            self.db.query(
                Player,
                func.count(Goal.id).label('goals')
            )
            .outerjoin(Goal, Goal.scorer_id == Player.id)
            .group_by(Player.id)
        )

        # Initialize scorers dict with goals
        for player, goals in goals_query:
            if goals > 0:  # Only include players who scored or assisted
                scorers[player.id] = {
                    'player_name': player.full_name(),
                    'team_name': player.team.name,
                    'goals': goals,
                    'assists': 0
                }

        # Count first assists
        first_assists_query = (
            self.db.query(
                Player,
                func.count(Goal.id).label('assists')
            )
            .outerjoin(Goal, Goal.assist1_id == Player.id)
            .group_by(Player.id)
        )

        # Add first assists to total
        for player, assists in first_assists_query:
            if assists > 0:
                if player.id not in scorers:
                    scorers[player.id] = {
                        'player_name': player.full_name(),
                        'team_name': player.team.name,
                        'goals': 0,
                        'assists': 0
                    }
                scorers[player.id]['assists'] += assists

        # Count second assists
        second_assists_query = (
            self.db.query(
                Player,
                func.count(Goal.id).label('assists')
            )
            .outerjoin(Goal, Goal.assist2_id == Player.id)
            .group_by(Player.id)
        )

        # Add second assists to total
        for player, assists in second_assists_query:
            if assists > 0:
                if player.id not in scorers:
                    scorers[player.id] = {
                        'player_name': player.full_name(),
                        'team_name': player.team.name,
                        'goals': 0,
                        'assists': 0
                    }
                scorers[player.id]['assists'] += assists

        # Convert to list and sort
        sorted_scorers = sorted(
            scorers.values(),
            key=lambda x: (x['goals'], x['assists']),
            reverse=True
        )

        return sorted_scorers[:limit]

    def format_top_scorers_table(self, limit: int = 10) -> str:
        """Format top scorers as a pretty table string"""
        scorers = self.calculate_top_scorers(limit)

        # Header
        header = f"{'Pos':>3} {'Player':<25} {'Team':<20} {'Goals':>5} {'Assists':>7}"
        separator = "-" * len(header)

        # Format each row
        rows = []
        for i, scorer in enumerate(scorers, 1):
            row = (f"{i:>3} "
                   f"{scorer['player_name']:<25} "
                   f"{scorer['team_name']:<20} "
                   f"{scorer['goals']:>5} "
                   f"{scorer['assists']:>7}")
            rows.append(row)

        return "\n".join([header, separator] + rows)