from flask import request
import MySQLdb
from utils import dbConn

class userHandler():
    def login(self):
        username = request.args.get("username")
        if not username:
            username = "world!" 
        return "hello "+username

    