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
from flask import request
import requests


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

def test_upload():

	session = db.dbConn().get_session(db.dbConn().get_engine())
	test_user = session.query(models.User).filter(models.User.email == test_email).first()

	validImageFile = 'temp1.zip'

	jsonStr, suc = call_upload_image(validImageFile)

	if(suc):
		session = db.dbConn().get_session(db.dbConn().get_engine())
		checkSet = session.query(models.dataset).filter(models.dataset.user_id == test_user.id)[0]

		if(checkSet is None):
			assert False, "Says that user doesn't exist while it does"
		if(checkSet.isMedia == False):
			assert False, "Dataset is not saved as media despite uploading a zip folder contaning images"

	if(not suc):
		assert False, "Dataset didn't upload for valid dataset"


	#session.delete(checkSet)
	#session.commit()
	validTextFile = 'document_example.zip'

	jsonStr, suc = call_upload_text(validTextFile)

	if(suc):
		session = db.dbConn().get_session(db.dbConn().get_engine())
		checkSet = session.query(models.dataset).filter(models.dataset.user_id == test_user.id)[1]

		if(checkSet is None):
			assert False, "Says that user doesn't exist while it does"
		if(checkSet.isMedia == True):
			assert False, "Dataset is saved as text despite uploading a zip folder contaning text"

	if(not suc):
		assert False, "Dataset didn't upload for valid dataset"

	'''
	TESTING FOR INVALID DATASETS
	'''

	validImageFile = 'temp1.zip'

	jsonStr, suc = call_upload_text(validImageFile)

	if(suc):
		assert False, "Dataset uploaded for invalid dataset"


	validTextFile = 'document_example.zip'

	jsonStr, suc = call_upload_image(validTextFile)

	if(suc):
		assert False, "Dataset uploaded for invalid dataset"


def test_get_datasets():

	session = db.dbConn().get_session(db.dbConn().get_engine())
	test_user = session.query(models.User).filter(models.User.email == test_email).first()

	jsonStr, suc = call_getDatasets(test_user.id)
	jsonArr = json.loads(jsonStr)

	imageResourceName = jsonArr['datasets'][0]['resource_name']
	textResource = jsonArr['datasets'][1]['resource_name']

	session = db.dbConn().get_session(db.dbConn().get_engine())
	imageDataset = session.query(models.dataset).filter(models.dataset.resource_id == imageResourceName).first()

	session = db.dbConn().get_session(db.dbConn().get_engine())
	checkUser = session.query(models.User).filter(models.User.id == imageDataset.user_id).first()

	if(suc):
		if(imageDataset is None):
			assert False,"Doesn't return dataset despite returning success message"
		if(checkUser is None):
			assert False, "Returns success message but corresponding user is invalid"

	if(not suc):
		assert False, "Couldn't return any of existing datasets"

	session = db.dbConn().get_session(db.dbConn().get_engine())
	textDataset = session.query(models.dataset).filter(models.dataset.resource_id == textResource).first()

	session = db.dbConn().get_session(db.dbConn().get_engine())
	checkUser = session.query(models.User).filter(models.User.id == textDataset.user_id).first()

	if(suc):
		if(textDataset is None):
			assert False,"Doesn't return dataset despite returning success message"
		if(checkUser is None):
			assert False, "Returns success message but corresponding user is invalid"

	if(not suc):
		assert False, "Couldn't return any of existing datasets"

def test_makeDatasetPublic():

	session = db.dbConn().get_session(db.dbConn().get_engine())
	test_user = session.query(models.User).filter(models.User.email == test_email).first()

	session = db.dbConn().get_session(db.dbConn().get_engine())
	checkSet = session.query(models.dataset).filter(models.dataset.user_id == test_user.id)[0]

	jsonStr, suc = call_publicDatasets(test_user.id, checkSet.id)

	if(suc):
		session = db.dbConn().get_session(db.dbConn().get_engine())
		checkSet = session.query(models.dataset).filter(models.dataset.user_id == test_user.id)[0]
		if(checkSet.isPublic == False):
			assert False, "Says that dataset was made public but it is still private"

	if(not suc):
		assert False, "Couldn't make dataset public for valid query"

	session = db.dbConn().get_session(db.dbConn().get_engine())
	checkSet = session.query(models.dataset).filter(models.dataset.user_id == test_user.id)[1]

	jsonStr, suc = call_publicDatasets(test_user.id, checkSet.id)

	if(suc):
		session = db.dbConn().get_session(db.dbConn().get_engine())
		checkSet = session.query(models.dataset).filter(models.dataset.user_id == test_user.id)[0]
		if(checkSet.isPublic == False):
			assert False, "Says that dataset was made public but it is still private"

	if(not suc):
		assert False, "Couldn't make dataset public for valid query"

