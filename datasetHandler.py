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

class datasetHandler:
    DREAM_username = os.environ.get('dream_user') or "none"
    DREAM_secretKey = os.environ.get('dream_secretKey') or "none"
    DREAM_Bucket = os.environ.get('dream_bucket') or "none"
    DREAM_auth = os.environ.get('dream_auth') or "none"
    DREAM_key = os.environ.get('dream_key') or "none"
    
    @staticmethod
    def makeMediaBatches(dataset, batchSize):
        ret = {}
        botoConn = boto.connect_s3(datasetHandler.DREAM_key, datasetHandler.DREAM_secretKey, host="objects-us-west-1.dream.io")
        bucket = botoConn.get_bucket(datasetHandler.DREAM_Bucket, validate=False)
        k = Key(bucket)
        k.key=dataset.resource_id+"/file_list.json"
        fileJson = k.get_contents_as_string()
        filesArr =  json.loads(fileJson)
        if(batchSize > len(filesArr) or batchSize <= 0):
            return None
        random.shuffle(filesArr)
        fileLen = len(filesArr)
        batches = []
        curIndex = 0
        while(curIndex<fileLen):
            batches.append(filesArr[curIndex:curIndex+batchSize])
            curIndex+=batchSize
        return batches

    @staticmethod
    def createExperiment(user_id, dataset_id):
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

        # price, description, multiSelect=None
        session = dbConn().get_session(dbConn().get_engine())
        user = session.query(models.User).filter(models.User.id == user_id).first()
        
        if(user is None):
            ret['errors'] = []
            ret['errors'].append("Invalid User")
            return apiDecorate(ret, 400, "Invalid User")
        
        dataset = session.query(models.dataset).filter(models.dataset.id == dataset_id).first()
        
        if(dataset is None):
            ret['errors'] = []
            ret['errors'].append("Invalid dataset")
            return apiDecorate(ret, 400, "Invalid dataset")
        price = argArray.get('price')
        batchSize = argArray.get('batchSize')
        description = argArray.get('description')
        multiSelect = argArray.get('multiSelect')
        datasetType = argArray.get('datasetType')

        if(multiSelect is None):
            multiSelect = 1

        if((price is None or len(price) <=0) or (batchSize is None or len(batchSize) <=0) or (description is None or len(description) <=0) or (datasetType is None or len(datasetType) <=0)):
            ret['errors'] = []
            ret['errors'].append("Parameters not set")
            return apiDecorate(ret, 400, "Parameters not set")
        try:
            batchSize = int(batchSize)
            price = float(price)
        except:
            ret['errors'] = []
            ret['errors'].append("price/batchSize not integer")
            return apiDecorate(ret, 400, "price/batchSize not integer")

        if(price < 0):
            ret['errors'] = []
            ret['errors'].append("Price less than 0")
            return apiDecorate(ret, 400, "Price less than 0")
        randNum = randint(1,10000)
        randNum2 = randint(1,10000)
        randString = ''.join(random.choice('0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ') for i in range(randint(10,20)))
        timeStamp = datetime.now()
        randName= str(randNum) + str(timeStamp.year) + str(timeStamp.month) + randString + str(timeStamp.day) + str(timeStamp.hour) + str(timeStamp.minute) + str(timeStamp.second) + str(randNum2)

        if(dataset.isMedia == 1):
            batches = datasetHandler.makeMediaBatches(dataset,batchSize)
            if(batches is None):
                ret['errors'] = []
                ret['errors'].append("Batch problems")
                return apiDecorate(ret, 400, "Batch problems")
            experiment = models.experiments(user.id, randName, price, len(batches), description)
            session.add(experiment)
            session.commit()
            botoConn = boto.connect_s3(datasetHandler.DREAM_key, datasetHandler.DREAM_secretKey, host="objects-us-west-1.dream.io")
            bucket = botoConn.get_bucket(datasetHandler.DREAM_Bucket, validate=False)
            batchCount = 0
            for batch in batches:
                batchJson  = json.dumps(batch)
                k = Key(bucket)
                k.key = "e_"+randName+"/"+str(batchCount)+".json"
                sent = k.set_contents_from_string(batchJson, cb=None, md5=None, reduced_redundancy=False)
                batch = models.batch(randName, batchCount)
                session.add(batch)
                session.commit()
                batchCount+=1 
            print "Here"
        print "Processing Batches"
        return "Success"
