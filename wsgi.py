"""Module to run server with uwsgi"""

# Libraries
from app import app
import uwsgidecorators
import os

# Modules
from src.apis.acquisition_api import ConsumeAPI

@uwsgidecorators.timer(15)
def job(self):
    """Run task to release queue every five minutes"""

    cls_api = ConsumeAPI()
    cls_api.empty_queue()

@uwsgidecorators.timer(20)
def job1(self):
    """ """

    cls_api = ConsumeAPI()
    cls_api.extract_line_with_data()


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)