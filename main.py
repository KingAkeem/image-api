import pytesseract
import numpy as np
import io

from flask import Flask, request
from flask_cors import CORS
from quantulum3 import parser
from PIL import Image
from http import HTTPStatus


app = Flask(__name__)
CORS(app)


"""
Reads and parses an image file, returning the relevant data based on the type 
"""
@app.route("/", methods=["POST"])
def scan():
	app.logger.debug(f'SCANNING REQUEST... {request}')
	# image type determines what kind of image we are interested
	image_type = request.args.get('image_type', default=None, type=str)

	# request.data represents the image data in bytes
	if not image_type or not request.data: 
		msg = "Image type and request data must be specified"
		app.logger.error(msg)
		return {"error": msg}, HTTPStatus.BAD_REQUEST

	# convert image to text format
	img1 = np.array(Image.open(io.BytesIO(request.data)))
	text = pytesseract.image_to_string(img1)
	app.logger.debug("IMAGE CONVERTED TO TEXT FORMAT\n\n%s", text)
	
	try:
		scanner = Scanner(image_type)
		data = scanner.scan(text)
	except ValueError as e:
		app.logger.error(e)
		return {"error": e.message}, HTTPStatus.BAD_REQUEST

	app.logger.debug("PARSED DATA\n\n%s", data)
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

if __name__ == '__main__':
	app.run(debug=True)