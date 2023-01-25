import io
import os
import pytesseract
import numpy as np
import sqlite3

from flask import Flask, request, g
from flask_cors import CORS
from quantulum3 import parser
from PIL import Image
from http import HTTPStatus
from datetime import datetime, timezone


app = Flask(__name__)
CORS(app)

FILE_DIR = "files"

if not os.path.exists(FILE_DIR):
	os.makedirs(FILE_DIR)


"""
Reads and parses an image file, returning the relevant data based on the type 
"""
@app.route("/", methods=["POST"])
def scan():
	app.logger.debug(f'SCANNING REQUEST... {request}')
	# scan type determines what kind of image we are interested
	scan_type = request.args.get('scan_type', default=None, type=str)
	# the user that initiates the scan
	user = request.args.get('user', default=None, type=str)

	db = get_db()

	insert_request(db, {
		"id": "abc",
		"scan_id": None,
		"created_date": datetime.now(timezone.utc).isoformat(),
		"created_user": user,
		"status": "PROCESSING"
	})

	# request.data represents the image data in bytes
	if not scan_type or not request.data or not user: 
		msg = "Image type, user and request data must be specified"
		app.logger.error(msg)
		return {"error": msg}, HTTPStatus.BAD_REQUEST

	# convert image to text format
	img1 = np.array(Image.open(io.BytesIO(request.data)))
	text = pytesseract.image_to_string(img1)
	app.logger.debug("IMAGE CONVERTED TO TEXT FORMAT\n\n%s", text)

	current_time = datetime.now(timezone.utc)
	directory_name = os.path.join(FILE_DIR, user, scan_type, current_time.isoformat())
	if not os.path.exists(directory_name):
		os.makedirs(directory_name)

	with open(f'{directory_name}/bytes', 'wb+') as f:
		f.write(request.data)

	with open(f'{directory_name}/data.txt', 'w+') as f:
		f.write(text)

	try:
		scanner = Scanner(scan_type)
		data = scanner.scan(text)
	except ValueError as e:
		app.logger.error(e)
		return {"error": e.message}, HTTPStatus.BAD_REQUEST

	insert_scan(db, {
		"id": "abc",
		"type": scan_type,
		"created_date": current_time, 
		"created_user": user,
		"text": text
	})

	app.logger.debug("PARSED DATA\n\n%s", data)
	insert_request(db, {
		"id": "abc",
		"scan_id": "scan_id",
		"created_date":datetime.now(timezone.utc).isoformat(), 
		"created_user": user,
		"status": "DONE"
	})

	return data, HTTPStatus.OK

class ScannerInterface:
	def scan(self, text):
		raise NotImplementedError("ScannerInterface requires scan method")


class Scanner(ScannerInterface):
	def __init__(self, type):
		super().__init__()
		if type.lower() == "nutrition":
			self._scanner = NutritionScanner()

		if not self._scanner:
			raise ValueError("unsupported scanner type, found ", type)
		
	def scan(self, text):
		return self._scanner.scan(text)


class NutritionScanner(ScannerInterface):
	def __init__(self):
		super().__init__()
		self.data = {
			"Serving Size": {}, 
			"Amount Per Serving": {},
			"Calories": {},
			"Total Fat": {},
			"Saturated Fat": {},
			"Trans Fat": {},
			"Cholesterol": {},
			"Sodium": {},
			"Total Carbohydrate": {},
			"Dietary Fiber": {},
			"Sugars": {},
			"Protein": {},
			"Vitamin A": {},
			"Calcium": {}
		}

	def insert_quantity(self, key, quantity):
		if quantity.unit.name in self.data[key]:
			self.data[key][quantity.unit.name] += quantity.value
		else:
			self.data[key][quantity.unit.name] = quantity.value
	
	def scan(self, text):
		for line in text.split('\n'):
			for key in self.data.keys():
				if line.startswith(key):
					for quantity in self.parse_quantities(key, line):
						self.insert_quantity(key, quantity)
		return self.data

	# get all of the text after the key which includes the parsable quantities 
	def parse_quantities(self, key, line):
		end_position = line.find(key) + len(key)
		quantities = parser.parse(line[end_position:])
		return quantities

def get_db(database = "database/scans"):
	db = getattr(g, '_database', None)
	if db is None:
		if not os.path.exists("database"):
			os.makedirs("database")

		db = g._database = sqlite3.connect(database)
	
	return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()


def setup_tables(conn):
	db = conn.cursor()
	db.execute("""
		CREATE TABLE IF NOT EXISTS request_tracker(
			id,
			scan_id,
			created_date,
			created_user,
			status
		)
	""")

	db.execute("""
		CREATE TABLE IF NOT EXISTS scan(
			id,
			created_date,
			created_user,
			text,
			type
		)
	""")
	conn.commit()

def insert_request(conn, request):
	db = conn.cursor()
	db.execute(f'''INSERT INTO request_tracker (
		id, 
		scan_id,
		created_date,
		created_user,
		status
	) VALUES (?, ?, ?, ?,?);''', (request["id"], request["scan_id"], request["created_date"], request["created_user"], request["status"]))
	conn.commit()

def insert_scan(conn, scan):
	db = conn.cursor()
	db.execute(f"""INSERT INTO scan (
		id, 
		type,
		created_date,
		created_user,
		text
	) VALUES (?, ?, ?, ?, ?)""", (scan["id"], scan["type"], scan["created_date"], scan["created_user"], scan["text"]))
	conn.commit()


def init_db():
	with app.app_context():
		db = get_db()
		setup_tables(db)

if __name__ == '__main__':
	init_db()
	app.run(debug=True)