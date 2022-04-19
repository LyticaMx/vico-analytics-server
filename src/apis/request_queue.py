"""Module to send requests"""

# Libraries
import logging
import os
import pickle
from time import sleep

import redis
import requests
from rq import Queue

# Configure Loggiing
log_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
log_path = f"{log_path}/proxy-data/"
logging.basicConfig(
    filename=f"{log_path}RequestQueuer.log",
    level=logging.INFO,
)


class RequestQueuer:
    """Class to consume an API and queue requests"""

    # Configure redis connection
    queue_size = 100
    redis_conn = redis.Redis(
        host=os.environ.get("REDIS_HOST"),
        port=os.environ.get("REDIS_PORT"),
        password=os.environ.get("REDIS_PASSWORD"),
    )
    queue = Queue("low", connection=redis_conn)

    def build_url_to_consume(self, path):
        """Get the host from environment variables and complete with path"""

        url = os.environ.get("HOST_API")
        url = f"{url}{path}"

        return url

    def send_api_data(self, payload, path):
        """Send data multipart type to the corresponding endpoint"""

        url = self.build_url_to_consume(path=path)
        request_type = payload.pop("request_type")

        if request_type == "multipart/form-data":
            response = requests.post(
                url=url,
                files=payload,
            )
        elif request_type == "application/json":
            response = requests.post(
                url=url,
                json=payload,
            )

        return response

    def format_request(self, data: dict):
        """Format request to be accepted"""
        # Non-bytes values must be mapped into a tuple -> '(None, value)'
        for key, value in data.items():
            if type(value) != bytes:
                data[key] = (None, value)

        return data

    def validate_request(self, file_):
        """Validate that the request has an image"""

        try:
            # Fetch key from the InmutableDict so we can read the bytes-object
            keyword = [*file_][0]
            binary_image = file_[keyword].read()
        except (KeyError, IndexError):
            return {}

        return {keyword: binary_image}

    def queue_requests(self, path, data):
        """Enqueue the request in string format"""

        data["path"] = path
        str_data = str(data)
        self.queued = self.queue.enqueue(str_data)

        return self.queued

    def write_request_to_file(self, path, data):
        """Write in this file as requests that already enter the queue"""

        data["path"] = path
        list_data = [data]
        pickle_path = os.path.dirname
        (os.path.dirname(os.path.abspath(__file__)))
        pickle_path = f"{pickle_path}/proxy-data/request.pickle"
        if os.path.exists(pickle_path):
            with open(pickle_path, "rb") as handle:
                list_data = pickle.load(handle)

            list_data.append(data)
            with open(pickle_path, "wb") as handle:
                pickle.dump(
                    list_data,
                    handle,
                    protocol=pickle.HIGHEST_PROTOCOL,
                )

        else:
            with open(pickle_path, "wb") as handle:
                pickle.dump(
                    list_data,
                    handle,
                    protocol=pickle.HIGHEST_PROTOCOL,
                )

    def enqueue_or_write_to_a_file(self, path, data):
        """Validate queue size to know whether to enqueue or write to a file"""

        if self.queue.count < self.queue_size:
            self.queued = self.queue_requests(path=path, data=data)
        else:
            self.write_request_to_file(path=path, data=data)

    def verify_sending_request(self, data, path):
        """Check if the request was sent with a satisfactory response,
        otherwise queue the request"""

        try:
            response = self.send_api_data(payload=data, path=path)
            response.raise_for_status()
        except (
            requests.exceptions.HTTPError,
            requests.exceptions.ConnectionError,
            requests.exceptions.Timeout,
            requests.exceptions.RequestException,
        ):
            # Validate request status, status in list do not queue
            unqueued_status_list = [422, 400, 404, 405]
            if response.status_code in unqueued_status_list:
                logging.info("The request cannot be queued. Client Error")
            else:
                if self.queue.count < self.queue_size:
                    self.queued = self.queue_requests(path=path, data=data)
                    logging.info("Queued request")
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
            logging.info("Empty queue")
        else:
            queue_id = self.queue.pop_job_id()
            fech_data = self.queue.fetch_job(job_id=queue_id)
            data = fech_data.to_dict()
            payload = data["description"]
            # Remove parentheses at the end of the payload_str,
            # to be able to convert it to dict
            payload_str = payload[:-2]
            payload_send = eval(payload_str)
            path = payload_send.pop("path")
            self.verify_sending_request(data=payload_send, path=path)
            logging.info("A dequeue request was sent")

    def read_data_from_file(self):
        """Read data from the file and send it to the api"""

        pickle_path = os.path.dirname
        (os.path.dirname(os.path.abspath(__file__)))
        pickle_path = f"{pickle_path}/proxy-data/request.pickle"
        if os.path.exists(pickle_path):
            logging.info("The file does not exist")

        else:
            with open(pickle_path, "rb") as handle:
                payloads = pickle.load(handle)

            for payload_send in payloads:
                pop_path = payload_send.pop("path")
                self.verify_sending_request(data=payload_send, path=pop_path)
                sleep(1)
