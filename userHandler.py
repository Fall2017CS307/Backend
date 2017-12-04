import os
from flask import request
import MySQLdb
from jsonReturn import apiDecorate
import models
from utils.dbConn import dbConn
from datetime import datetime
from random import randint
from utils.notification import notification
import json
class userHandler():

    @staticmethod
    def getUserById(user_id):
        session = dbConn().get_session(dbConn().get_engine())
        retUser = session.query(models.User).filter(models.User.id == user_id).first()
        if(retUser is None):
            return ""
        ret = {}
        ret['id'] = retUser.id
        ret['name'] = retUser.first_name
        return json.dumps(ret)


    def login(self):
        ret = {}
        if request.method == "GET":
            argArray = request.args

        elif request.method  == "POST":
            if(len(request.form) > 0):
                argArray = request.form
            else:
                print request.get_data()
                argArray = json.loads(request.data)


        user = models.User(password=argArray.get("password"), email=argArray.get("email"))
        if  not user.email or not user.password :
            ret['errors'] = []
            ret['errors'].append("Invalid and/or expired key supplied")
            return apiDecorate(ret, 400, "Invalid and/or expired key supplied")

        session = dbConn().get_session(dbConn().get_engine())
        user = session.query(models.User).filter(models.User.email == user.email).filter(models.User.password == user.password).filter(models.User.isEmail == 1).filter(models.User.isPhone == 1).first()

        if user is None:
            ret['errors'] = []
            ret['errors'].append("Incorect User/password combinator or the user is not registered")
            return apiDecorate(ret, 400, "Invalid and/or expired key supplied")
        ret['id'] = user.id

        return apiDecorate(ret, 200, "Login Accepted")

    def register(self):
        ret = {}
        if request.method == "GET":
            argArray = request.args
        elif request.method  == "POST":
            if(len(request.form) > 0):
                argArray = request.form
            else:
                print request.get_data()
                argArray = json.loads(request.data)

        firstName = argArray.get("firstname")
        lastName = argArray.get("lastname")
        email = argArray.get("email")
        phone = argArray.get("phone")
        password = argArray.get("password")
        gender = argArray.get("gender")
        country = argArray.get("country")
        skill = argArray.get("skill")


        user = models.User(first_name = firstName, last_name=lastName, password=password, email=email, phone=phone, gender=gender, country=country,skill=skill)

        if len(user.errors) > 0:
            ret['errors'] = user.errors
            return apiDecorate(ret, 400, "Invalid and/or incomplete data specified")
            return apiDecorate(ret)

        session = dbConn().get_session(dbConn().get_engine())
        checkUser = session.query(models.User).filter(models.User.email == email).first()
        if(checkUser is not None):
            ret['errors'] = []
            ret['errors'].append("User already exists")
            return apiDecorate(ret, 400, "User already exists")

        session.add(user)
        session.commit()

        ## Generate email key
        randNum = randint(1,10000)
        randNum2 = randint(1,10000)
        timeStamp = datetime.now()
        emailKey = str(randNum) + str(timeStamp.year) + str(timeStamp.month) + str(timeStamp.day) + str(timeStamp.hour) + str(timeStamp.minute) + str(timeStamp.second) + "_" + str(randNum2)
        contentText = "Go to the link to verify " + "http://datonate.com:5000/api/verify/email/"+emailKey

        res = notification.sendMail(fromEmail="anirudhchellani@gmail.com",toEmail=user.email, subject="Confirm your account", contentType="text/plain", content=contentText)
        print(res)
        ## Generate Phone key


        randNum = randint(1,10000)
        randNum2 = randint(1,10000)
        timeStamp = datetime.now()
        phoneKey = str(randNum) + str(timeStamp.year) + str(timeStamp.month) + str(timeStamp.day) + str(timeStamp.hour) + str(timeStamp.minute) + str(timeStamp.second) + "__" + str(randNum2)
        textContent="Go to the link to verify " + "http://datonate.com:5000/api/verify/phone/"+phoneKey
        message = notification.sendText(user.phone,textContent)
        regUser = session.query(models.User).filter(models.User.email == user.email).first()

        userValidate = models.user_validate(regUser.id, emailKey, phoneKey)
        session.add(userValidate)
        session.commit()

        return apiDecorate(ret, 200, "User Added")

    def verify_email(self,key):
        ret = {}
        if key is None:
            ret['errors'] = []
            ret['errors'].append("Invalid and/or expired key supplied")
            return apiDecorate(ret, 400, "Invalid and/or expired key supplied")

        session = dbConn().get_session(dbConn().get_engine())
        userValidate = session.query(models.user_validate).filter(models.user_validate.emailCode == key).first()
        if(userValidate is None):
            ret['errors'] = []
            ret['errors'].append("Invalid and/or expired key supplied")
            return apiDecorate(ret, 400, "Invalid and/or expired key supplied")
        curUser = session.query(models.User).filter(models.User.id == userValidate.id).first()
        if(curUser is None):
            ret['errors'] = []
            ret['errors'].append("Server Error")
            return apiDecorate(ret, 500, "Server Error")
        curUser.isEmail = True
        session.commit()
        if(curUser.isPhone == True):
            session.delete(userValidate)
        session.commit()
        return apiDecorate(ret, 200, "Verified")

    def verify_phone(self,key):
        ret = {}
        if key is None:
            ret['errors'] = []
            ret['errors'].append("Invalid and/or expired key supplied")
            return apiDecorate(ret, 400, "Invalid and/or expired key supplied")

        session = dbConn().get_session(dbConn().get_engine())
        userValidate = session.query(models.user_validate).filter(models.user_validate.phoneCode == key).first()
        if(userValidate is None):
            ret['errors'] = []
            ret['errors'].append("Invalid and/or expired key supplied")
            return apiDecorate(ret, 400, "Invalid and/or expired key supplied")
        curUser = session.query(models.User).filter(models.User.id == userValidate.id).first()
        if(curUser is None):
            ret['errors'] = []
            ret['errors'].append("Server Error")
            return apiDecorate(ret, 500, "Server Error")
        curUser.isPhone = True
        session.commit()
        if(curUser.isEmail == True):
            session.delete(userValidate)
        session.commit()
        return apiDecorate(ret, 200, "Verified")

    def getUser(self,id):
        session = dbConn().get_session(dbConn().get_engine())
        user = session.query(models.User).filter(models.User.id == id).first()
        return user

    def getDatasets(self, user_id):
        ret = {}
        user = self.getUser(user_id)
        if user is None:
            ret['errors'] = []
            ret['errors'].append("Invalid User")
            return apiDecorate(ret, 400, "Invalid User")

        session = session = dbConn().get_session(dbConn().get_engine())
        datasets = session.query(models.dataset).filter(models.dataset.user_id == user_id).all()
        returnDict = []
        for data in datasets:
            returnData = {}
            returnData['id'] = data.id
            returnData['resource_name'] = data.resource_id
            if(data.isPublic == True):
                returnData['status'] = "Public"
            else:
                returnData['status'] = "Private"
            returnDict.append(returnData)
        ret['datasets'] = returnDict
        return apiDecorate(ret, 200, "Success")

    def deleteDataset(self, user_id, dataset_id):
        ret = {}
        user = self.getUser(user_id)
        if user is None:
            ret['errors'] = []
            ret['errors'].append("Invalid User")
            return apiDecorate(ret, 400, "Invalid User")

        session = session = dbConn().get_session(dbConn().get_engine())
        dataset = session.query(models.dataset).filter(models.dataset.user_id == user_id).filter(models.dataset.id == dataset_id).first()
        if dataset is None:
            ret['errors'] = []
            ret['errors'].append("Invalid dataset or user doesnt own the dataset")
            return apiDecorate(ret, 400, "Invalid dataset or user doesnt own the dataset")
        session.delete(dataset)
        session.commit()
        return apiDecorate(ret, 200, "Success")


    def makeDatasetPublic(self, user_id, dataset_id):
        ret = {}
        user = self.getUser(user_id)
        if user is None:
            ret['errors'] = []
            ret['errors'].append("Invalid User")
            return apiDecorate(ret, 400, "Invalid User")

        session = session = dbConn().get_session(dbConn().get_engine())
        dataset = session.query(models.dataset).filter(models.dataset.user_id == user_id).filter(models.dataset.id == dataset_id).first()
        if dataset is None:
            ret['errors'] = []
            ret['errors'].append("Invalid dataset or user doesnt own the dataset")
            return apiDecorate(ret, 400, "Invalid dataset or user doesnt own the dataset")

        dataset.isPublic = True
        session.commit()

        return apiDecorate(ret, 200, "Success")


    def makeDatasetPrivate(self, user_id, dataset_id):
        ret = {}
        user = self.getUser(user_id)
        if user is None:
            ret['errors'] = []
            ret['errors'].append("Invalid User")
            return apiDecorate(ret, 400, "Invalid User")

        session = session = dbConn().get_session(dbConn().get_engine())
        dataset = session.query(models.dataset).filter(models.dataset.user_id == user_id).filter(models.dataset.id == dataset_id).first()
        if dataset is None:
            ret['errors'] = []
            ret['errors'].append("Invalid dataset or user doesnt own the dataset")
            return apiDecorate(ret, 400, "Invalid dataset or user doesnt own the dataset")

        dataset.isPublic = False
        session.commit()

        return apiDecorate(ret, 200, "Success")

    def toggleDataset(self,user_id,dataset_id):
        ret = {}
        user = self.getUser(user_id)
        if user is None:
            ret['errors'] = []
            ret['errors'].append("Invalid User")
            return apiDecorate(ret, 400, "Invalid User")

        session = session = dbConn().get_session(dbConn().get_engine())
        dataset = session.query(models.dataset).filter(models.dataset.user_id == user_id).filter(models.dataset.id == dataset_id).first()
        
        if dataset is None:
            ret['errors'] = []
            ret['errors'].append("Invalid dataset or user doesnt own the dataset")
            return apiDecorate(ret, 400, "Invalid dataset or user doesnt own the dataset")
        
        if(dataset.isPublic == False):
            dataset.isPublic = True
        else:
            dataset.isPublic = False
        session.commit()
        return apiDecorate(ret, 200, "Success")
        
    def getPublicDatasets(self):
        ret = {}
        session = session = dbConn().get_session(dbConn().get_engine())
        datasets = session.query(models.dataset).filter(models.dataset.isPublic == True).all()
        returnDict = []
        for data in datasets:
            returnData = {}
            #returnData['file_name'] = data.file_name
            returnData['resource_name'] = data.resource_id
            returnData['id'] = data.id
            returnDict.append(returnData)
        ret['datasets'] = returnDict
        return apiDecorate(ret, 200, "Success")


    def copyPublicDataset(self, user_id, dataset_id):
        ret = {}
        user = self.getUser(user_id)
        if user is None:
            ret['errors'] = []
            ret['errors'].append("Invalid User")
            return apiDecorate(ret, 400, "Invalid User")

        session = session = dbConn().get_session(dbConn().get_engine())
        dataset = session.query(models.dataset).filter(models.dataset.id == dataset_id).filter(models.dataset.isPublic==True).first()
        if dataset is None:
            ret['errors'] = []
            ret['errors'].append("Invalid dataset or dataset is not public")
            return apiDecorate(ret, 400, "Invalid dataset or dataset is not public")

        #copyDataset = models.dataset(user.id, file_name=dataset.file_name, resource_id=dataset.resource_id)
        copyDataset = models.dataset(user.id, isMedia=dataset.isMedia, resource_id=dataset.resource_id)
        session.add(copyDataset)
        session.commit()
        copyDataset.isPublic = True
        session.commit()
        return apiDecorate(ret, 200, "Success")
        
    def getBalance(self,user_id):
        ret = {}
        user = self.getUser(user_id)
        if user is None:
            ret['errors'] = []
            ret['errors'].append("Invalid User")
            return apiDecorate(ret, 400, "Invalid User")
            
        ret['balance'] = user.balance
        return apiDecorate(ret,200,"success")
         
