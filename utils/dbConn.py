import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy


class dbConn(): 
    def __init__(self):
        
        self.sqlHost=os.environ.get('datonate_sql') or "none"
        self.sqlUser=os.environ.get('datonate_sqlUser') or "none"
        self.sqlPass=os.environ.get('datonate_sqlPass') or "none"
        self.sqlDB=os.environ.get('datonate_sqldb') or "none"

    def get_engine(self):
        engineString = "mysql+mysqldb://"+self.sqlUser+":"+self.sqlPass+"@"+self.sqlHost+"/"+self.sqlDB
        app = Flask(__name__)
        app.config['SQLALCHEMY_DATABASE_URI'] = engineString
        db = SQLAlchemy(app)
        return db