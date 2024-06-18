# Short URL

Web-service to shorten URLs.

## Installation

1. Checkout the GIT-repository and `cd` into the project root.
2. Create a virtual environment: `python3 -m venv .venv`
3. Activate the virtual environment: `source .venv/bin/activate`
4. Install dependencies: `pip install -r requirements.txt`

Note: this service was written and tested using Python version 3.10.

## Run

To run the service:
 - make sure a MySQL-server is running and accessible
 - make sure your MySQL-database contains the schema as defined in [sql/schema.sql](sql/schema.sql)
 - make sure environment variables are set (DB_HOST, DB_PORT, DB_NAME, DB_USER, DB_PASS)
 - start the service: `fastapi dev shorturl/main.py`

The service will be serving at http://127.0.0.1:8000/ and API docs are available at http://127.0.0.1:8000/docs.

## Tests

To run all tests (both unit and integration) run `pytest` from the project root.

## Docker

To start both the service and a MySQL-server in Docker containers, run `docker compose up --build`
