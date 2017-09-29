import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

sqlHost=os.environ.get('datonate_sql') or "none"
sqlUser=os.environ.get('datonate_sqlUser') or "none"
sqlPass=os.environ.get('datonate_sqlPass') or "none"
sqlDB=os.environ.get('datonate_sqldb') or "none"

engineString = "mysql+mysqldb://"+sqlUser+":"+sqlPass+"@"+sqlHost+"/"+sqlDB

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = engineString
db = SQLAlchemy(app)

class User(db.Model):
    __tablename__ = 'user'
    
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(15))
    last_name = db.Column(db.String(15))
    email = db.Column(db.String(50))
    password = db.Column(db.String(32))
    phone = db.Column(db.String(10))
    
    def __repr__(self):
            return "Hello world!"

