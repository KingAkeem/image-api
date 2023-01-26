# image-api
This service is used to scan images and JSON objects containing relevant information.

## Technologies you should know about
- poetry (dependency manager)
- sqlite (database engine)
- flask (server framework)

## How to use this service
The service can be run using the `run.sh` script or `poetry` directly.
Either method will start the service listening locally on port 5000 by default.

- Using `run.sh` script
```bash
chmod +x run.sh
./run.sh
```

- Using `poetry`
```bash
poetry install
poetry run python main.py
```
------

## Endpoints

### Request
POST /scan

Query Parameters
- user - who initiated the scan
- type - type of scan desired
	* `nutrition`

### Response
JSON object containing the results

----

### Supported options 
- Nutrition Labels (`.jpeg`, `.jpg`)