def test_makeDatasetPrivate():

	session = db.dbConn().get_session(db.dbConn().get_engine())
	test_user = session.query(models.User).filter(models.User.email == test_email).first()

	session = db.dbConn().get_session(db.dbConn().get_engine())
	checkSet = session.query(models.dataset).filter(models.dataset.user_id == test_user.id)[0]

	jsonStr, suc = call_privateDatasets(test_user.id, checkSet.id)

	if(suc):
		session = db.dbConn().get_session(db.dbConn().get_engine())
		checkSet = session.query(models.dataset).filter(models.dataset.user_id == test_user.id)[0]
		if(checkSet.isPublic == True):
			assert False, "Says that dataset was made private but it is still public"

	if(not suc):
		assert False, "Couldn't make dataset private for valid query"

	session = db.dbConn().get_session(db.dbConn().get_engine())
	checkSet = session.query(models.dataset).filter(models.dataset.user_id == test_user.id)[1]

	jsonStr, suc = call_privateDatasets(test_user.id, checkSet.id)

	if(suc):
		session = db.dbConn().get_session(db.dbConn().get_engine())
		checkSet = session.query(models.dataset).filter(models.dataset.user_id == test_user.id)[0]
		if(checkSet.isPublic == True):
			assert False, "Says that dataset was made private but it is still private"

	if(not suc):
		assert False, "Couldn't make dataset private for valid query"

def test_user_delete():
	session = db.dbConn().get_session(db.dbConn().get_engine())
	delUser = session.query(models.User).filter(models.User.email == test_email).first()
	checkSet = session.query(models.dataset).filter(models.dataset.user_id == delUser.id).all()
	for temp in checkSet:
		session.delete(temp)
		session.commit()
	session = db.dbConn().get_session(db.dbConn().get_engine())
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

def call_upload_image(file):

	session = db.dbConn().get_session(db.dbConn().get_engine())
	checkUser = session.query(models.User).filter(models.User.email == test_email).first()

	temp = str(checkUser.id)
	f = open(file, 'rb')
	print(f)
	r = requests.post('http://127.0.0.1:5000/api/' + temp + '/upload/1', files={'file': f})
	jsonArr = json.loads(str(r.text))
	if(jsonArr['status'] == 200):
		return r.text, True
	else:
		return r.text, False

def call_upload_text(file):

	session = db.dbConn().get_session(db.dbConn().get_engine())
	checkUser = session.query(models.User).filter(models.User.email == test_email).first()

	temp = str(checkUser.id)
	f = open(file, 'rb')
	print(f)
	r = requests.post('http://127.0.0.1:5000/api/' + temp + '/upload/0', files={'file': f})
	jsonArr = json.loads(str(r.text))
	if(jsonArr['status'] == 200):
		return r.text, True
	else:
		return r.text, False

def call_getDatasets(userID):

	jsonString  = urllib2.urlopen(SERVER_ADDRESS + '/api/' + str(userID) + '/datasets').read()
	jsonArr = json.loads(jsonString)
	if(jsonArr['status']!=200):
		return jsonString, False
	return jsonString, True

def call_publicDatasets(user, dataset):
	jsonString  = urllib2.urlopen(SERVER_ADDRESS + '/api/' + str(user) + '/dataset/public/' + str(dataset) + '/').read()
	jsonArr = json.loads(jsonString)
	if(jsonArr['status']!=200):
		return str(jsonArr), False
	return str(jsonArr), True

def call_privateDatasets(user, dataset):
	jsonString  = urllib2.urlopen(SERVER_ADDRESS + '/api/' + str(user) + '/dataset/private/' + str(dataset) + '/').read()
	jsonArr = json.loads(jsonString)
	if(jsonArr['status']!=200):
		return str(jsonArr), False
	return str(jsonArr), True
