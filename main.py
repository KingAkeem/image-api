from PIL import Image
import pytesseract
import numpy as np
import io

from quantulum3 import parser
from flask import Flask, request
from flask_cors import CORS


app = Flask(__name__)
CORS(app)

ok_status_code = 200
bad_request_status_code = 400

if __name__ == '__main__':
	app.run(debug=True)

"""
Reads and parses an image file, returning the relevant data based on the type 
"""
@app.route("/", methods=["POST"])
def scan():
	# image type determines what kind of image we are interested
	image_type = request.args.get('image_type', default=None, type=str)

	# request.data represents the image data
	if not image_type or not request.data: 
		return {"error": "Image type and request data must be specified"}, bad_request_status_code

	# convert image to text format
	img1 = np.array(Image.open(io.BytesIO(request.data)))
	text = pytesseract.image_to_string(img1)
	
	try:
		scanner = Scanner(image_type)
		data = scanner.scan(text)
	except ValueError as e:
		return {"error": e.message}, bad_request_status_code

	return data, ok_status_code

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

	# get all of the text after the key which includes the parsable quantities 
	def parse_quantities(key, line):
		end_position = line.find(key) + len(key)
		quantities = parser.parse(line[end_position:])
		return quantities