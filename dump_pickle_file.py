"""Module for dump to .pickle file"""

# Modules
from src.apis.request_queue import RequestQueuer

"""Run task to check if the .plickle file contains requests and send them to the api"""

cls_api = RequestQueuer()
cls_api.read_data_from_file()
