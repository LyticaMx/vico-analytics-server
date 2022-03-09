"""Module to run server with uwsgi"""

# Libraries
import uwsgidecorators

# Modules
from app import app
from src.apis.request_queue import RequestQueuer


@uwsgidecorators.timer(5)
def check_queue(self):
    """Run task to release queue every five minutes"""

    cls_api = RequestQueuer()
    cls_api.empty_queue()


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
