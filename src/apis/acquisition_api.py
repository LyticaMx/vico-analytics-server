"""Module"""

# Libraries
import os
from dataclasses import dataclass
import requests
from io import BytesIO
from collections import deque
from threading import *
import time
import cv2

@dataclass
class AcquisitionsAPI(Thread):
    """Class"""

    def __init__(self):
        self.queue_size = 3
        self.cola = deque(maxlen=self.queue_size)
    
    def send_api_data(self, multipart_form_data):
        """ """

        # url = os.environ.get("ACQUISITION_API", None)
        url = "https://dev.vico.ai/acquisition/monito"
        response = requests.post(url=url, files=multipart_form_data)

        return response

    def validate_queue(self, data, file):
        """ """

        # file_name = file["capture"].read()
        # # path = f"/tmp/{file_name}"

        # data["capture"] = file_name
        cap = cv2.VideoCapture(0)
        _, frame = cap.read()

        file = BytesIO()
        timestamp = "2022-02-15T15:00:00.000000"
        file_name = f"{timestamp}.jpg"
        path = f"/tmp/{file_name}"

        cv2.imwrite(path, frame)
        multipart_form_data = {
            "store_id": (None, 4),
            "timestamp": (None, timestamp),
            "process": (None, "gender"),
            "status": (None, "running"), # Optional
            "tracking_id": (None, 15), # Optional
            "centroid": (None, "50,50"), # Optional
            "capture": (file_name, open(path, "rb")),
        }
        response  = self.send_api_data(multipart_form_data=multipart_form_data)
        print(response)
        try:
            response.raise_for_status()
        except (requests.exceptions.HTTPError, requests.ConnectionError, requests.Timeout):
            if len(self.cola) < self.queue_size:
                self.cola.append(data.items())
            else:
                with open('request.txt', 'a') as handler:
                    data = str(data)
                    handler.write("\n" + data)

        return response.content
        

    def run(self):
        # Aqui el codigo del hilo
        print(self.cola)
