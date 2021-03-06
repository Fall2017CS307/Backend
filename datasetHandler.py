import os
import random
from flask import request, redirect, url_for
import MySQLdb
from jsonReturn import apiDecorate
import models
from utils.dbConn import dbConn
from datetime import datetime, timedelta
#import datetime
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
from utils.notification import notification
import base64
from sqlalchemy import desc

class datasetHandler:
    DREAM_username = os.environ.get('dream_user') or "none"
    DREAM_secretKey = os.environ.get('dream_secretKey') or "none"
    DREAM_Bucket = os.environ.get('dream_bucket') or "none"
    DREAM_auth = os.environ.get('dream_auth') or "none"
    DREAM_key = os.environ.get('dream_key') or "none"

    @staticmethod
    def getBatch(batch_id):
        ret = {}
        session = dbConn().get_session(dbConn().get_engine())
        batch = session.query(models.batch).filter(models.batch.id==batch_id).first()
        if(batch is None):
            ret['errors'] = []
            ret['errors'].append("Invalid batch id")
            return apiDecorate(ret, 400, "Invalid batch id")
        experiment = session.query(models.experiments).filter(models.experiments.resource_id==batch.experiment_id).first()
        dataset = session.query(models.dataset).filter(models.dataset.id==experiment.dataset_id).first()
        #k.key = "e_"+randName+"/"+str(batchCount)+".json"
        botoConn = boto.connect_s3(datasetHandler.DREAM_key, datasetHandler.DREAM_secretKey, host="objects-us-west-1.dream.io")
        bucket = botoConn.get_bucket(datasetHandler.DREAM_Bucket, validate=False)
        k = Key(bucket)
        k.key = "e_"+batch.experiment_id+"/"+str(batch.local_resource_id)+".json"
        fileJson = k.get_contents_as_string()
        fileArr = json.loads(fileJson)
        ret['description']  = experiment.description
        if(dataset.isMedia == 1):
            filesArr = []
            for item in fileArr:
                itemKey =  dataset.resource_id + "/" + str(item)
                itemK = Key(bucket)
                itemK.key = itemKey
                fileEntry = {}
                fileEntry['name'] = item
                fileEntry['link'] = itemK.generate_url(3600, query_auth=True, force_http=True)
                filesArr.append(fileEntry)
            ret['files'] = filesArr
        else:
            ret['data'] = fileArr
        ret['count'] = batch.curAnnotation
        return apiDecorate(ret, 200, "Success")
        #print k.generate_url(3600, query_auth=True, force_http=True)
        return fileJson
        #print fileJson

    @staticmethod
    def makeBatches(dataset, batchSize):
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
    def getExperiments(user_id):
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
        sort = argArray.get("sort")
        levelFilter = argArray.get("education")
        if(levelFilter is not None and len(str(levelFilter)) < 0):
            levelFilter = None
        if(levelFilter is not None):
            try:
                levelFilter = int(levelFilter)
            except:
                levelFilter = None
        session = dbConn().get_session(dbConn().get_engine())
        user = session.query(models.User).filter(models.User.id == user_id).first()
        if(user is None):
            ret['errors'] = []
            ret['errors'].append("Invalid User")
            return apiDecorate(ret, 400, "Invalid User")

        ret = {}
        if(sort == "compensation"):
            batches = session.query(models.batch.experiment_id).filter(models.batch.user_id==None).order_by(models.batch.price).group_by(models.batch.price).group_by(models.batch.experiment_id).all()
        if(sort == "time"):
             batches = session.query(models.batch.experiment_id).filter(models.batch.user_id==None).order_by(models.batch.allocateTime).group_by(models.batch.allocateTime).group_by(models.batch.experiment_id).all()
             
        else:
            batches = session.query(models.batch.experiment_id).filter(models.batch.user_id==None).distinct(models.batch.experiment_id).all()
        experiments = []
        for batch in batches:
            experiment = session.query(models.experiments).filter(models.experiments.resource_id==batch[0]).first()
            if((experiment.gender != None and experiment.gender != user.gender) or (experiment.country != None and experiment.country!=user.country) or (user.skill < experiment.skill) or (levelFilter is not None and experiment.skill != levelFilter) or(experiment.isPaused != 0)):
                print "User skill " + str(user.skill) + "experiment.skill " + str(experiment.skill) + "\n"
                continue
            datas = session.query(models.dataset).filter(models.dataset.id == experiment.dataset_id).first()
            tempExperiment = {}
            tempExperiment['id'] = experiment.id
            tempExperiment['price'] = experiment.price
            tempExperiment['description'] = experiment.description
            tempExperiment['isMedia'] = datas.isMedia
            tempExperiment['allocate'] = experiment.allocateTime or 0
            experiments.append(tempExperiment)

        ret['experiments'] = experiments
        return apiDecorate(ret,200,"Success")

    @staticmethod
    def batchList(user_id):
        ret = {}
        session = dbConn().get_session(dbConn().get_engine())
        user = session.query(models.User).filter(models.User.id == user_id).first()
        if(user is None):
            ret['errors'] = []
            ret['errors'].append("Invalid User")
            return apiDecorate(ret, 400, "Invalid User")
        batches = session.query(models.batch).filter(models.batch.user_id == user.id).filter(models.batch.isCompleted==False).all()
        userBatches = []
        for batch in batches:
            userBatch = {}
            userBatch['id'] = batch.id
            experiment = session.query(models.experiments).filter(models.experiments.resource_id == batch.experiment_id).first()
            if(experiment.isPaused != 0):
                continue
            datas = session.query(models.dataset).filter(models.dataset.id == experiment.dataset_id).first()
            userBatch['description'] = experiment.description
            userBatch['price'] = experiment.price
            userBatch['isMedia'] = datas.isMedia
            if(batch.deadline != None):
                userBatch['due'] = str(batch.deadline)
            else:
                 userBatch['due'] = "No Deadline"
            userBatches.append(userBatch)
        ret['batches'] = userBatches
        return apiDecorate(ret, 200, "Success")

    @staticmethod
    def assignBatch(user_id, experiment_id):
        ret = {}
        session = dbConn().get_session(dbConn().get_engine())
        user = session.query(models.User).filter(models.User.id == user_id).first()
        if(user is None):
            ret['errors'] = []
            ret['errors'].append("Invalid User")
            return apiDecorate(ret, 400, "Invalid User")

        experiment = session.query(models.experiments).filter(models.experiments.id == experiment_id).first()
        if(experiment is None):
            ret['errors'] = []
            ret['errors'].append("Invalid experiment")
            return apiDecorate(ret, 400, "Invalid experiment")

        hasBatch = session.query(models.batch).filter(models.batch.experiment_id == experiment.resource_id).filter(models.batch.user_id == user.id).first()
        if(hasBatch is not None):
            #ret['errors'] = []
            #ret['errors'].append("User already has a batch")

            ret['batch_id'] = hasBatch.id
            return apiDecorate(ret, 200, "Success")

        batch = session.query(models.batch).filter(models.batch.experiment_id == experiment.resource_id).filter(models.batch.user_id==None).first()
        if(batch is None):
            ret['errors'] = []
            ret['errors'].append("No batch available")
            return apiDecorate(ret, 400, "No batch available")

        batch.user_id = user.id
        ret['batch_id'] = batch.id
        if(experiment.maxTime != None):
            batch.deadline = datetime.now() + timedelta(hours=experiment.maxTime)
            if(experiment.notifTime != None):
                batch.notifDeadline = datetime.now() + timedelta(hours=(experiment.maxTime - experiment.notifTime))
        session.commit()
        return apiDecorate(ret, 200, "Success")

    @staticmethod
    def createExperiment(user_id):
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

        dataset_id = argArray.get("dataset_id")
        if(dataset_id is None):
            ret['errors'] = []
            ret['errors'].append("Invalid dataset")
            return apiDecorate(ret, 400, "Invalid dataset")
        try:
            dataset_id = int(dataset_id)
        except:
            ret['errors'] = []
            ret['errors'].append("Invalid dataset")
            return apiDecorate(ret, 400, "Invalid dataset")

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
        gender = argArray.get("gender")
        country = argArray.get("country")
        skill = argArray.get("skill")
        '''dt = argArray.get("deadline")'''
        maxTime = argArray.get("maxTime")
        notifTime = argArray.get("notifTime")
        allocateTime = argArray.get("allocateTime")
        title = argArray.get("title")

        if(maxTime is not None):
            try:
                if len(maxTime) == 0 or maxTime == 0:
                    maxTime = None
                else:
                    maxTime = int(maxTime)
            except:
                return apiDecorate(ret, 400, "Max time is not integer")

        if(notifTime is not None):
            try:
                if len(notifTime) == 0 or maxTime == 0:
                    notifTime = None
                else:
                    notifTime = int(notifTime)
            except:
                return apiDecorate(ret, 400, "Notification time is not integer")

        if(allocateTime is not None):
            try:
                if len(allocateTime) == 0 or maxTime == 0:
                    allocateTime = None
                else:
                    allocateTime = int(allocateTime)
            except:
                return apiDecorate(ret, 400, "Allocate time is not integer")


        if(notifTime is not None and maxTime is None):
            return apiDecorate(ret, 400, "Allocation time needs to be specified if, notification time is specified")

        if(notifTime is not None):
            if notifTime < 0 or notifTime > maxTime:
                return apiDecorate(ret, 400, "Notification time incorrect")
        '''
        if(dt is not None):
            #deadline = datetime.datetime.strptime(dt, '%Y/%m/%d')
            deadline = datetime.strptime(dt, '%Y/%m/%d')
        else:
            deadline = None
        '''

        if(gender is not None and len(gender) <1):
            gender = None
        if(country is not None and len(country) < 1):
            country = None
        if(skill is not None and len(skill) < 1):
            skill = 0
        else:
            try:
                skill = int(skill)
            except:
                skill = 0
        if(multiSelect is None):
            multiSelect = 1

        if((price is None or len(price) <=0) or (batchSize is None or len(batchSize) <=0) or (description is None or len(description) <=0) or (datasetType is None or len(datasetType) <=0) or (title is None or len(title) == 0) ):
            ret['errors'] = []
            ret['errors'].append("Parameters not set")
            return apiDecorate(ret, 400, "Parameters not set")
        try:
            batchSize = int(batchSize)
            price = float(price)
            datasetType = int(datasetType)
        except:
            ret['errors'] = []
            ret['errors'].append("price/batchSize not integer")
            return apiDecorate(ret, 400, "price/batchSize not integer")
        if(price < 0):
            ret['errors'] = []
            ret['errors'].append("Price less than 0")
            return apiDecorate(ret, 400, "Price less than 0")
        totalCost = batchSize*price
        if(user.balance < totalCost):
            ret['errors'] = []
            ret['errors'].append("Insufficient funds")
            return apiDecorate(ret, 400, "Insufficient funds")
        else:
             user.balance-= totalCost
        session.commit()
        randNum = randint(1,10000)
        randNum2 = randint(1,10000)
        randString = ''.join(random.choice('0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ') for i in range(randint(10,20)))
        timeStamp = datetime.now()
        randName= str(randNum) + str(timeStamp.year) + str(timeStamp.month) + randString + str(timeStamp.day) + str(timeStamp.hour) + str(timeStamp.minute) + str(timeStamp.second) + str(randNum2)

        if(int(dataset.isMedia) != int(datasetType)):
            print int(dataset.isMedia)
            print datasetType
            ret['errors'] = []
            ret['errors'].append("Invalid dataset type and experiment type")
            return apiDecorate(ret, 400, "Invalid dataset type and experiment type")

        batches = datasetHandler.makeBatches(dataset,batchSize)
        if(batches is None):
            ret['errors'] = []
            ret['errors'].append("Batch problems")
            return apiDecorate(ret, 400, "Batch problems")
        experiment = models.experiments(user.id,title, randName, price, len(batches), description, dataset.id, gender, country, skill,maxTime,notifTime,allocateTime )
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
            batch = models.batch(randName, batchCount, len(batch))
            batch.allocateTime  = allocateTime or 0
            batch.price = price
            session.add(batch)
            session.commit()
            batchCount+=1
        
        k = Key(bucket)
        k.key = "e_"+randName+"/res.json"
        arr = []
        sent = k.set_contents_from_string(json.dumps(arr), cb=None, md5=None, reduced_redundancy=False)
        return apiDecorate(ret, 200, "Success")

    @staticmethod
    def userBatchExtracter(batch_id):

        session = dbConn().get_session(dbConn().get_engine())


        curBatch = session.query(models.batch).filter(models.batch.id == batch_id).first()
        curBatch.isCompleted= True

        curExp = session.query(models.experiments).filter(models.experiment.resource_id == curBatch.experiment_id)
        price = curExp.price
        curUser = session.query(models.User).filter(models.User.id == curBatch.user_id)

        curUser.balance = curUser.balance + price

        session.commit()


    @staticmethod
    def rateBatch(batch_id, rating):
        ret = {}
        session = dbConn().get_session(dbConn().get_engine())
        curBatch = session.query(models.batch).filter(models.batch.id == batch_id).first()
        if(curBatch is None):
            ret['errors'] = []
            ret['errors'].append("Invalid batch")
            return apiDecorate(ret, 400, "Invalid batch")
        if(curBatch.isCompleted == False):
            ret['errors'] = []
            ret['errors'].append("Batch not annotated")
            return apiDecorate(ret, 400, "Batch not annotated")

        if(curBatch.rating is not None):
            ret['errors'] = []
            ret['errors'].append("Batch already has rating")
            return apiDecorate(ret, 400, "Batch already has rating")

        if(rating > 5):
            rating = 5
        elif(rating < 0):
            rating = 0
        curBatch.rating = rating
        session.commit()
        return apiDecorate(ret, 200, "success")
    
    @staticmethod
    def getBatchToRate(experiment_id):
        ret = {}
        session = dbConn().get_session(dbConn().get_engine())
        experiment = session.query(models.experiments).filter(models.experiments.id == experiment_id).first()
        if experiment is None:
            ret['errors'] = []
            ret['errors'].append("Invalid experiment id")
            return apiDecorate(ret, 400, "Invalid experiment id")
        batches = session.query(models.batch).filter(models.batch.experiment_id == experiment.resource_id).filter(models.batch.rating == None).all()
        finishedBatch = []

        for batch in batches:
            if(batch.isCompleted == False):
                continue
            botoConn = boto.connect_s3(datasetHandler.DREAM_key, datasetHandler.DREAM_secretKey, host="objects-us-west-1.dream.io")
            bucket = botoConn.get_bucket(datasetHandler.DREAM_Bucket, validate=False)
            curBatch = {}
            curBatch['id'] = batch.id
            link = "e_"+experiment.resource_id+"/"+str(batch.local_resource_id)+"_res.json"
            itemk = Key(bucket)
            itemk.key = link
            print link
            link = itemk.generate_url(3600, query_auth=True, force_http=True)
            curBatch['link'] = link
            print link
            finishedBatch.append(curBatch)
        ret['batches'] = finishedBatch
        return apiDecorate(ret, 200, "success")
        
    @staticmethod
    def getPastExperiments(user_id):
        ret = {}
        session = dbConn().get_session(dbConn().get_engine())
        myBatches = session.query(models.batch).filter(models.batch.user_id == user_id)
        batches = myBatches.all()
        listBatch = []
        for curBatch in batches:
            exp = session.query(models.experiments).filter(models.experiments.resource_id == curBatch.experiment_id).first()
            batchData = {}
            batchData['description'] = exp.description
            if(curBatch.rating is None):
                batchData['rating'] = -1
            else:
                batchData['rating'] = curBatch.rating
            listBatch.append(batchData)
        ret['batches'] = listBatch
        return apiDecorate(ret, 200, 'success')
        
    @staticmethod
    def submitBatchRowImage(batch_id):
        ret = {}
        if request.method == "GET":
            argArray = request.args

        elif request.method  == "POST":
            if(len(request.form) > 0):
                argArray = request.form
            else:
                print request.get_data()
                argArray = json.loads(request.data)

        imageText = argArray.get('imageText') or ""
        imageData = argArray.get('imageData') or ""
        if(len(imageText) == 0 or len(imageData) == 0 ):
            return apiDecorate(ret,400,"Image data/text not present")
        session = dbConn().get_session(dbConn().get_engine())

        curBatch = session.query(models.batch).filter(models.batch.id == batch_id).first()
        if(curBatch is None):
            return apiDecorate(ret, 400, 'Invalid batch id')
        curExperiment = session.query(models.experiments).filter(models.experiments.resource_id == curBatch.experiment_id).first()
        curDataset = session.query(models.dataset).filter(models.dataset.id == curExperiment.dataset_id).first()
        if(curDataset.isMedia == False):
            return apiDecorate(ret,400,"Invalid submission route called")
        if(curBatch.isCompleted == True):
            print "eee"
            return apiDecorate(ret,400,"Batch finished annotating")
        batchData = {}
        batchData['text'] = imageText
        batchData['data'] = imageData
        
        botoConn = boto.connect_s3(datasetHandler.DREAM_key, datasetHandler.DREAM_secretKey, host="objects-us-west-1.dream.io")
        fileApp = "e_"+curExperiment.resource_id+"/"+str(curBatch.local_resource_id)+"_"+str(curBatch.curAnnotation)
        bucket = botoConn.get_bucket(datasetHandler.DREAM_Bucket, validate=False)
        k = Key(bucket)
        k.key = fileApp+".json"
        print "key "+k.key
        sent = k.set_contents_from_string(json.dumps(batchData), cb=None, md5=None, reduced_redundancy=False)
        if((curBatch.curAnnotation +1) >= curBatch.totalAnnotation):
            curBatch.isCompleted = True
        curBatch.curAnnotation +=1
        session.commit()
        session = dbConn().get_session(dbConn().get_engine())
        curBatch = session.query(models.batch).filter(models.batch.id == batch_id).first()
        if(curBatch.isCompleted == True):
            datasetHandler.makeBatchData(batch_id)
        return apiDecorate(ret, 200, "Success")
        
    @staticmethod
    def submitBatchRowText(batch_id):
        ret = {}
        if request.method == "GET":
            argArray = request.args

        elif request.method  == "POST":
            if(len(request.form) > 0):
                argArray = request.form
            else:
                print request.get_data()
                argArray = json.loads(request.data)

        responseText = argArray.get('response') or ""
        if(len(responseText) == 0):
            return apiDecorate(ret,400,"responseText not present")
        session = dbConn().get_session(dbConn().get_engine())

        curBatch = session.query(models.batch).filter(models.batch.id == batch_id).first()
        if(curBatch is None):
            return apiDecorate(ret, 400, 'Invalid batch id')
        curExperiment = session.query(models.experiments).filter(models.experiments.resource_id == curBatch.experiment_id).first()
        curDataset = session.query(models.dataset).filter(models.dataset.id == curExperiment.dataset_id).first()
        if(curDataset.isMedia == True):
            return apiDecorate(ret,400,"Invalid submission route called")
        if(curBatch.isCompleted == True):
            return apiDecorate(ret,400,"Batch finished annotating")
        batchData = {}
        batchData['text'] = responseText

        botoConn = boto.connect_s3(datasetHandler.DREAM_key, datasetHandler.DREAM_secretKey, host="objects-us-west-1.dream.io")
        fileApp = "e_"+curExperiment.resource_id+"/"+str(curBatch.local_resource_id)+"_"+str(curBatch.curAnnotation)
        bucket = botoConn.get_bucket(datasetHandler.DREAM_Bucket, validate=False)
        k = Key(bucket)
        k.key = fileApp+".json"
        print "key "+k.key
        sent = k.set_contents_from_string(json.dumps(batchData), cb=None, md5=None, reduced_redundancy=False)
        if((curBatch.curAnnotation +1) >= curBatch.totalAnnotation):
            curBatch.isCompleted = True
        curBatch.curAnnotation +=1
        session.commit()
        session = dbConn().get_session(dbConn().get_engine())
        curBatch = session.query(models.batch).filter(models.batch.id == batch_id).first()
        if(curBatch.isCompleted == True):
            datasetHandler.makeBatchData(batch_id)
        return apiDecorate(ret, 200, "Success")


    @staticmethod
    def getExperimentProgress(user_id):
        ret = {}
        session = dbConn().get_session(dbConn().get_engine())
        experiments = session.query(models.experiments).filter(models.experiments.user_id == user_id).all()
        if(experiments is None):
            return apiDecorate(ret, 400,"Invalid id")
        ret['experiments'] = []
        for experiment in experiments:
            totalAnnotateCount = 0
            curAnnotateCount = 0
            print(experiment.resource_id)
            batches = session.query(models.batch).filter(models.batch.experiment_id == experiment.resource_id).all()
            
            botoConn = boto.connect_s3(datasetHandler.DREAM_key, datasetHandler.DREAM_secretKey, host="objects-us-west-1.dream.io")
            bucket = botoConn.get_bucket(datasetHandler.DREAM_Bucket, validate=False)
            dataArr = []
            for batch in batches :
                if(batch.isCompleted == True):
                    fileName = "e_"+experiment.resource_id+"/"+str(batch.local_resource_id)+"_res.json"
                    k = Key(bucket)
                    k.key = fileName
                    fileJson = k.get_contents_as_string()
                    fileArr = json.loads(fileJson)
                    dataArr.append(fileArr)
                    
                totalAnnotateCount += batch.totalAnnotation
                curAnnotateCount += batch.curAnnotation
            fileApp = "e_"+experiment.resource_id+"/"+"res.json"
            k = Key(bucket)
            k.key = fileApp
            print "key "+k.key
            sent = k.set_contents_from_string(json.dumps(dataArr), cb=None, md5=None, reduced_redundancy=False)
            
            curExp = {}
            curExp['total'] = totalAnnotateCount
            curExp['completed'] = curAnnotateCount
            curExp['experiment_id'] = experiment.id
            curExp['price'] = experiment.price
            curExp['description'] = experiment.description
            curExp['link'] = k.generate_url(3600, query_auth=True, force_http=True)
            if(experiment.isPaused != 0):
                curExp['status'] = "Paused"
            else:
                curExp['status'] = "Resumed"
            
            ret['experiments'].append(curExp)

        return apiDecorate(ret, 200, "Success")
        
    @staticmethod
    def getExperimentDetails(experiment_id):
        ret = {}
        session = dbConn().get_session(dbConn().get_engine())
        experiment = session.query(models.experiments).filter(models.experiments.id == experiment_id).first()
        if experiment is None:
            ret['errors'] = []
            ret['errors'].append("Invalid experiment id")
            return apiDecorate(ret,400,ret['errors'][0])
        
        ret['id'] = experiment_id
        ret['description'] = experiment.description
        ret['notifTime'] = experiment.notifTime
        ret['allocateTime'] = experiment.allocateTime
        ret['maxTime'] = experiment.maxTime
        return apiDecorate(ret, 200, "success")
        
    @staticmethod
    def updateExperiment(experiment_id):
        ret = {}
        session = dbConn().get_session(dbConn().get_engine())
        experiment = session.query(models.experiments).filter(models.experiments.id == experiment_id).first()
        if experiment is None:
            ret['errors'] = []
            ret['errors'].append("Invalid experiment id")
            return apiDecorate(ret,400,ret['errors'][0])
        argArray = {}
        if request.method == "GET":
            argArray = request.args

        elif request.method  == "POST":
            if(len(request.form) > 0):
                argArray = request.form
            else:
                print request.get_data()
                argArray = json.loads(request.data)
        
        description = argArray.get("description")
        notifTime = argArray.get("notifTime")
        allocateTime = argArray.get("allocateTime")
        maxTime = argArray.get("maxTime")
        if(description == None or len(description) == 0):
            return apiDecorate(ret, 400, "Description cant be empty")
            
        if(maxTime is not None):
            try:
                if len(maxTime) == 0 or maxTime == 0:
                    maxTime = None
                else:
                    maxTime = int(maxTime)
            except:
                return apiDecorate(ret, 400, "Max time is not integer")

        if(notifTime is not None):
            try:
                if len(notifTime) == 0 or maxTime == 0:
                    notifTime = None
                else:
                    notifTime = int(notifTime)
            except:
                return apiDecorate(ret, 400, "Notification time is not integer")

        if(allocateTime is not None):
            try:
                if len(allocateTime) == 0 or maxTime == 0:
                    allocateTime = None
                else:
                    allocateTime = int(allocateTime)
            except:
                return apiDecorate(ret, 400, "Allocate time is not integer")


        if(notifTime is not None and max is None):
            return apiDecorate(ret, 400, "Allocation time needs to be specified if, notification time is specified")

        if(notifTime is not None):
            if notifTime < 0 or notifTime > maxTime:
                return apiDecorate(ret, 400, "Notification time incorrect")
        
        content = "Experiment (" + experiment.title + "), has been changed." + "\n New instruction are  : " + description
        experiment.description = description
        experiment.notifTime = notifTime
        experiment.allocateTime = allocateTime
        experiment.maxTime = maxTime
        session.commit()
        session = dbConn().get_session(dbConn().get_engine())
        
        batches = session.query(models.batch).filter(models.batch.user_id != None).filter(models.batch.experiment_id == experiment.resource_id).all()
        if(len(batches) < 1):
            return apiDecorate(ret, 200, "Success")
        for batch in batches:
            user = session.query(models.User).filter(models.User.id == batch.user_id).first()
            notification.sendMail("anirudhchellani@gmail.com", user.email, "Experiment changed", "text/plain", content)
            notification.sendText(user.phone, content)
        return apiDecorate(ret, 200, "Success")
    
    @staticmethod
    def notifyTime():
        session = dbConn().get_session(dbConn().get_engine())
        curTime = datetime.now()
        batches = session.query(models.batch).filter(models.batch.notifDeadline!=None).filter(models.batch.notifDeadline < curTime).all()
        if(len(batches) < 1):
            return "No Batch"
        else:
            print batches
            str = ""
            for batch in batches:
                experiment = session.query(models.experiments).filter(models.experiments.resource_id == batch.experiment_id).first()
                user = session.query(models.User).filter(models.User.id == batch.user_id).first()
                content = "Experiment - " + experiment.title + " -  due soon. Please complete"
                notification.sendMail("anirudhchellani@gmail.com", user.email, "Experiment due", "text/plain", content)
                notification.sendText(user.phone, "some content")
            return str
    
    @staticmethod
    def toggleExperiment(experiment_id):
        ret = {}
        session = dbConn().get_session(dbConn().get_engine())
        experiment = session.query(models.experiments).filter(models.experiments.id == experiment_id).first()
        if(experiment is None):
            ret['errors'] = []
            ret['errors'].append("Invalid experiment id")
            return apiDecorate(ret,400,ret['errors'][0])
        if(experiment.isPaused == 0):
            experiment.isPaused = 1
        else:
            experiment.isPaused = 0
        session.commit()
        return apiDecorate(ret,200,"success")

    @staticmethod
    def makeBatchData(batch_id):
        ret = {}
        session = dbConn().get_session(dbConn().get_engine())

        curBatch = session.query(models.batch).filter(models.batch.id == batch_id).first()
        curExp = session.query(models.experiments).filter(models.experiments.resource_id == curBatch.experiment_id).first()
        price = curExp.price
        curUser = session.query(models.User).filter(models.User.id == curBatch.user_id).first()
        if(curUser is None):
            return apiDecorate(ret, 400, "Not right user")
            
        curUser.balance = curUser.balance + price
        session.commit()
        
        session = dbConn().get_session(dbConn().get_engine())
    
        curBatch = session.query(models.batch).filter(models.batch.id == batch_id).first()
        curExperiment = session.query(models.experiments).filter(models.experiments.resource_id == curBatch.experiment_id).first()
        batches = session.query(models.batch).filter(models.batch.experiment_id == curBatch.experiment_id).order_by(models.batch.local_resource_id).all()
        botoConn = boto.connect_s3(datasetHandler.DREAM_key, datasetHandler.DREAM_secretKey, host="objects-us-west-1.dream.io")
        bucket = botoConn.get_bucket(datasetHandler.DREAM_Bucket, validate=False)
        dataArr = []
        for i in range(0,curBatch.totalAnnotation):
            k = Key(bucket)
            fileApp = "e_"+curExperiment.resource_id+"/"+str(curBatch.local_resource_id)+"_"+str(i)+".json"
            k.key = fileApp
            fileJson = k.get_contents_as_string()
            fileArr = json.loads(fileJson)
            dataArr.append(fileArr)
            
        fileApp = "e_"+curExperiment.resource_id+"/"+str(curBatch.local_resource_id)+"_res"
        k = Key(bucket)
        k.key = fileApp+".json"
        print "key "+k.key
        sent = k.set_contents_from_string(json.dumps(dataArr), cb=None, md5=None, reduced_redundancy=False)
        