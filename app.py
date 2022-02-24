"""Module to write the path of a new process"""

# Libraries
import threading
from flask import Flask, request
from threading import *
import time

# Modules
from src.apis.acquisition_api import AcquisitionsAPI


app = Flask(__name__)

@app.route("/queue", methods=["POST"])
def main_acquisition():
    """Execute process to send requests to acquisition_api"""

    payload_data = request.form.to_dict()
    payload_file = request.files
    cls_aquisition = AcquisitionsAPI()
    response = cls_aquisition.validate_queue(data=payload_data, file=payload_file)

    return response


# Arranque del hilo
hilo = AcquisitionsAPI()
hilo = hilo.run()
t = Timer(3.0, hilo)
t.start()
time.sleep(20)

if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True, threaded=True),