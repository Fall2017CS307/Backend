import MySQLdb
import os

def test_db_config():
	sqlHost=os.environ.get('datonate_sql') or "none"
	sqlUser=os.environ.get('datonate_sqlUser') or "none"
	sqlPass=os.environ.get('datonate_sqlPass') or "none"
	sqlDB=os.environ.get('datonate_sqldb') or "none"
	

	try:	
		db = MySQLdb.connect(host=sqlHost, user=sqlUser, passwd=sqlPass, db=sqlDB)
		db.cursor()	
	except:
		assert(False)

