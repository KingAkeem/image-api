import requests

"""
Reads nutrition file from example directory and attempts to convert it to json then prints the result
"""
def run_test():
	file_name = "examples/nutrition_facts.jpeg" 
	print(f"testing nutrition scan w/ {file_name}")
	with open(file_name, 'rb') as f:
		response = requests.post('http://127.0.0.1:5000/scan?user=automated&type=nutrition', data=f)
		print(response.json())

	print(f"testing generic scan w/ {file_name}")
	with open(file_name, 'rb') as f:
		response = requests.post('http://127.0.0.1:5000/scan?user=automated', data=f)
		print(response.text)

run_test()
