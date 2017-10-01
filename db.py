import os
from sqlalchemy import create_engine, Column
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.types import Integer, String 

class dbConn(): 
    def __init__(self):
        
        self.sqlHost=os.environ.get('datonate_sql') or "none"
        self.sqlUser=os.environ.get('datonate_sqlUser') or "none"
        self.sqlPass=os.environ.get('datonate_sqlPass') or "none"
        self.sqlDB=os.environ.get('datonate_sqldb') or "none"

    def get_engine(self):
        engineString = "mysql+mysqldb://"+self.sqlUser+":"+self.sqlPass+"@"+self.sqlHost+"/"+self.sqlDB
        return create_engine(engineString, pool_recycle=3600)

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


def setupDB():
    engine=dbConn().get_engine() 
    Base.metadata.create_all(engine) 

