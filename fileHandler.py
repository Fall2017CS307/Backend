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
import boto
from boto.s3.key import Key
from os.path import getsize
import zipfile
import imghdr
import csv
import json

class fileHandler():
    UPLOAD_FOLDER = './static/uploads'
    ALLOWED_EXTENSIONS = set(['zip'])
    DREAM_username = os.environ.get('dream_user') or "none"
    DREAM_secretKey = os.environ.get('dream_secretKey') or "none"
    DREAM_Bucket = os.environ.get('dream_bucket') or "none"
    DREAM_auth = os.environ.get('dream_auth') or "none"
    DREAM_key = os.environ.get('dream_key') or "none"

    @staticmethod
    def allowed_file(filename):
        return '.' in filename and \
            filename.rsplit('.', 1)[1].lower() in fileHandler.ALLOWED_EXTENSIONS


    @staticmethod
    def csvFile(zipF,zipList):
        readObject = str(zipF.read(zipList[0]))
        csvObject = csv.reader(readObject)
        csvArr = {}
        csvArr['cue'] = []
        for row in csvObject:
            print row
            #print row[0]
            #if(not isinstance(row,str)):
             #   print "Here"
              #  return None
            csvArr['cue'].append(row)
        if(not len(csvArr['cue'])):
            print "LOL"
            return None
        fileArr = []
        fileArr.append(json.dumps(csvArr))
        print(fileArr[0])
        return fileArr
    
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
        randName_noext = str(randNum) + str(timeStamp.year) + str(timeStamp.month) + randString + str(timeStamp.day) + str(timeStamp.hour) + str(timeStamp.minute) + str(timeStamp.second) + str(randNum2)
        randName = randName_noext+".zip"
        storageLocation = os.path.join(fileHandler.UPLOAD_FOLDER, randName)
        uploadedFile.save(storageLocation)

        fileSize = os.stat(storageLocation).st_size

        if(not zipfile.is_zipfile(storageLocation)):
            ret['errors'] = []
            ret['errors'].append("Invalid File, File not a valid zip file")
            return apiDecorate(ret, 400, "Invalid File")
        
        zipF = zipfile.ZipFile(storageLocation)
        zipList = zipF.namelist()
        countFiles = len(zipList)
        #print countFiles
        if(countFiles <= 0):
            ret['errors'] = []
            ret['errors'].append("Zip file empty")
            return apiDecorate(ret, 400, "Zip file empty")
        if(countFiles == 1):
            fileArrr = fileHandler.csvFile(zipF,zipList)
            if(fileArrr is None):
                ret['errors'] = []
                ret['errors'].append("Invalid File, File not a valid zip file")
                return apiDecorate(ret, 400, "Invalid File")
        fileRead = open(storageLocation, 'r+')



        botoConn = boto.connect_s3(fileHandler.DREAM_key, fileHandler.DREAM_secretKey, host="objects-us-west-1.dream.io")
        bucket = botoConn.get_bucket(fileHandler.DREAM_Bucket, validate=True)
        k = Key(bucket)
        k.key = randName
        sent = k.set_contents_from_file(fileRead, cb=None, md5=None, reduced_redundancy=False, rewind=True)


        if sent != fileSize:
            return "false"

        data = models.dataset(user_id=user_id, file_name=uploadedFile.filename, resource_id=randName)

        session = dbConn().get_session(dbConn().get_engine())
        session.add(data)
        session.commit()
        return "true " + randName 

@staticmethod
def retDatasets(user_id):

    ret = {}
    user = userHandler().getUser(user_id)


    session = dbConn().get_session(dbConn().get_engine())
    allUserDatasets = session.query(models.dataset).filter(models.dataset.user_id == user.id).all()

    if(allUserDatasets is None):
        ret['errors'] = []
        ret['errors'].append("No files uploaded")
        return apiDecorate(ret, 400, "User has not uploaded any files")
