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

def test_allPublicDatasets():

 	session = db.dbConn().get_session(db.dbConn().get_engine())
	datasets = session.query(models.dataset).filter(models.dataset.isPublic == True).all()

	jsonStr, suc = call_allPublicDatasets()
	jsonArr = json.loads(jsonStr)


	if(suc):
		for s in jsonArr['datasets']:

			session = db.dbConn().get_session(db.dbConn().get_engine())
		   	temp = session.query(models.dataset).filter(models.dataset.resource_id == s['resource_name']).first()

			flag = False

			for t in datasets:
				x = t.resource_id + " " + temp.resource_id
				#assert False, x
				if(t.resource_id == temp.resource_id):
					flag = True

			if(flag == False):

				assert False, "Gives success but fails to retrieve some/all of the datasets"


	if(not suc):
		assert False, "Failed to retrieve all public datasets"

def test_copyPublicDataset():

	session = db.dbConn().get_session(db.dbConn().get_engine())
	test_user = session.query(models.User).filter(models.User.email == test_email).first()

	session = db.dbConn().get_session(db.dbConn().get_engine())
	dataset = session.query(models.dataset).filter(models.dataset.isPublic == True).first()

	jsonStr, suc = call_copyPublicDataset(test_user.id, dataset.id)

	if(not suc):
		assert False, "Failed to copy all public datasets"

	session = db.dbConn().get_session(db.dbConn().get_engine())
	datasets = session.query(models.dataset).filter(models.dataset.isPublic == True).all()

	flag = False

	for temp in datasets:
		if(temp.user_id == test_user.id):
			flag = True

	if(flag == False):
		assert False, "Returns success message but doesn't copy the datasets into given user ID"

def test_createExperiment():

	session = db.dbConn().get_session(db.dbConn().get_engine())
	test_user = session.query(models.User).filter(models.User.email == test_email).first()

	jsonStr, suc = call_createExperiment(test_user.id)

	if(not suc):
		assert False, "Experiment could not be created"

	session = db.dbConn().get_session(db.dbConn().get_engine())
	test_exp = session.query(models.experiments).filter(models.experiments.user_id == test_user.id).first()
	if(test_exp is None):
		assert False, "Gives success message but is not created in experiment table"

def test_getExperiments():

	session = db.dbConn().get_session(db.dbConn().get_engine())
	test_user = session.query(models.User).filter(models.User.email == test_email).first()

	jsonStr, suc = call_getExperiments(test_user.id)

	jsonArr = json.loads(jsonStr)
	if(not suc):
		assert False, "Could not receive all experiment"

	#assert False, jsonStr

	session = db.dbConn().get_session(db.dbConn().get_engine())

	if(len(jsonArr['experiments']) != session.query(models.experiments).count()):
		assert False, "Gives success message but doesn't return all experiments"

def test_assignBatch():

	session = db.dbConn().get_session(db.dbConn().get_engine())
	test_user = session.query(models.User).filter(models.User.email == test_email).first()

	session = db.dbConn().get_session(db.dbConn().get_engine())
	test_experiment = session.query(models.experiments).filter(models.experiments.user_id == test_user.id).first()

	jsonStr, suc = call_assignBatch(test_user.id, test_experiment.id)

	if(not suc):
		assert False, "Did not assign batch"

	jsonArr = json.loads(jsonStr)

	session = db.dbConn().get_session(db.dbConn().get_engine())
	test_batch = session.query(models.batch).filter(models.batch.id == jsonArr['batch_id']).first()

	if(test_batch.user_id != test_user.id):
		assert False, "Didn't assign batch to right user ID"

def test_batchList():

	session = db.dbConn().get_session(db.dbConn().get_engine())
	test_user = session.query(models.User).filter(models.User.email == test_email).first()

	session = db.dbConn().get_session(db.dbConn().get_engine())
	test_batch = session.query(models.batch).filter(models.batch.user_id == test_user.id).first()

	jsonStr, suc = call_batchList(test_user.id)
	jsonArr = json.loads(jsonStr)

	if(not suc):
		assert False, "Could not give a list of batches"

	if(test_batch.id != jsonArr['batches'][0]['id']):

		assert False, "Returned success but didn't return a correct list of batches"
