"""Module to send requests"""

# Libraries
import os
from time import sleep
import requests
import redis
from rq import Queue
import logging
import pickle
from dotenv import load_dotenv, find_dotenv


logging.basicConfig(filename='RequestQueuer.log', level=logging.INFO)

class RequestQueuer():
    """Class to consume an API and queue requests"""

    load_dotenv(find_dotenv())
    
    queue_size = 10
    redis_conn = redis.Redis(
                        host=os.environ.get("REDIS_HOST"),
                        port=os.environ.get("REDIS_PORT"),
                        password=os.environ.get("REDIS_PASSWORD"),
                )
    queue = Queue("low", connection=redis_conn)

    def send_api_data(self, payload, path):
        """Send data to the corresponding endpoint"""

        url = os.environ.get("HOST_API")
        url = f"{url}{path}"
        response = requests.post(url=url, files=payload,)

        return response

    def format_request(self, data, image):
        """Format request to be accepted"""

        for key, value in data.items():
            if key != "file":
                key = {key: (None, value)}
        
            key["file"] = image

        return key

    def validate_request(self, file_):
        """Validate that the request has an image"""

        try:
            binary_image = file_["file"].read()
        except KeyError:
            binary_image = None

        return binary_image

    def queue_requests(self, path, data):
        """Enqueue the request in string format"""

        data["path"] = path
        str_data = str(data)
        self.queued = self.queue.enqueue(str_data)

        return self.queued

    def write_request_to_file(self, path, data):
        """Write in this file as requests that already enter the queue"""

        data["path"] = path
        if os.path.dirname("request.pickle"):
            list_data = [data]
            with open('request.pickle', 'wb') as handle:
                pickle.dump(list_data, handle, protocol=pickle.HIGHEST_PROTOCOL)
        else:
            with open('request.pickle', 'rb') as handle:
                list_data = pickle.load(handle)
            
            list_data.append(data)
            with open('request.pickle', 'wb') as handle:
                pickle.dump(list_data, handle, protocol=pickle.HIGHEST_PROTOCOL)

    def verify_sending_request(self, data, path):
        """Check if the request was sent with a satisfactory response, 
           otherwise queue the request"""
          
        try:
            response = self.send_api_data(payload=data, path=path)
            response.raise_for_status()
        except (requests.exceptions.HTTPError, 
                requests.exceptions.ConnectionError, 
                requests.exceptions.Timeout, 
                requests.exceptions.RequestException,):
            if self.queue.count < self.queue_size:
                self.queued = self.queue_requests(path=path, data=data)
                logging.info('Queued request')
            else:
                self.write_request_to_file(path=path, data=data)

    def main(self, data, file_, path):
        """Method Main"""
        
        binary_image = self.validate_request(file_=file_)
        data = self.format_request(data=data, image=binary_image)
        self.verify_sending_request(data=data, path=path)
        
    def empty_queue(self):
        """Forward requests to empty the queue"""

        if self.queue.count == 0:
            logging.info('Empty queue')
        else:
            queue_id =  self.queue.pop_job_id()
            fech_data = self.queue.fetch_job(job_id=queue_id)
            data = fech_data.to_dict()
            payload = data["description"]
            # Remove parentheses at the end of the payload_str to be able to convert it to dict
            payload_str = payload[:-2]
            payload_send = eval(payload_str)
            path = payload_send.pop("path")
            self.verify_sending_request(data=payload_send, path=path)
            logging.info("A dequeue request was sent")

    def read_data_from_file(self):
        """Read data from the file and send it to the api"""

        if os.path.dirname("request.pickle"):
            with open("request.pickle", "rb") as handle:
                payloads = pickle.load(handle)
            
            for payload_send in payloads:
                pop_path = payload_send.pop("path")
                self.verify_sending_request(data=payload_send, path=pop_path)
                sleep(1)
        else:
            logging.info("The file does not exist")
            print("Vacio")
