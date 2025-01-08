from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Dict
from src.database.models import Player, Team, Substitution


class SubstitutionCalculator:
    def __init__(self, db: Session):
        self.db = db

    def calculate_substitution_stats(self, limit: int = 10) -> List[Dict]:
        """Calculate statistics for players who get substituted out the most"""

        # Query to get players and their substitution counts
        sub_stats = (
            self.db.query(
                Player,
                func.count(Substitution.id).label('times_subbed_out')
            )
            .join(Substitution, Substitution.player_out_id == Player.id)
            .group_by(Player.id)
            .having(func.count(Substitution.id) > 0)  # Only include players who were substituted
            .order_by(func.count(Substitution.id).desc())
            .limit(limit)
            .all()
        )

        stats = []
        for player, sub_count in sub_stats:
            stats.append({
                'player_name': player.full_name(),
                'team_name': player.team.name,
                'role': self._get_role_name(player.role),
                'times_subbed_out': sub_count
            })

        return stats

    def _get_role_name(self, role_code: str) -> str:
        """Convert role code to full name"""
        roles = {
            'V': 'Goalkeeper',
            'A': 'Defender',
            'U': 'Forward'
        }
        return roles.get(role_code, role_code)

    def format_substitution_stats_table(self, limit: int = 10) -> str:
        """Format substitution statistics as a pretty table string"""
        stats = self.calculate_substitution_stats(limit)

        # Header
        header = f"{'Pos':>3} {'Player':<25} {'Team':<20} {'Role':<12} {'Subbed Out':>10}"
        separator = "-" * len(header)

        # Format each row
        rows = []
        for i, stat in enumerate(stats, 1):
            row = (f"{i:>3} "
                   f"{stat['player_name']:<25} "
                   f"{stat['team_name']:<20} "
                   f"{stat['role']:<12} "
                   f"{stat['times_subbed_out']:>10}")
            rows.append(row)

        return "\n".join([header, separator] + rows)