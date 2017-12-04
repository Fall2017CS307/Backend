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
    def imgFile(zipF):
        zipList = zipF.namelist()
        print "imgFile"
        files = []
        fileNames = []
        for fileName in zipList:
            fileByte = str(zipF.read(fileName))
            if imghdr.what(None,h=fileByte) is not None:
                print fileName
                fileArr = {}
                fileNames.append(fileName)
                fileArr['name'] = fileName
                fileArr['fileByte'] = fileByte
                files.append(fileArr)
        if(len(files) <=0):
            return None
        dumpString = json.dumps(fileNames, ensure_ascii=False)
        
        fileArr = {}
        fileArr['name'] = 'file_list.json'
        fileArr['fileByte'] = dumpString
        files.append(fileArr)
        
        return files

    @staticmethod
    def jsonFile(zipF):
        zipList = zipF.namelist()
        if(len(zipList)!=1):
            return None
        jsonArr = []
        fileContent = str(zipF.read(zipList[0]))
        try:
            fileArr = json.loads(fileContent)
            if(not (type(fileArr) is list)):
                return None
            for item in fileArr:
                print item
                if(not (type(item) is dict)):
                    continue

                question = str(item.get("question"))
                print type(question)
                if(not(type(question) is str)):
                    continue
                addInfo = str(item.get("addInfo"))

                itemArr = {}
                itemArr['question'] = question
                itemArr['addInfo'] = addInfo
                jsonArr.append(itemArr)

            if(len(jsonArr) <1):
                return None
            
        except:
            print "Except"
            return None
        fileArr = {}
        files = []
        fileArr['name'] = 'file_list.json'
        fileArr['fileByte'] = json.dumps(jsonArr)
        files.append(fileArr)
        return files
    
    @staticmethod
    def uploadFile(user_id, datasetType):

        ret = {}
        argArray = {}
        if request.method == "GET":
            argArray = request.args

        elif request.method  == "POST":
            if(len(request.form) > 0):
                argArray = request.form
            else:
                print request.get_data()
                argArray = json.loads(request.data)
        user = userHandler().getUser(user_id)

        if user is None:
            ret['errors'] = []
            ret['errors'].append("User doesnt't exist/not logged in")
            return apiDecorate(ret, 400, "User doesnt't exist/not logged in")

        if 'file' not in request.files:
            ret['errors'] = []
            ret['errors'].append("File not supplied")
            return apiDecorate(ret, 400, "File not supplied")
        
        if(datasetType!=0 and datasetType!=1):
            ret['errors'] = []
            ret['errors'].append("Invalid Type")
            return apiDecorate(ret, 400, "Invalid Type")

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
        randName = randName_noext
        storageLocation = os.path.join(fileHandler.UPLOAD_FOLDER, randName)
        uploadedFile.save(storageLocation)

        fileSize = os.stat(storageLocation).st_size

        if(not zipfile.is_zipfile(storageLocation)):
            ret['errors'] = []
            ret['errors'].append("Invalid File, File not a valid zip file")
            return apiDecorate(ret, 400, "Invalid File")
        
        zipF = zipfile.ZipFile(storageLocation)
        if(datasetType == 0):
            fileArr = fileHandler.jsonFile(zipF)
        else:
            fileArr = fileHandler.imgFile(zipF)
        if(fileArr is None):
            ret['errors'] = []
            ret['errors'].append("Zip file empty or contains invalid/incompatible files")
            return apiDecorate(ret, 400, "Zip file empty")
        botoConn = boto.connect_s3(fileHandler.DREAM_key, fileHandler.DREAM_secretKey, host="objects-us-west-1.dream.io")
        bucket = botoConn.get_bucket(fileHandler.DREAM_Bucket, validate=False)

        for file in fileArr:
            k = Key(bucket)
            k.key = randName+"/"+file['name']
            sent = k.set_contents_from_string(file['fileByte'], cb=None, md5=None, reduced_redundancy=False)
            print len(file['fileByte'])
            print sent

        data = models.dataset(user_id=user_id, isMedia=datasetType, resource_id=randName)
        data.title = argArray.get("dataset_title") or "No Title Given"
        session = dbConn().get_session(dbConn().get_engine())
        session.add(data)
        session.commit()
        return apiDecorate(ret, 200, "Verified")

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
