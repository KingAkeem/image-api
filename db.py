import os
import sqlite3
import uuid

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
		CREATE TABLE IF NOT EXISTS status_tracker(
			id,
			created_date,
			created_user,
			message,
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

def id():
	return str(uuid.uuid4())

def insert_status(status):
	conn = get_connection()
	cur = conn.cursor()
	cur.execute(f'''INSERT INTO status_tracker (
		id, 
		created_date,
		created_user,
		message,
		status
	) VALUES (?,?,?,?,?);''', (id(), timestamp(), status["created_user"], status["message"], status["status"]))
	conn.commit()

def insert_scan(scan):
	conn = get_connection()
	cur = conn.cursor()
	cur.execute(f"""INSERT INTO scan (
		id, 
		type,
		created_date,
		created_user,
		text
	) VALUES (?, ?, ?, ?, ?)""", (id(), scan["type"], scan["created_date"], scan["created_user"], scan["text"]))
	conn.commit()
