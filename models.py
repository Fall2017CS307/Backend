import os
from utils import dbConn
from sqlalchemy import create_engine, Column
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.types import Integer, String 
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
            return ""

def setupTables():
    engine=dbConn().get_engine() 
    Base.metadata.create_all(engine) 