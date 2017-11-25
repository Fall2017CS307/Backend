import sys
sys.path.append("..")

import MySQLdb
import os
import utils.dbConn as db
import models
import json
import urllib2
from random import randint
from datetime import datetime


SERVER_ADDRESS = "http://127.0.0.1:5000"

email_new = "ramyaksingh@yahoo.com"
password_new = "secret"

test_first = 'First'
test_last = 'Last'
test_password = 'secret'
test_email = 'test_email@email.com'
test_phone = '3126469650'

session = db.dbConn().get_session(db.dbConn().get_engine())

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

## call functions to suppirt test cases

def test_registration():

	email_existing = "achellan@purdue.edu"
	password_existing = "secret"


	firstname = "xyz"
	lastname = "abc"
	phone = "9876543210"


	jsonStr, suc = call_registration(firstname, lastname, email_existing, password_existing, phone)

	if(suc):
		assert False, "Registration successful for already existing user \n Response + " +jsonStr


	jsonStr, suc = call_registration(test_first, test_last, test_email, test_password, test_phone)

	if(not suc):
		assert False, "Registration unsuccessful for new user with valid information \n Response + " +jsonStr


	#tempUser = session.query(models.User).filter(models.User.email == test_email).first()
	#tempUserValidate = session.query(models.user_validate).filter(models.user_validate.id == tempUser.id).first()
	#session.delete(tempUserValidate)
	#session.commit()

def test_emailAndPhoneVerification():

	#test_user = models.User(first_name = test_first, last_name=test_last, password=test_password, email=test_email, phone=test_phone)
	#session = db.dbConn().get_session(db.dbConn().get_engine())
	#session.add(test_user)
	#session.commit()

	session = db.dbConn().get_session(db.dbConn().get_engine())
	test_user = session.query(models.User).filter(models.User.email == test_email).first()
	if(test_user is None):
		assert False, "Test User doesnt exist"

	print(test_user)
	'''

	randNum = randint(1,10000)
	randNum2 = randint(1,10000)
	timeStamp = datetime.now()
	emailKey = str(randNum) + str(timeStamp.year) + str(timeStamp.month) + str(timeStamp.day) + str(timeStamp.hour) + str(timeStamp.minute) + str(timeStamp.second) + "_" + str(randNum2)
	contentText = "Go to the link to verify " + "http://datonate.com:5000/api/verify/email/"+emailKey


	## Generate Phone key


	randNum = randint(1,10000)
	randNum2 = randint(1,10000)
	timeStamp = datetime.now()
	phoneKey = str(randNum) + str(timeStamp.year) + str(timeStamp.month) + str(timeStamp.day) + str(timeStamp.hour) + str(timeStamp.minute) + str(timeStamp.second) + "__" + str(randNum2)
	textContent="Go to the link to verify " + "http://datonate.com:5000/api/verify/phone/"+phoneKey
	'''
	userValidateTemp = session.query(models.user_validate).filter(models.user_validate.id == test_user.id).first()
	print(test_user)
	print(userValidateTemp)
	emailKey = session.query(models.user_validate).filter(models.user_validate.id == test_user.id).first().emailCode
	phoneKey = session.query(models.user_validate).filter(models.user_validate.id == test_user.id).first().phoneCode
	#regUser = session.query(models.User).filter(models.User.email == user.email).first()

	#userValidate = models.user_validate(test_user.id, emailKey, phoneKey)
	#session.add(userValidate)
	#session.commit()


	jsonStr, suc = call_email(emailKey)

	if(suc):
		session = db.dbConn().get_session(db.dbConn().get_engine())
		checkUser = session.query(models.User).filter(models.User.id == test_user.id).first()
		print(checkUser)
		print(checkUser.isEmail)
		if(checkUser.isEmail == False):
			assert False, "Says this it verified, but verification wasn't performed inside user table"

	if(not suc):
		assert False, "Failed verify email for valid key"

	jsonStr, suc = call_email('100')

	if(suc):
		assert False, "Verified with wrong key"



	jsonStr, suc = call_phone(phoneKey)

	if(suc):
		session = db.dbConn().get_session(db.dbConn().get_engine())
		checkUser = session.query(models.User).filter(models.User.id == test_user.id).first()
		if(checkUser.isPhone == False):
			assert False, "Says this it verified, but verification wasn't performed inside user table"

	if(not suc):
		assert False, "Failed verify phone for valid key"

	jsonStr, suc = call_phone('100')

	if(suc):
		assert False, "Verified with wrong key"




def test_login():
	email = test_email
	password = test_password

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


def test_user_delete():
	delUser = session.query(models.User).filter(models.User.email == test_email).first()
	session.delete(delUser)
	session.commit()

def call_login(email, password):
	jsonString  = urllib2.urlopen(SERVER_ADDRESS+"/api/login?email="+email+"&password="+password).read()
	jsonArr = json.loads(jsonString)
	if(jsonArr['status']!=200):
		return str(jsonArr), False
	return str(jsonArr), True

def call_registration(firstname, lastname, email, password, phone):
	jsonString  = urllib2.urlopen(SERVER_ADDRESS+"/api/register?firstname="+firstname+"&lastname="+lastname+"&email="+email+"&password="+password+"&phone="+phone).read()
	jsonArr = json.loads(jsonString)

	if(jsonArr['status']!=200):
		return str(jsonArr), False
	return str(jsonArr), True

def call_email(key):
	jsonString  = urllib2.urlopen(SERVER_ADDRESS + "/api/verify/email/" + key).read()
	jsonArr = json.loads(jsonString)
	if(jsonArr['status']!=200):
		return str(jsonArr), False
	return str(jsonArr), True

def call_phone(key):
	jsonString  = urllib2.urlopen(SERVER_ADDRESS + "/api/verify/phone/" + key).read()
	jsonArr = json.loads(jsonString)
	if(jsonArr['status']!=200):
		return str(jsonArr), False
	return str(jsonArr), True
