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
	
	jsonString  = urllib2.urlopen(SERVER_ADDRESS+"/api/login?email="+email+"&password="+password).read()	
	jsonArr = json.loads(jsonString)
	if(jsonArr['status']!=200):
		assert False,"Login Failed for valid user/password combination \n Response + " + str(jsonArr)
	
	jsonString  = urllib2.urlopen(SERVER_ADDRESS+"/api/login?email="+invalidEmail+"&password="+password).read()	
	jsonArr = json.loads(jsonString)
	if(jsonArr['status']==200):
		assert False,"Login Success for invalid user \n Response + " + str(jsonArr)

	jsonString  = urllib2.urlopen(SERVER_ADDRESS+"/api/login?email="+email+"&password="+invalidPassword).read()	
	jsonArr = json.loads(jsonString)
	if(jsonArr['status']==200):
		assert False,"Login Success for invalid password \n Response + " + str(jsonArr)
	
	