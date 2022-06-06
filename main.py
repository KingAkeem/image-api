from crypt import methods
from PIL import Image
import pytesseract
import numpy as np
import io

from quantulum3 import parser
from flask import Flask, request
from flask_cors import CORS


app = Flask(__name__)
CORS(app)

@app.route("/", methods=["POST"])
def scan():
	img1 = np.array(Image.open(io.BytesIO(request.data)))
	text = pytesseract.image_to_string(img1)

	scanner = NutritionScanner()
	scanner.scan_nutrition(text) 
	return scanner.nutrition

class NutritionScanner:
	def __init__(self):
		self.nutrition = {}
		self.keys = [
			"Serving Size", 
			"Amount Per Serving",
			"Calories",
			"Total Fat",
			"Saturated Fat"
			"Trans Fat",
			"Cholesterol",
			"Sodium",
			"Total Carbohydrate",
			"Dietary Fiber",
			"Sugars",
			"Protein",
			"Vitamin A",
			"Calcium"
		]

		# load keys
		for key in self.keys:
			self.nutrition[key] = {}
		
	def insert_quantity(self, key, quantity):
		if quantity.unit.name in self.nutrition[key]:
			self.nutrition[key][quantity.unit.name] += quantity.value
		else:
			self.nutrition[key][quantity.unit.name] = quantity.value
	

	def scan_nutrition(self, text):
		for line in text.split('\n'):
			for key in self.keys:
				if line.startswith(key):
					for quantity in parse_quantities(key, line):
						self.insert_quantity(key, quantity)

# get all of the text after the key which includes the parsable quantities 
def parse_quantities(key, line):
	end_position = line.find(key) + len(key)
	quantities = parser.parse(line[end_position:])
	return quantities