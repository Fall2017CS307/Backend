import os
import random
from flask import request, redirect, url_for
import MySQLdb
from jsonReturn import apiDecorate
import models
from utils.dbConn import dbConn
from datetime import datetime
from random import randint
from utils.notification import notification
from userHandler import userHandler
from werkzeug.utils import secure_filename
import cloudfiles

class fileHandler():
    UPLOAD_FOLDER = './static/uploads'
    ALLOWED_EXTENSIONS = set(['zip'])
    DREAM_username = os.environ.get('dream_user') or "none"
    DREAM_key = os.environ.get('dream_key') or "none"
    DREAM_Bucket = os.environ.get('dream_bucket') or "none"
    DREAM_auth = os.environ.get('dream_auth') or "none"

    @staticmethod
    def allowed_file(filename):
        return '.' in filename and \
            filename.rsplit('.', 1)[1].lower() in fileHandler.ALLOWED_EXTENSIONS


    @staticmethod
    def uploadFile(user_id):
        
        ret = {}
        user = userHandler().getUser(user_id)
        
        if user is None:
            ret['errors'] = []
            ret['errors'].append("User doesnt't exist/not logged in")
            return apiDecorate(ret, 400, "User doesnt't exist/not logged in")
        
        if 'file' not in request.files:
            ret['errors'] = []
            ret['errors'].append("File not supplied")
            return apiDecorate(ret, 400, "File not supplied") 
        
        uploadedFile = request.files['file']
        
        if not uploadedFile:
            ret['errors'] = []
            ret['errors'].append("File not supplied")
            return apiDecorate(ret, 400, "File not supplied") 

        if not fileHandler.allowed_file(uploadedFile.filename):
            ret['errors'] = []
            ret['errors'].append("File not supported")
            return apiDecorate(ret, 400, "File not supported") 

        filename = secure_filename(uploadedFile.filename)

        randNum = randint(1,10000)
        randNum2 = randint(1,10000)
        randString = ''.join(random.choice('0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ') for i in range(randint(10,20)))
        timeStamp = datetime.now()
        randName = str(randNum) + str(timeStamp.year) + str(timeStamp.month) + randString + str(timeStamp.day) + str(timeStamp.hour) + str(timeStamp.minute) + str(timeStamp.second) + str(randNum2) + ".zip"
        storageLocation = os.path.join(fileHandler.UPLOAD_FOLDER, randName)
        uploadedFile.save(storageLocation)
        print storageLocation

        dreamConn = cloudfiles.get_connection(username=fileHandler.DREAM_username,api_key=fileHandler.DREAM_key,authurl=fileHandler.DREAM_auth, )
        dreamContainer = dreamConn.get_container(fileHandler.DREAM_Bucket)
        obj = dreamContainer.create_object(randName)
        obj.load_from_filename(storageLocation)
        
        return randName
