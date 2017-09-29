from sqlalchemy import create_engine, Column
from utils.dbConn import dbConn
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.types import *
engine = dbConn().get_engine() 

Base = declarative_base()

class User(Base):
    __tablename__ = 'user'
    
    id = Column(Integer, primary_key=True)
    first_name = Column(String(15))
    last_name = Column(String(15))
    email = Column(String(50))
    password = Column(String(32))
    phone = Column(String(10))
    
    def __repr__(self):
            return "Hello world!"