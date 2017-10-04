import os
from flask import request
import MySQLdb
from jsonReturn import apiDecorate
import models
from utils.dbConn import dbConn
from datetime import datetime
from random import randint
from utils.notification import notification

class userHandler():
    def login(self):
        ret = {}
        if request.method == "GET":
            argArray = request.args

        elif request.method  == "POST":
            argArray = request.form

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
        
        return apiDecorate(ret, 200, "Login Accepted")

    def register(self):
        ret = {}
        if request.method == "GET":
            argArray = request.args
        elif request.method  == "POST":
            argArray = request.form

        firstName = argArray.get("firstname")
        lastName = argArray.get("lastname")
        email = argArray.get("email")
        phone = argArray.get("phone")
        password = argArray.get("password")

            
        user = models.User(first_name = firstName, last_name=lastName, password=password, email=email, phone=phone)

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
        # sg_key = os.environ.get('sendgrid_apikey') or "none"
        # sg = sendgrid.SendGridAPIClient(apikey=sg_key)
        # from_email = Email("anirudhchellani@gmail.com")
        # to_email = Email(user.email)
        # subject = "Confirm your account"
        contentText = "Go to the link to verify " + "http://127.0.0.1:5000/api/verify/email/"+emailKey
        # content = Content("text/plain", "Go to the link to verify " + "http://127.0.0.1:5000/api/verify/email/"+emailKey)
        # mail = Mail(from_email, subject, to_email, content)
        # response = sg.client.mail.send.post(request_body=mail.get())

        res = notification.sendMail(fromEmail="anirudhchellani@gmail.com",toEmail=user.email, subject="Confirm your account", contentType="text/plain", content=contentText)
        print(res)
        ## Generate Phone key

    
        randNum = randint(1,10000)
        randNum2 = randint(1,10000)
        timeStamp = datetime.now()
        phoneKey = str(randNum) + str(timeStamp.year) + str(timeStamp.month) + str(timeStamp.day) + str(timeStamp.hour) + str(timeStamp.minute) + str(timeStamp.second) + "__" + str(randNum2)
        textContent="Go to the link to verify " + "http://127.0.0.1:5000/api/verify/phone/"+phoneKey
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

        if(curUser.isPhone == True):
            session.delete(userValidate)

        session.delete(userValidate)
        session.commit()
        return "User Validated"

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
        if(curUser.isEmail == True):
            session.delete(userValidate)
        session.commit()
        return "User Validated"