'''
def test_getBatch():


	session = db.dbConn().get_session(db.dbConn().get_engine())
	test_user = session.query(models.User).filter(models.User.email == test_email).first()

	session = db.dbConn().get_session(db.dbConn().get_engine())
	test_batch = session.query(models.batch).filter(models.batch.user_id == test_user.id).first()

	#assert False, int(test_batch.id)

	jsonStr, suc = call_getBatch(int(test_batch.id))
	#jsonArr = json.loads(jsonStr)

	assert False, jsonStr
'''

def test_rateBatch():

	session = db.dbConn().get_session(db.dbConn().get_engine())
	test_user = session.query(models.User).filter(models.User.email == test_email).first()

	session = db.dbConn().get_session(db.dbConn().get_engine())
	test_batch = session.query(models.batch).filter(models.batch.user_id == test_user.id).first()
	test_batch.isCompleted = True
	session.commit()

	jsonStr, suc = call_rateBatch(test_batch.id, 4)

	if(not suc):
		assert False, "Could not rate participant"

	session = db.dbConn().get_session(db.dbConn().get_engine())
	test_batch = session.query(models.batch).filter(models.batch.user_id == test_user.id).first()

	if(test_batch.rating != 4):
		assert False, "Returned success but didn't input correct value"

def test_getPastExperiments():

	session = db.dbConn().get_session(db.dbConn().get_engine())
	test_user = session.query(models.User).filter(models.User.email == test_email).first()

	session = db.dbConn().get_session(db.dbConn().get_engine())
	test_batch = session.query(models.batch).filter(models.batch.user_id == test_user.id).first()

	jsonStr, suc = call_getPastExperiments(test_user.id)

	if(not suc):
		assert False, "Failed to return past experiments"

	if(test_batch.isCompleted == False):
		assert False, "Returned success but didn't provide all prior experiments"

def test_getExperimentsProgress():

	session = db.dbConn().get_session(db.dbConn().get_engine())
	test_user = session.query(models.User).filter(models.User.email == test_email).first()

	#session = db.dbConn().get_session(dbConn().get_engine())
	experiment = session.query(models.experiments).filter(models.experiments.user_id == test_user.id).first()

	checkBatch = session.query(models.batch).filter(models.batch.experiment_id == experiment.resource_id).all()
	#assert False, len(checkBatch)
	com = 0

	for batch in checkBatch:
		if(batch.curAnnotation == batch.totalAnnotation):
			com = com + 1;


	jsonStr, suc = call_getExperimentProgress(test_user.id)
	jsonArr = json.loads(jsonStr)

	if(not suc):
		assert False, "Could not return progress"

	if(jsonArr['experiments'][0]['completed'] != com):
		assert False, "Returns succes but fails to return correct progress"

def test_getBatchToRate():

	session = db.dbConn().get_session(db.dbConn().get_engine())
	test_user = session.query(models.User).filter(models.User.email == test_email).first()

	#session = db.dbConn().get_session(dbConn().get_engine())
	experiment = session.query(models.experiments).filter(models.experiments.user_id == test_user.id).first()
	checkBatch = session.query(models.batch).filter(models.batch.experiment_id == experiment.resource_id).first()
	#checkBatch.isCompleted = True
	session.commit()

	session = db.dbConn().get_session(db.dbConn().get_engine())
	test_user = session.query(models.User).filter(models.User.email == test_email).first()

	#session = db.dbConn().get_session(dbConn().get_engine())
	experiment = session.query(models.experiments).filter(models.experiments.user_id == test_user.id).first()

	jsonStr, suc = call_getBatchToRate(experiment.id)
	jsonArr = json.loads(jsonStr)

	if(not suc):
		assert False, "Does not return a batch to rate"

	'''
	t = str(checkBatch.isCompleted) + " " + str(experiment.resource_id) + " " + str(checkBatch.experiment_id) + " " +  str(len(jsonArr['batches']))
	assert False, t
	'''
	if(len(jsonArr['batches']) != 0):
		assert False, "Returns wrong number of batches"

