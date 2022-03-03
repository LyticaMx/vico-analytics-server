"""Module to run server with uwsgi"""

# Libraries
from app import app
import uwsgidecorators

# Modules
from src.apis.acquisition_api import ConsumeAPI

@uwsgidecorators.timer(15)
def check_queue(self):
    """Run task to release queue every five minutes"""

    cls_api = ConsumeAPI()
    cls_api.empty_queue()

@uwsgidecorators.timer(20)
def check_file(self):
    """Run task to check if the .plickle file contains requests and send them to the api"""

    cls_api = ConsumeAPI()
    cls_api.read_data_from_file()


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)