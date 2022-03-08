"""Module to run server with uwsgi"""

# Libraries
from app import app
import uwsgidecorators

# Modules
from src.apis.request_queue import RequestQueuer


@uwsgidecorators.timer(5)
def check_queue(self):
    """Run task to release queue every five minutes"""

    cls_api = RequestQueuer()
    cls_api.empty_queue()

@uwsgidecorators.timer(7200)
def check_file(self):
    """Run task to check if the .plickle file contains requests and send them to the api"""

    cls_api = RequestQueuer()
    cls_api.read_data_from_file()


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
