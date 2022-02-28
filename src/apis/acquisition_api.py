"""Module to send requests"""

# Libraries
import os
import re
import time
import requests
from urllib3.exceptions import MaxRetryError, NewConnectionError
import redis
from rq import Queue
import logging
from dotenv import load_dotenv, find_dotenv


class ConsumeAPI():
    """Class to consume an API and queue requests"""

    load_dotenv(find_dotenv())
    logging.basicConfig(filename='myapp.log', level=logging.INFO)

    queue_size = 5
    redis_conn = redis.Redis(
                        host=os.environ.get("REDIS_HOST"),
                        port=os.environ.get("REDIS_PORT"),
                        password=os.environ.get("REDIS_PASSWORD"),
                )
    cola = Queue("low", connection=redis_conn)

    def send_api_data(self, payload, path):
        """Send data to the corresponding endpoint"""

        url = os.environ.get("HOST_API")
        url = f"{url}{path}"
        response = requests.post(url=url, files=payload,)
        time.sleep(3)

        return response

    def format_request(self, data, image):
        """Format request to be accepted"""

        data["file"] = image
        data["visitor"] = (None, data["visitor"])

        return data


    def validate_request(self, file_):
        """Validate that the request has an image"""

        try:
            binary_image = file_["file"].read()
        except KeyError:
            binary_image = None

        return binary_image


    def validate_queue(self, response, data, path):
        """Queue requests"""

        try:
            response.raise_for_status()
        except (requests.exceptions.HTTPError, 
                requests.exceptions.ConnectionError, 
                requests.exceptions.Timeout, 
                requests.exceptions.RequestException,
                MaxRetryError,
                NewConnectionError):
            data["path"] = path
            if len(self.cola) < self.queue_size:
                str_data = str(data)
                self.queue = self.cola.enqueue(str_data)
                logging.info('Queued request')
                return response.content, response.status_code
            else:
                with open('request.txt', 'a') as handler:
                    data = str(data)
                    handler.write("\n" + data)

        return response.content, response.status_code


    def main(self, data, file_, path):
        """Method Main"""
        
        binary_image = self.validate_request(file_=file_)
        data = self.format_request(data=data, image=binary_image)
        response  = self.send_api_data(payload=data, path=path)
        response, status = self.validate_queue(response=response, data=data, path=path)
        
        return response, status

    def empty_queue(self):
        """Forward requests to empty the queue"""

        if self.cola.count == 0:
            logging.info('Empty queue')
        else:
            logging.info("Dequeue")
            queue_id =  self.cola.pop_job_id()
            fech_data = self.cola.fetch_job(job_id=queue_id)
            data = fech_data.to_dict()
            payload = data["description"]
            payload_str = payload[:-2]
            payload_send = eval(payload_str)
            path = payload_send.pop("path")
            response  = self.send_api_data(payload=payload_send, path=path)
            self.validate_queue(response=response, data=payload_send, path=path)
