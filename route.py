from flask import Flask, request
import MySQLdb
from utils import dbConn
from userHandler import userHandler
from fileHandler import fileHandler
from datasetHandler import datasetHandler
app = Flask(__name__)

app.add_url_rule('/api/login', 'api/login',userHandler().login, methods=['GET', 'POST'])
app.add_url_rule('/api/register', 'api/register',userHandler().register, methods=['GET', 'POST'])
app.add_url_rule('/api/verify/email/<string:key>', '/api/verify/email', userHandler().verify_email, methods=['GET', 'POST'])
app.add_url_rule('/api/verify/phone/<string:key>', '/api/verify/phone', userHandler().verify_phone, methods=['GET', 'POST'])
app.add_url_rule('/api/<int:user_id>/upload/<int:datasetType>', '/api/user_id/upload', fileHandler.uploadFile, methods=['POST'])
app.add_url_rule('/api/<int:user_id>/datasets', '/api/user_id/datasets', userHandler().getDatasets, methods=['POST', 'GET'])

#app.add_url_rule('api/charge','api/charge', paymentHandler().charge, methods=['POST'])

#^THIS MIGHT REQUIRE SOME MODIFICATION

#'/api/<int:user_id>/datasets', '/api/user_id/datasets',

app.add_url_rule('/api/<int:user_id>/dataset/delete/<int:dataset_id>/', '/api/user_id/dataset/delete/dataset_id', userHandler().deleteDataset, methods=['POST', 'GET'])
app.add_url_rule('/api/<int:user_id>/dataset/public/<int:dataset_id>/', '/api/user_id/dataset/public/dataset_id', userHandler().makeDatasetPublic, methods=['POST', 'GET'])
app.add_url_rule('/api/<int:user_id>/dataset/private/<int:dataset_id>/', '/api/user_id/dataset/private/dataset_id', userHandler().makeDatasetPrivate, methods=['POST', 'GET'])
app.add_url_rule('/api/datasets/public', '/api/datasets/public', userHandler().getPublicDatasets, methods=['POST', 'GET'])
app.add_url_rule('/api/<int:user_id>/dataset/copy/<int:dataset_id>/', '/api/user_id/dataset/copy/private/dataset_id', userHandler().copyPublicDataset, methods=['POST', 'GET'])

#Create Experiments
app.add_url_rule('/api/<int:user_id>/create/<int:dataset_id>/', '/api/user_id/create/dataset_id', datasetHandler.createExperiment, methods=['POST', 'GET'])
app.add_url_rule('/api/getExperiments', '/api/getExperiments', datasetHandler.getExperiments, methods=['POST', 'GET'])

app.add_url_rule('/api/<int:user_id>/assign/<int:experiment_id>','/api/user_id/assign/experiment_id', datasetHandler.assignBatch, methods=['POST', 'GET'])
app.add_url_rule('/api/<int:user_id>/batchList','/api/user_id/batchList', datasetHandler.batchList, methods=['POST', 'GET'])
app.add_url_rule('/api/<int:batch_id>/getBatch','/api/batch_id/getBatch', datasetHandler.getBatch, methods=['POST', 'GET'])
if __name__ == '__main__':
    app.run(debug=True)
