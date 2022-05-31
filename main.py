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
	return scan_ingredients(text) 

nutrition_fact_keys = [
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

def scan_ingredients(text):
	ingredients = {}
	for line in text.split('\n'):
		for nutrition_fact_key in nutrition_fact_keys:
			if line.startswith(nutrition_fact_key):

				end_position = line.find(nutrition_fact_key) + len(nutrition_fact_key)
				quantities = parser.parse(line[end_position:])

				ingredients[nutrition_fact_key] = {}

				for quantity in quantities:
					if quantity.unit.name in ingredients[nutrition_fact_key]:
						ingredients[nutrition_fact_key][quantity.unit.name] += quantity.value
					else:
						ingredients[nutrition_fact_key][quantity.unit.name] = quantity.value
	return ingredients

