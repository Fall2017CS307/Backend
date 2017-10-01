import sys
sys.path.append("..")

import MySQLdb
import os
import db

def test_db_config():

	try:	
		engine = db.dbConn().get_engine()
	except:
		assert False, "Database environmental variable not set"

def test_table_creation():
	engine = db.dbConn().get_engine()
	tables = db.Base.metadata.tables.keys()
	try:
		for table in tables:
			if not engine.dialect.has_table(engine, table):
				assert False, "Database tables not created"
	except:
		assert False, "Check previous test cases!"

