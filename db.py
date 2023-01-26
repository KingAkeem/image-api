import os
import sqlite3

from flask import g
from datetime import datetime, timezone


"""
Initialize database and setup tables
"""
def init(app):
	with app.app_context():
		setup_tables() # nothing happens if they exist

"""
Get database connection
"""
def get_connection(db_directory = "database", db_name = "scans"):
	conn = getattr(g, '_database', None)
	if conn is None:
		# attempt to create db_directory for the database file if it doesn't exist
		if not os.path.exists(db_directory):
			os.makedirs(db_directory)

		db_url = os.path.join(db_directory, db_name) # construct complete path to DB file
		conn = g._database = sqlite3.connect(db_url) # store connection for later use
	
	return conn


def setup_tables():
	conn = get_connection()
	cur = conn.cursor()
	cur.execute("""
		CREATE TABLE IF NOT EXISTS request_tracker(
			id,
			created_date,
			created_user,
			status
		)
	""")

	cur.execute("""
		CREATE TABLE IF NOT EXISTS scan(
			id,
			created_date,
			created_user,
			text,
			type
		)
	""")
	conn.commit()

def timestamp():
	return datetime.now(timezone.utc).isoformat()

def insert_request(request):
	conn = get_connection()
	cur = conn.cursor()
	# auto-generate ID
	# use current time for created date
	# user and status are only required fields
	cur.execute(f'''INSERT INTO request_tracker (
		id, 
		created_date,
		created_user,
		status
	) VALUES (?, ?, ?,?);''', ("abc", timestamp(), request["created_user"], request["status"]))
	conn.commit()

def insert_scan(scan):
	conn = get_connection()
	cur = conn.cursor()
	# auto-generate ID
	# all other fields required
	cur.execute(f"""INSERT INTO scan (
		id, 
		type,
		created_date,
		created_user,
		text
	) VALUES (?, ?, ?, ?, ?)""", ("something", scan["type"], scan["created_date"], scan["created_user"], scan["text"]))
	conn.commit()
