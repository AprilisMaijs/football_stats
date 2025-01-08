from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


class Team(Base):
    __tablename__ = 'teams'

    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True)

    # Relationships
    players = relationship("Player", back_populates="team")
    home_matches = relationship("Match", foreign_keys="Match.home_team_id", back_populates="home_team")
    away_matches = relationship("Match", foreign_keys="Match.away_team_id", back_populates="away_team")
    goals = relationship("Goal", back_populates="team")
    cards = relationship("Card", back_populates="team")
    substitutions = relationship("Substitution", back_populates="team")


class Player(Base):
    __tablename__ = 'players'

    id = Column(Integer, primary_key=True)
    team_id = Column(Integer, ForeignKey('teams.id'))
    number = Column(Integer)
    first_name = Column(String)
    last_name = Column(String)
    role = Column(String)  # V, A, or U

    # Relationships
    team = relationship("Team", back_populates="players")
    goals_scored = relationship("Goal", foreign_keys="Goal.scorer_id", back_populates="scorer")
    first_assists = relationship("Goal", foreign_keys="Goal.assist1_id", back_populates="assist1")
    second_assists = relationship("Goal", foreign_keys="Goal.assist2_id", back_populates="assist2")
    cards = relationship("Card", back_populates="player")
    substitutions_in = relationship("Substitution", foreign_keys="Substitution.player_in_id",
                                    back_populates="player_in")
    substitutions_out = relationship("Substitution", foreign_keys="Substitution.player_out_id",
                                     back_populates="player_out")

    def full_name(self):
        return f"{self.first_name} {self.last_name}"


class MatchReferee(Base):
    __tablename__ = 'match_referees'

    id = Column(Integer, primary_key=True)
    match_id = Column(Integer, ForeignKey('matches.id'))
    referee_id = Column(Integer, ForeignKey('referees.id'))
    is_main = Column(Boolean, default=False)

    # Relationships
    match = relationship("Match", back_populates="match_referees")
    referee = relationship("Referee", back_populates="match_referees")


# noinspection PyTypeChecker
class Match(Base):
    __tablename__ = 'matches'

    id = Column(Integer, primary_key=True)
    date = Column(DateTime)
    venue = Column(String)
    spectators = Column(Integer)
    home_team_id = Column(Integer, ForeignKey('teams.id'))
    away_team_id = Column(Integer, ForeignKey('teams.id'))

    # Relationships
    home_team = relationship("Team", foreign_keys=[home_team_id], back_populates="home_matches")
    away_team = relationship("Team", foreign_keys=[away_team_id], back_populates="away_matches")
    goals = relationship("Goal", back_populates="match")
    cards = relationship("Card", back_populates="match")
    substitutions = relationship("Substitution", back_populates="match")
    match_referees = relationship("MatchReferee", back_populates="match")


class Goal(Base):
    __tablename__ = 'goals'

    id = Column(Integer, primary_key=True)
    match_id = Column(Integer, ForeignKey('matches.id'))
    team_id = Column(Integer, ForeignKey('teams.id'))
    scorer_id = Column(Integer, ForeignKey('players.id'))
    assist1_id = Column(Integer, ForeignKey('players.id'), nullable=True)
    assist2_id = Column(Integer, ForeignKey('players.id'), nullable=True)
    time = Column(String)  # Format: "mm:ss"
    is_penalty = Column(Boolean, default=False)

    # Relationships
    match = relationship("Match", back_populates="goals")
    team = relationship("Team", back_populates="goals")
    # noinspection PyTypeChecker
    scorer = relationship("Player", foreign_keys=[scorer_id], back_populates="goals_scored")
    assist1 = relationship("Player", foreign_keys=[assist1_id], back_populates="first_assists")
    assist2 = relationship("Player", foreign_keys=[assist2_id], back_populates="second_assists")


class Card(Base):
    __tablename__ = 'cards'

    id = Column(Integer, primary_key=True)
    match_id = Column(Integer, ForeignKey('matches.id'))
    team_id = Column(Integer, ForeignKey('teams.id'))
    player_id = Column(Integer, ForeignKey('players.id'))
    time = Column(String)  # Format: "mm:ss"
    is_red = Column(Boolean, default=False)

    # Relationships
    match = relationship("Match", back_populates="cards")
    team = relationship("Team", back_populates="cards")
    player = relationship("Player", back_populates="cards")


class Substitution(Base):
    __tablename__ = 'substitutions'

    id = Column(Integer, primary_key=True)
    match_id = Column(Integer, ForeignKey('matches.id'))
    team_id = Column(Integer, ForeignKey('teams.id'))
    player_out_id = Column(Integer, ForeignKey('players.id'))
    player_in_id = Column(Integer, ForeignKey('players.id'))
    time = Column(String)  # Format: "mm:ss"

    # Relationships
    match = relationship("Match", back_populates="substitutions")
    team = relationship("Team", back_populates="substitutions")
    player_out = relationship("Player", foreign_keys=[player_out_id], back_populates="substitutions_out")
    player_in = relationship("Player", foreign_keys=[player_in_id], back_populates="substitutions_in")


class Referee(Base):
    __tablename__ = 'referees'

    id = Column(Integer, primary_key=True)
    first_name = Column(String)
    last_name = Column(String)

    # Relationships
    match_referees = relationship("MatchReferee", back_populates="referee")

    def full_name(self):
        return f"{self.first_name} {self.last_name}"