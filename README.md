# vico-analytics-server

Intermediary server

### Prerequisites

- Python 3.8
- Flaks 2.0
- requests 2.27
- Poetry 1.0+

### Installing

- Follow the variables in the .env.sample to a .env indicating your own credentials.
- Run poetry install
- Run poetry shell
- Run flask run

## Run Queue
- Run rq worker

## Run Uwsgi
- Run uwsgi --socket 0.0.0.0:5000 --protocol=http -w wsgi:app --enable-threads --master

## Build Whit
* Flask
* Python