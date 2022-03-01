"""Module to run server with uwsgi"""

# Libraries
from app import app
import uwsgidecorators

# Modules
from src.apis.acquisition_api import ConsumeAPI

@uwsgidecorators.timer(15)
def job(self):
    """Run task to release queue every five minutes"""
    cls_aquisition = ConsumeAPI()
    cls_aquisition.empty_queue()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)