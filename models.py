import os
from utils import dbConn
from sqlalchemy import create_engine, Column, ForeignKey, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.types import Integer, String
from sqlalchemy.dialects.mysql import BOOLEAN
import re
import hashlib
import time
from datetime import datetime

Base = declarative_base()

class User(Base):
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True)
    first_name = Column(String(15), nullable=False)
    last_name = Column(String(15), nullable=False)
    email = Column(String(50), nullable=False)
    password = Column(String(32), nullable=False)
    phone = Column(String(10), nullable=False)
    gender = Column(BOOLEAN, nullable=True)
    skill = Column(Integer, default=0)
    country = Column(String(50), nullable=True)
    balance = Column(Integer, default=0, nullable=False)
    isPhone = Column(BOOLEAN, default=0, nullable=False)
    isEmail = Column(BOOLEAN, default=0, nullable=False)

    errors = []
    def __repr__(self):
            return self.first_name + " " + self.last_name + " " + self.email + " " + self.password + " " + self.phone

    def __init__(self, first_name=None, last_name=None, email=None, password=None, phone=None, gender=None, country=None, skill=None):
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
        if(gender is None):
            self.gender = None
        else:
            try:
                gender = int(gender)
                if(gender ==0 or gender == 1):
                    self.gender = gender
                else:
                    self.gender = None
                    self.errors.append("Gender is not binary")
            except:
                self.errors("Gender is not integer")
                self.gender = None
        if(skill is None):
            self.skill = 0
        else:
            try:
                skill = int(skill)
                if(skill >=0 and skill < 5):
                    self.skill = skill
            except:
                self.skill = 0
                self.errors.append("Skill is not integer")
        self.country = country

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
    title = Column(String, nullable=False)
    user_id = Column(Integer,ForeignKey("user.id"))
    resource_id = Column(String(60))
    isMedia = Column(BOOLEAN, default=0, nullable=False)
    isPublic = Column(BOOLEAN, default=0, nullable=False)
#resouce 40, file 30
    def __init__(self, user_id, isMedia, resource_id):
        self.user_id = user_id
        self.isMedia = isMedia
        self.resource_id = resource_id
        self.title = title

class experiments(Base):
    __tablename__ = 'experiments'

    id = Column(Integer, primary_key=True)
    title = Column(String, nullable=False)
    user_id = Column(Integer,ForeignKey("user.id"))
    resource_id =  Column(String(60),unique=True, nullable=False)
    price = Column(Integer, default=0, nullable=False)
    batchSize = Column(Integer, default=0, nullable=False)
    description = Column(String(60))
    dataset_id =  Column(Integer,ForeignKey("dataset.id"))
    gender = Column(BOOLEAN, nullable=True)
    skill = Column(Integer, default=0)
    country = Column(String(50), nullable=True)
    deadline = Column(DateTime, nullable = True)
    isPhone = Column(BOOLEAN, default=0, nullable=False)
    annotateCount = Column(Integer, default=0, nullable=False)

    def __init__(self,user_id, resource_id, price, batchSize, description, dataset_id, gender=None, country=None, skill=None, deadline=None):
        self.user_id = user_id
        self.resource_id = resource_id
        self.price = price
        self.batchSize = batchSize
        self.description = description
        self.dataset_id = dataset_id
        self.gender=gender
        self.country=country
        self.skill=skill
        self.deadline = deadline
        self.title = title

class batch(Base):
    __tablename__ = 'batches'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer,ForeignKey("user.id"))
    experiment_id = Column(String(60),ForeignKey("experiments.resource_id"))
    local_resource_id = Column(Integer, default=0, nullable=False)
    isCompleted = Column(BOOLEAN, default=0, nullable=False)
    rating = Column(Integer, nullable=True)
    curAnnotation = Column(Integer, default=0, nullable=False)
    totalAnnotation = Column(Integer, default=0, nullable=False)
    
    def __init__(self,experiment_id, local_resource_id, batchSize):
        self.experiment_id = experiment_id
        self.local_resource_id = local_resource_id
        self.totalAnnotation = batchSize

def setupTables():
    engine=dbConn.dbConn().get_engine()
    Base.metadata.create_all(engine)
