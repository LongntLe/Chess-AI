from sqlalchemy import *
from sqlalchemy import create_engine, ForeignKey, Index
from sqlalchemy import Column, Date, Integer, String, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, backref
 
engine = create_engine('sqlite:///chess_db.db', echo=True)
Base = declarative_base()
 
########################################################################
class Moves(Base):
    """
    Primary database to store move evaluation
    I did not intialize state as an indexed column in the beginning. Thus the last 5 lines.
    """
    __tablename__ = "moves"
 
    id = Column(Integer, primary_key=True)
    state = Column(String, index=True)
    value = Column(Float)
 
    #----------------------------------------------------------------------
    def __init__(self, state, value):
        """"""
        self.state = state
        self.value = value
 
# create tables
Base.metadata.create_all(engine)

try:
    state_index = Index('state_idx', Moves.state) # index column. Effectively compromising space for searching speed.
    state_index.create(bind=engine)
except:
    pass