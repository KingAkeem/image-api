import requests


def run_test():
	with open("examples/nutrition_facts.jpeg", 'rb') as f:
		response = requests.post('http://127.0.0.1:5000/?image_type=nutrition', data=f)
		print(response.json())

run_test()
