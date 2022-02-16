"""Module to write the path of a new process"""

# Libraries
from flask import Flask

# Modules
from src.apis.acquisition_api import AcquisitionsAPI


app = Flask(__name__)

@app.route("/queue")
def main_acquisition():
    """Execute process to send requests to acquisition_api"""

    cls_aquisition = AcquisitionsAPI()
    process = cls_aquisition.validate_queue()
