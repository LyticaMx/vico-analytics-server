"""Module to write the path of a new process"""

# Libraries
from flask import Flask, request
from threading import *
from flask_apscheduler import APScheduler
from collections import deque


# Modules
from src.apis.acquisition_api import AcquisitionsAPI

class Config:
    SCHEDULER_API_ENABLED = True

# create app
app = Flask(__name__)
app.config.from_object(Config())
# initialize scheduler
scheduler = APScheduler()
# if you don't wanna use a config, you can set options here:
# scheduler.api_enabled = True
scheduler.init_app(app)

queue_size = 3
cola = deque(maxlen=queue_size)

@app.route("/", methods=["POST"])
def main_acquisition():
    """Execute process to send requests to acquisition_api"""
    payload_data = request.form.to_dict()
    payload_file = request.files
    cls_aquisition = AcquisitionsAPI()
    response = cls_aquisition.validate_queue(data=payload_data, file_=payload_file)

    return response


@scheduler.task('interval', id='do_job_1', seconds=5)
def job():
    cls_aquisition = AcquisitionsAPI()
    cls_aquisition.empty_queue()

scheduler.start()

if __name__ == "__main__":
    app.run(host='0.0.0.0')