def test_getExperimentDetails():

	session = db.dbConn().get_session(db.dbConn().get_engine())
	test_user = session.query(models.User).filter(models.User.email == test_email).first()

	#session = db.dbConn().get_session(dbConn().get_engine())
	experiment = session.query(models.experiments).filter(models.experiments.user_id == test_user.id).first()
	jsonStr, suc = call_getExperimentDetails(experiment.id)

	if(not suc):
		assert False, "Doesn't return experiment details"

	jsonArr = json.loads(jsonStr)

	if(jsonArr['id'] != experiment.id):
		assert False, "Returns success but experiment details are wrong"

def test_getUserBalance():

	session = db.dbConn().get_session(db.dbConn().get_engine())
	test_user = session.query(models.User).filter(models.User.email == test_email).first()

	jsonStr, suc = call_getUserBalance(test_user.id)

	jsonArr = json.loads(jsonStr)

	if(not suc):
		assert False, "Fails to return balance"

	if(jsonArr['balance'] != test_user.balance):
		assert False, "Returns success message but balance shown is not correct"


def test_user_delete():
	session = db.dbConn().get_session(db.dbConn().get_engine())
	delUser = session.query(models.User).filter(models.User.email == test_email).first()
	checkExp = session.query(models.experiments).filter(models.experiments.user_id == delUser.id).first()
	checkBatch = session.query(models.batch).filter(models.batch.experiment_id == checkExp.resource_id).all()

	for temp in checkBatch:
		session.delete(temp)
	session.commit()

	session = db.dbConn().get_session(db.dbConn().get_engine())
	checkExp = session.query(models.experiments).filter(models.experiments.user_id == delUser.id).all()

	for temp in checkExp:
		session.delete(temp)
	session.commit()

	session = db.dbConn().get_session(db.dbConn().get_engine())
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

def call_allPublicDatasets():
	jsonString  = urllib2.urlopen(SERVER_ADDRESS + '/api/datasets/public').read()
	print(jsonString)
	jsonArr = json.loads(jsonString)
	if(jsonArr['status']!=200):
		return str(jsonArr), False
	return jsonString, True

def call_copyPublicDataset(user, dataset):
	jsonString  = urllib2.urlopen(SERVER_ADDRESS + '/api/' + str(user) + '/dataset/copy/' + str(dataset) + '/').read()
	jsonArr = json.loads(jsonString)
	if(jsonArr['status']!=200):
		return str(jsonArr), False
	return str(jsonArr), True

def call_createExperiment(user):

	session = db.dbConn().get_session(db.dbConn().get_engine())
	checkUser = session.query(models.User).filter(models.User.email == test_email).first()
	checkUser.balance = 2000
	session.commit()

	session = db.dbConn().get_session(db.dbConn().get_engine())
	checkSet = session.query(models.dataset).filter(models.dataset.user_id == user).first()

	temp = 0
	if(checkSet.isMedia):
		temp = 1

	jsonString = urllib2.urlopen(SERVER_ADDRESS + '/api/' + str(user) + '/create?dataset_id=' + str(checkSet.id) + '&batchSize=1&user_id=' + str(user)
	+ '&price=1&description=IMAGE&isPhone=3126469650&datasetType=' + str(temp) + '&title=FirstExperiment').read()

	jsonArr = json.loads(jsonString)

	#assert False, jsonArr['status']
 	if(jsonArr['status'] == 200):
 		return jsonString, True
 	else:
 		return jsonString, False


def call_getExperiments(user):

	jsonString  = urllib2.urlopen(SERVER_ADDRESS + '/api/getExperiments/' + str(user)).read()

	jsonArr = json.loads(jsonString)

	print(jsonString)
	if(jsonArr['status']!=200):
		return str(jsonArr), False
	return jsonString, True


