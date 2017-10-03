import os
from flask import request
import MySQLdb
from jsonReturn import apiDecorate
import models
from utils.dbConn import dbConn
from datetime import datetime
from random import randint
import sendgrid
from sendgrid.helpers.mail import *
from twilio.rest import Client

class userHandler():
    def login(self):
        username = request.args.get("username")
        if request.method == "GET":
            passwprd = request.args.get("password")

        elif request.method  == "POST":
            username = request.form.get("username")
            password = request.form.get("password")

        if  username and passwprd :
            testDict = {}
            testDict['test']="Success"
            return jsonReturn.apiDecorate(testDict)

        return "Failed"

    def register(self):
        ret = {}
        if request.method == "GET":
            firstName = request.args.get("firstname")
            lastName = request.args.get("lastname")
            email = request.args.get("email")
            phone = request.args.get("phone")
            password = request.args.get("password")

        elif request.method  == "POST":
            firstName = request.form.get("firstname")
            lastName = request.form.get("lastname")
            email = request.form.get("email")
            phone = request.form.get("phone")
            password = request.form.get("password")
            
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
        sg_key = os.environ.get('sendgrid_apikey') or "none"
        sg = sendgrid.SendGridAPIClient(apikey=sg_key)
        from_email = Email("anirudhchellani@gmail.com")
        to_email = Email(user.email)
        subject = "Confirm your account"
        content = Content("text/plain", "Go to the link to verify " + "http://127.0.0.1:5000/api/verify/email/"+emailKey)
        mail = Mail(from_email, subject, to_email, content)
        response = sg.client.mail.send.post(request_body=mail.get())
        print(response)
        ## Generate Phone key

    
        randNum = randint(1,10000)
        randNum2 = randint(1,10000)
        timeStamp = datetime.now()
        phoneKey = str(randNum) + str(timeStamp.year) + str(timeStamp.month) + str(timeStamp.day) + str(timeStamp.hour) + str(timeStamp.minute) + str(timeStamp.second) + "__" + str(randNum2)


        account_sid = os.environ.get('twillio_account_sid') or "none"
        auth_token  = os.environ.get('twillio_auth_token') or "none"

        twillio_client = Client(account_sid, auth_token)

        message = twillio_client.messages.create(
        to="+1"+user.phone, 
        from_="+1606-268-9633",
        body="Go to the link to verify " + "http://127.0.0.1:5000/api/verify/phone/"+phoneKey)

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