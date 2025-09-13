from sqlalchemy import Column, String, Float, DateTime, Integer
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Result(Base):
    __tablename__ = 'results'

    date = Column(DateTime, primary_key=True)
    home_team = Column(String, primary_key=True)
    away_team = Column(String, primary_key=True)
    league = Column(String, primary_key=True)  
    model_type = Column(String, primary_key=True)  
    result_code = Column(Integer)
    home_win_prob = Column(Float)
    draw_prob = Column(Float)
    away_win_prob = Column(Float)