def call_assignBatch(user, experiment):

	jsonString  = urllib2.urlopen(SERVER_ADDRESS + '/api/' + str(user) + '/assign/' + str(experiment)).read()
	jsonArr = json.loads(jsonString)

	print(jsonString)

	if(jsonArr['status']!=200):
		return str(jsonArr), False
	return jsonString, True

def call_batchList(user):


	jsonString  = urllib2.urlopen(SERVER_ADDRESS + '/api/' + str(user) + '/batchList').read()

	jsonArr = json.loads(jsonString)

	#print(jsonString)
	if(jsonArr['status']!=200):
		return str(jsonArr), False
	return jsonString, True

def call_getBatch(batch_id):

	jsonString  = urllib2.urlopen(SERVER_ADDRESS + '/api/' + str(batch_id) + '/getBatch').read()

	#jsonArr = json.loads(jsonString)

	#assert False, jsonString
	#print(jsonString)
	if(jsonArr['status']!=200):
		return str(jsonArr), False
	return jsonString, True


def call_getBatch(batch_id):

	jsonString  = urllib2.urlopen(SERVER_ADDRESS + '/api/' + str(batch_id) + '/getBatch').read()

	jsonArr = json.loads(jsonString)

	#assert False, jsonString
	#print(jsonString)
	if(jsonArr['status']!=200):
		return str(jsonArr), False
	return jsonString, True

def call_rateBatch(batch_id, rating):

	jsonString  = urllib2.urlopen(SERVER_ADDRESS + '/api/' + str(batch_id) + '/rateBatch/' + str(rating)).read()

	jsonArr = json.loads(jsonString)

	#assert False, jsonString
	#print(jsonString)
	if(jsonArr['status']!=200):
		return str(jsonArr), False
	return jsonString, True

def call_getPastExperiments(user_id):

	jsonString  = urllib2.urlopen(SERVER_ADDRESS + '/api/getPastExperiments/' + str(user_id)).read()

	jsonArr = json.loads(jsonString)

	#assert False, jsonString
	#print(jsonString)
	if(jsonArr['status']!=200):
		return str(jsonArr), False
	return jsonString, True

def call_getExperimentProgress(user_id):

	jsonString  = urllib2.urlopen(SERVER_ADDRESS + '/api/getExperimentProgress/' + str(user_id)).read()

	jsonArr = json.loads(jsonString)

	if(jsonArr['status']!=200):
		return str(jsonArr), False
	return jsonString, True

def call_getBatchToRate(experiment_id):

	jsonString  = urllib2.urlopen(SERVER_ADDRESS + '/api/getBatchToRate/' + str(experiment_id)).read()

	jsonArr = json.loads(jsonString)

	if(jsonArr['status']!=200):
		return str(jsonArr), False
	return jsonString, True

def call_getExperimentDetails(experiment_id):

	jsonString  = urllib2.urlopen(SERVER_ADDRESS + '/api/getExperimentDetails/' + str(experiment_id)).read()

	jsonArr = json.loads(jsonString)

	if(jsonArr['status']!=200):
		return str(jsonArr), False
	return jsonString, True

def call_getUserBalance(user_id):

	jsonString  = urllib2.urlopen(SERVER_ADDRESS + '/api/userBalance/' + str(user_id)).read()

	jsonArr = json.loads(jsonString)

	if(jsonArr['status']!=200):
		return str(jsonArr), False
	return jsonString, True

'''
session = db.dbConn().get_session(db.dbConn().get_engine())
test_user = session.query(models.User).filter(models.User.email == 'singh351@purdue.edu').first()

test_user.balance = 10000
session.commit()


session = db.dbConn().get_session(db.dbConn().get_engine())
test_experiment = session.query(models.experiments).filter(models.experiments.id == 1).first()

call_assignBatch(test_user.id, test_experiment.id)
'''
