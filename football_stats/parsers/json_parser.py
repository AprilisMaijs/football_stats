import json
from datetime import datetime
from typing import Dict, List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_
from football_stats.database.models import Base, Team, Player, Match, Goal, Card, Substitution, Referee, MatchReferee


class MatchParser:
    def __init__(self, db: Session):
        self.db = db

    def parse_file(self, file_path: str) -> None:
        """Parse a single match JSON file and store it in the database"""
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            match_data = data['Spele']

            # Check if match already exists (same date, teams and venue)
            match_date = datetime.strptime(match_data['Laiks'], '%Y/%m/%d')
            teams = [team['Nosaukums'] for team in match_data['Komanda']]
            existing_match = self.db.query(Match).filter(
                and_(
                    Match.date == match_date,
                    Match.venue == match_data['Vieta'],
                    Match.home_team.has(Team.name == teams[0]),
                    Match.away_team.has(Team.name == teams[1])
                )
            ).first()

            if existing_match:
                print(f"Match already exists: {teams[0]} vs {teams[1]} on {match_date}")
                return

            # Process teams first
            processed_teams = []
            for team_data in match_data['Komanda']:
                team = self._process_team(team_data)
                processed_teams.append(team)

            # Commit to ensure teams have IDs
            self.db.commit()

            # Create match object
            match = Match(
                date=match_date,
                venue=match_data['Vieta'],
                spectators=match_data['Skatitaji'],
                home_team=processed_teams[0],
                away_team=processed_teams[1]
            )
            self.db.add(match)
            self.db.commit()  # Commit to get match ID

            # Process the rest of the data for each team
            for i, team_data in enumerate(match_data['Komanda']):
                team = processed_teams[i]

                # Process goals
                if 'Varti' in team_data and team_data['Varti']:
                    goals = self._process_goals(team_data['Varti'], team, match)
                    for goal in goals:
                        self.db.add(goal)

                # Process cards
                if 'Sodi' in team_data and team_data['Sodi']:
                    cards = self._process_cards(team_data['Sodi'], team, match)
                    for card in cards:
                        self.db.add(card)

                # Process substitutions
                if 'Mainas' in team_data and team_data['Mainas']:
                    subs = self._process_substitutions(team_data['Mainas'], team, match)
                    for sub in subs:
                        self.db.add(sub)

            # Process main referee
            main_ref = self._get_or_create_referee(
                first_name=match_data['VT']['Vards'],
                last_name=match_data['VT']['Uzvards']
            )
            self.db.commit()  # Commit to get referee ID

            match_ref = MatchReferee(
                match=match,
                referee=main_ref,
                is_main=True
            )
            self.db.add(match_ref)

            # Process assistant referees
            for ref_data in match_data['T']:
                ref = self._get_or_create_referee(
                    first_name=ref_data['Vards'],
                    last_name=ref_data['Uzvards']
                )
                match_ref = MatchReferee(
                    match=match,
                    referee=ref,
                    is_main=False
                )
                self.db.add(match_ref)

            # Final commit for all remaining changes
            self.db.commit()

    def _process_team(self, team_data: Dict) -> Team:
        """Process team data and return Team object"""
        team = self.db.query(Team).filter_by(name=team_data['Nosaukums']).first()

        if not team:
            team = Team(name=team_data['Nosaukums'])
            self.db.add(team)
            self.db.flush()  # Flush to get team ID

            # Process players
            for player_data in team_data['Speletaji']['Speletajs']:
                player = Player(
                    team=team,
                    number=player_data['Nr'],
                    first_name=player_data['Vards'],
                    last_name=player_data['Uzvards'],
                    role=player_data['Loma']
                )
                self.db.add(player)

        return team

    def _get_or_create_referee(self, first_name: str, last_name: str) -> Referee:
        """Get existing referee or create new one"""
        referee = self.db.query(Referee).filter_by(
            first_name=first_name,
            last_name=last_name
        ).first()

        if not referee:
            referee = Referee(
                first_name=first_name,
                last_name=last_name
            )
            self.db.add(referee)
            self.db.flush()  # Flush to get referee ID

        return referee

    def _get_player_by_number(self, number: int, team: Team) -> Optional[Player]:
        """Helper to get player by their number in a team"""
        return self.db.query(Player).filter_by(
            team_id=team.id,
            number=number
        ).first()

    def _process_goals(self, goals_data: Dict, team: Team, match: Match) -> List[Goal]:
        """Process goals data and return list of Goal objects"""
        goals = []
        if not goals_data:  # Handle empty goals data
            return goals

        vg_list = goals_data.get('VG', [])
        if isinstance(vg_list, dict):  # Handle single goal case
            vg_list = [vg_list]

        for goal_data in vg_list:
            scorer = self._get_player_by_number(goal_data['Nr'], team)

            # Process assists
            assists = []
            if 'P' in goal_data:
                assist_data = goal_data['P']
                if isinstance(assist_data, dict):  # Single assist
                    assist_data = [assist_data]
                for assist in assist_data:
                    assists.append(self._get_player_by_number(assist['Nr'], team))

            goal = Goal(
                match=match,
                team=team,
                scorer=scorer,
                time=goal_data['Laiks'],
                is_penalty=(goal_data['Sitiens'] == 'J')
            )

            # Add assists if any
            if len(assists) > 0 and assists[0]:
                goal.assist1 = assists[0]
            if len(assists) > 1 and assists[1]:
                goal.assist2 = assists[1]

            goals.append(goal)

        return goals

    def _process_cards(self, cards_data: Dict, team: Team, match: Match) -> List[Card]:
        """Process cards data and return list of Card objects"""
        cards = []
        if not cards_data:  # Handle empty cards data
            return cards

        sods_list = cards_data.get('Sods', [])
        if isinstance(sods_list, dict):  # Handle single card case
            sods_list = [sods_list]

        for card_data in sods_list:
            player = self._get_player_by_number(card_data['Nr'], team)

            # Check if player already has a yellow card in this match
            existing_card = self.db.query(Card).filter_by(
                match=match,
                player=player
            ).first()

            card = Card(
                match=match,
                team=team,
                player=player,
                time=card_data['Laiks'],
                is_red=(existing_card is not None)  # Red if second card
            )
            cards.append(card)

        return cards

    def _process_substitutions(self, subs_data: Dict, team: Team, match: Match) -> List[Substitution]:
        """Process substitutions data and return list of Substitution objects"""
        substitutions = []
        if not subs_data:  # Handle empty substitutions data
            return substitutions

        maina_list = subs_data.get('Maina', [])
        if isinstance(maina_list, dict):  # Handle single substitution case
            maina_list = [maina_list]

        for sub_data in maina_list:
            player_out = self._get_player_by_number(sub_data['Nr1'], team)
            player_in = self._get_player_by_number(sub_data['Nr2'], team)

            sub = Substitution(
                match=match,
                team=team,
                player_out=player_out,
                player_in=player_in,
                time=sub_data['Laiks']
            )
            substitutions.append(sub)

        return substitutions