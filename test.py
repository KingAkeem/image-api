import requests


"""
Reads nutrition file from example directory and attempts to convert it to json then prints the result
"""
def run_test():
	print("Testing with nutrition image...")
	with open("examples/nutrition_facts.jpeg", 'rb') as f:
		response = requests.post('http://127.0.0.1:5000/scan?user=automated&type=nutrition', data=f)
		print(response.json())

run_test()
