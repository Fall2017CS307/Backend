from flask import Flask, request
import MySQLdb
from utils import dbConn
from userHandler import userHandler
from fileHandler import fileHandler
app = Flask(__name__)

app.add_url_rule('/api/login', 'api/login',userHandler().login, methods=['GET', 'POST'])
app.add_url_rule('/api/register', 'api/register',userHandler().register, methods=['GET', 'POST'])
app.add_url_rule('/api/verify/email/<string:key>', '/api/verify/email', userHandler().verify_email, methods=['GET', 'POST'])
app.add_url_rule('/api/verify/phone/<string:key>', '/api/verify/phone', userHandler().verify_phone, methods=['GET', 'POST'])
app.add_url_rule('/api/<int:user_id>/upload', '/api/user_id/upload', fileHandler.uploadFile, methods=['POST'])
app.add_url_rule('/api/<int:user_id>/datasets', '/api/user_id/datasets', userHandler().getDatasets, methods=['POST', 'GET'])

if __name__ == '__main__':
    app.run(debug=True)
