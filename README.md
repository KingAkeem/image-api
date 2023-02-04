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

## File Storage
Scanned files are stored in the `files` directory by default.
The directory naming convention is
`/files/{user}/{scan_type}/{time}`

The files saved are
- bytes (bytes data of image)
- data.txt (text data of image)

## Database
The database is sqlite3. The database file is stored under the `database` directory by default.
The name of the database is `scans`, it contains two tables.
- scans: a table of records containing the scan information and including text data
- status_tracker: a table of status information about each scanned record

------

## Endpoints

### Request
POST /scan

Query Parameters
- user - who initiated the scan
- type - type of scan desired (optional)
	* `nutrition`

If a type isn't specified, the plain text of the image will be returned

### Response
JSON object containing the results of the type or text if a valid type is not passed.

----

### Supported options 
- Nutrition Labels (`.jpeg`, `.jpg`)

