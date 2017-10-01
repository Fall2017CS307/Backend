import os
from sqlalchemy import create_engine

class dbConn(): 
    def __init__(self):
        
        self.sqlHost=os.environ.get('datonate_sql') or "none"
        self.sqlUser=os.environ.get('datonate_sqlUser') or "none"
        self.sqlPass=os.environ.get('datonate_sqlPass') or "none"
        self.sqlDB=os.environ.get('datonate_sqldb') or "none"

    def get_engine(self):
        engineString = "mysql+mysqldb://"+self.sqlUser+":"+self.sqlPass+"@"+self.sqlHost+"/"+self.sqlDB
        return create_engine(engineString, pool_recycle=3600)



