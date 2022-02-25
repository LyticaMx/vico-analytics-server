"""Module"""

# Libraries
import os
import time
from dataclasses import dataclass
import requests
from io import BytesIO
from collections import deque
from threading import *
import cv2

@dataclass
class AcquisitionsAPI():
    """Class"""

    def send_api_data(self, payload, image):
        """ """

        url = os.environ.get("ACQUISITION_API")
        # url = "https://dev.vico.ai/acquisition/visitor-counte"
        response = requests.post(url=url, files={"file": image, "visitor": (None, payload)},)

        return response

    def validate_queue(self, data, file_):
        """ """
        queue_size = 3
        cola = deque(maxlen=queue_size)

        payload= data["visitor"]
        binary_image = file_["file"].read()
        response  = self.send_api_data(payload=payload, image=binary_image)
        try:
            response.raise_for_status()
        except (requests.exceptions.HTTPError, requests.ConnectionError, requests.Timeout):
            if len(cola) < queue_size:
                cola = cola.append(data.items())
                print("COLA: ", cola)
                return response.content, cola
            else:
                with open('request.txt', 'a') as handler:
                    data = str(data)
                    handler.write("\n" + data)

        return response.content

    def empty_queue(self):
        print("cola")
