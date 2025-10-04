from sqlalchemy import Column, String, Float, DateTime, UniqueConstraint
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Result(Base):
    __tablename__ = 'results'

    date = Column(DateTime, primary_key=True)
    home_team = Column(String, primary_key=True)
    away_team = Column(String)
    league = Column(String)  
    model_type = Column(String, primary_key=True)
    home_win_prob = Column(Float)
    draw_prob = Column(Float)
    away_win_prob = Column(Float)

    __table_args__ = (
        UniqueConstraint("date", "home_team", "model_type", name="uq_result_entry"),
    )

    def as_dict(self):
        return {
            'date': self.date,
            'home_team': self.home_team,
            'away_team': self.away_team,
            'league': self.league,
            'model_type': self.model_type,
            'home_win_prob': self.home_win_prob,
            'draw_prob': self.draw_prob,
            'away_win_prob': self.away_win_prob
        }
    
    def __repr__(self):
        return self.as_dict().__repr__()