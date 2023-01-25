import requests


"""
Reads nutrition file from example directory and attempts to convert it to json then prints the result
"""
def run_test():
	with open("examples/nutrition_facts.jpeg", 'rb') as f:
		response = requests.post('http://127.0.0.1:5000/?user=automated&scan_type=nutrition', data=f)
		print(response.json())

run_test()