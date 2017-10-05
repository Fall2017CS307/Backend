import os
from utils import dbConn
from sqlalchemy import create_engine, Column, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.types import Integer, String
from sqlalchemy.dialects.mysql import BOOLEAN
import re
import hashlib

Base = declarative_base()

class User(Base):
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True)
    first_name = Column(String(15), nullable=False)
    last_name = Column(String(15), nullable=False)
    email = Column(String(50), nullable=False)
    password = Column(String(32), nullable=False)
    phone = Column(String(10), nullable=False)
    isPhone = Column(BOOLEAN, default=0, nullable=False)
    isEmail = Column(BOOLEAN, default=0, nullable=False)

    errors = []
    def __repr__(self):
            return self.first_name + " " + self.last_name + " " + self.email + " " + self.password + " " + self.phone

    def __init__(self, first_name=None, last_name=None, email=None, password=None, phone=None):
        self.errors = []
        if(first_name and re.match('^[a-zA-Z]+$', first_name)):
            self.first_name = first_name
        else:
            self.first_name = None
            self.errors.append("Invalid First name formatting")
        if(last_name and re.match('^[a-zA-Z]+$', last_name)):
            self.last_name = last_name
        else:
            self.last_name = None
            self.errors.append("Invalid Last name formatting")
        if(email and re.match("([a-z0-9!#$%&'*+\/=?^_`{|}~-]+(?:\.[a-z0-9!#$%&'*+\/=?^_`""{|}~-]+)*(@|\sat\s)(?:[a-z0-9](?:[a-z0-9-]*[a-z0-9])?(\.|""\sdot\s))+[a-z0-9](?:[a-z0-9-]*[a-z0-9])?)",email )):
            self.email = email
        else:
            self.email = None
            self.errors.append("Invalid email formatting")
        if(password):
            m = hashlib.md5()
            m.update(password)
            self.password = m.hexdigest()
        else:
            self.password = None
            self.errors.append("Invalid password formatting")
        if(phone and re.match("^[0-9]{10}$", phone)):
            self.phone = phone
        else:
            self.phone = None
            self.errors.append("Invalid phone formatting")

class user_validate(Base):
    __tablename__ = 'user_validate'
    id = Column(Integer,ForeignKey("user.id"), primary_key=True)
    emailCode = Column(String(32))
    phoneCode = Column(String(32))

    def __init__(self, id, emailCode,phoneCode):
        self.id = id
        self.emailCode = emailCode
        self.phoneCode = phoneCode

class dataset(Base):

    __tablename__ = 'dataset'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer,ForeignKey("user.id"))
    file_name = Column(String(30))
    resource_id = Column(String(60))

#resouce 40, file 30
    def __init__(self, user_id, file_name, resource_id):
        self.user_id = user_id
        self.file_name = file_name
        self.resource_id = resource_id


def setupTables():
    engine=dbConn.dbConn().get_engine()
    Base.metadata.create_all(engine)
