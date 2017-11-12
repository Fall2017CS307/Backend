import sys
sys.path.append("..")

import MySQLdb
import os
import utils.dbConn as db
import models
import json
import urllib2

SERVER_ADDRESS = "http://127.0.0.1:5000"

def test_db_config():
	try:
		engine = db.dbConn().get_engine()
	except:
		assert False, "Database environmental variable not set"

def test_table_creation():
	engine = db.dbConn().get_engine()
	tables = models.Base.metadata.tables.keys()
	try:
		for table in tables:
			if not engine.dialect.has_table(engine, table):
				assert False, "Database tables not created"
	except:
		assert False, "Check previous test cases!"

def test_login():
	email = "achellan@purdue.edu"
	password = "secret"
	invalidEmail = "invalid@datonate.com"
	invalidPassword="InvalidPassword"

	jsonStr, suc = call_login(email, password)
	if(not suc):
		assert False,"Login unsuccessfull for valid user \n Response + " +jsonStr

	jsonStr, suc = call_login(email, invalidPassword)
	if(suc):
		assert False,"Login successfull for invalid user \n Response + " +jsonStr

	jsonStr, suc = call_login(invalidEmail, password)
	if(suc):
		assert False,"Login Success for invalid password \n Response + " + str(jsonArr)

## call functions to suppirt test cases

def test_registration():

	email_existing = "achellan@purdue.edu"
	password_existing = "secret"
	email_new = "ramyaksingh@yahoo.com"
	password_new = "secret"
	firstname = "xyz"
	lastname = "abc"
	phone = "9876543210"

	jsonStr, suc = call_registration(firstname, lastname, email_existing, password_existing, phone)

	if(suc):
		assert False,"Registration successful for already existing user \n Response + " +jsonStr

	jsonStr, suc = call_registration(firstname, lastname, email_new, password_new, phone)

	if(not suc):
		assert False,"Registration unsuccessful for new user with valid information \n Response + " +jsonStr


def call_login(email, password):
	jsonString  = urllib2.urlopen(SERVER_ADDRESS+"/api/login?email="+email+"&password="+password).read()
	jsonArr = json.loads(jsonString)
	if(jsonArr['status']!=200):
		return str(jsonArr), False
	return str(jsonArr), True

def call_registration(firstname, lastname, email, password, phone):
	jsonString  = urllib2.urlopen(SERVER_ADDRESS+"/api/register?firstname="+firstname+"/api/register?lastname="+lastname+
	"/api/register?email="+email+"/api/register?password="+password+"/api/register?phone="+phone).read()
	jsonArr = json.loads(jsonString)

	if(jsonArr['status']!=200):
		return str(jsonArr), False
	return str(jsonArr), True
