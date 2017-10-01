from flask import request
import MySQLdb
from jsonReturn import apiDecorate
import models
from utils.dbConn import dbConn
class userHandler():
    def login(self):
        if request.method == "GET":
            username = request.args.get("username")
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
        if(checkUser is None):
            session.add(user)
            session.commit()
            return apiDecorate(ret, 200, "User Added")
        else:
            ret['errors'] = []
            ret['errors'].append("User already exists")
            return apiDecorate(ret, 400, "User already exists")
            return apiDecorate(ret)