"""Module"""

# Libraries
import os
from dataclasses import dataclass
import requests
from io import BytesIO
from collections import deque
import cv2

@dataclass
class AcquisitionsAPI:
    """Class"""

    def receive_data(self):
        """b"""

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

        return multipart_form_data
    
    def send_api_data(self, multipart_form_data):
        """ """

        # url = os.environ.get("ACQUISITION_API", None)
        url = "https://dev.vico.ai/acquisition/monito"
        response = requests.post(url=url, files=multipart_form_data)

        return response

    def validate_queue(self):
        """ """

        queue_size = 3
        cola = deque(maxlen=queue_size)

        while True:
            multipart_form_data = self.receive_data()
            response  = self.send_api_data(multipart_form_data=multipart_form_data)
            try:
                response.raise_for_status()
            except (requests.exceptions.HTTPError, requests.ConnectionError, requests.Timeout):
                if len(cola) < queue_size:
                    cola.append(multipart_form_data.items())
                else:
                    filehandler = open('peticiones.txt', 'wt')
                    data = str(multipart_form_data)
                    filehandler.write(data)
