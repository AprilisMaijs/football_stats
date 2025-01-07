from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Dict, Tuple
from src.database.models import Team, Match, Goal


class StandingsCalculator:
    def __init__(self, db: Session):
        self.db = db

    def calculate_standings(self) -> List[Dict]:
        """Calculate tournament standings for all teams"""
        teams = self.db.query(Team).all()
        standings = []

        for team in teams:
            # Get all matches for this team
            home_matches = self.db.query(Match).filter(Match.home_team_id == team.id).all()
            away_matches = self.db.query(Match).filter(Match.away_team_id == team.id).all()

            stats = {
                'team_name': team.name,
                'points': 0,
                'matches_played': len(home_matches) + len(away_matches),
                'wins_regular': 0,
                'wins_overtime': 0,
                'losses_regular': 0,
                'losses_overtime': 0,
                'goals_for': 0,
                'goals_against': 0
            }

            # Process home matches
            for match in home_matches:
                home_goals = len([g for g in match.goals if g.team_id == team.id])
                away_goals = len([g for g in match.goals if g.team_id != team.id])

                stats['goals_for'] += home_goals
                stats['goals_against'] += away_goals

                self._update_match_stats(stats, home_goals, away_goals, match)

            # Process away matches
            for match in away_matches:
                home_goals = len([g for g in match.goals if g.team_id != team.id])
                away_goals = len([g for g in match.goals if g.team_id == team.id])

                stats['goals_for'] += away_goals
                stats['goals_against'] += home_goals

                self._update_match_stats(stats, away_goals, home_goals, match)

            # Calculate goal difference
            stats['goal_difference'] = stats['goals_for'] - stats['goals_against']

            standings.append(stats)

        # Sort standings by points (descending), then goal difference
        return sorted(standings,
                      key=lambda x: (x['points'], x['goal_difference']),
                      reverse=True)

    def _update_match_stats(self, stats: Dict, team_goals: int, opponent_goals: int, match: Match):
        """Update match statistics based on goals scored"""
        is_overtime = self._is_overtime_game(match)

        if is_overtime:
            if team_goals > opponent_goals:
                stats['wins_overtime'] += 1
                stats['points'] += 3
            else:
                stats['losses_overtime'] += 1
                stats['points'] += 2
        else:
            if team_goals > opponent_goals:
                stats['wins_regular'] += 1
                stats['points'] += 5
            else:
                stats['losses_regular'] += 1
                stats['points'] += 1

    def _is_overtime_game(self, match: Match) -> bool:
        """
        Determine if a game went to overtime by checking if any goals
        were scored after 60:00 (regular time)
        """
        for goal in match.goals:
            minutes, seconds = map(int, goal.time.split(':'))
            total_seconds = minutes * 60 + seconds
            if total_seconds > 3600:  # 60:00 in seconds
                return True
        return False

    def format_standings_table(self) -> str:
        """Format standings as a pretty table string"""
        standings = self.calculate_standings()

        # Header
        header = f"{'Pos':>3} {'Team':<20} {'GP':>3} {'W':>3} {'WO':>3} {'LO':>3} {'L':>3} {'GF':>3} {'GA':>3} {'GD':>4} {'Pts':>4}"
        separator = "-" * len(header)

        # Format each row
        rows = []
        for i, team in enumerate(standings, 1):
            row = (f"{i:>3} {team['team_name']:<20} "
                   f"{team['matches_played']:>3} "
                   f"{team['wins_regular']:>3} "
                   f"{team['wins_overtime']:>3} "
                   f"{team['losses_overtime']:>3} "
                   f"{team['losses_regular']:>3} "
                   f"{team['goals_for']:>3} "
                   f"{team['goals_against']:>3} "
                   f"{team['goal_difference']:>4} "
                   f"{team['points']:>4}")
            rows.append(row)

        return "\n".join([header, separator] + rows)