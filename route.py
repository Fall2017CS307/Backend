from flask import Flask, request
import MySQLdb
from utils import dbConn
from userHandler import userHandler

app = Flask(__name__)

app.add_url_rule('/api/login', 'api/login',userHandler().login, methods=['GET', 'POST'])

if __name__ == '__main__':
    app.run(debug=True)