"""Module to send requests"""

# Libraries
import os
import requests
import redis
from rq import Queue

class ConsumeAPI():
    """Class to consume an API and queue requests"""

    queue_size = 5
    redis_conn = redis.Redis(
                        host=os.environ.get("REDIS_HOST"),
                        port=os.getenv("REDIS_PORT"),
                        password=os.getenv("REDIS_PASSWORD"),
                )
    cola = Queue("low", connection=redis_conn)

    def send_api_data(self, payload, path):
        """Send data to the corresponding endpoint"""

        url = os.environ.get("HOST_API")
        url = f"{url}{path}"
        response = requests.post(url=url, files=payload,)

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
        except (requests.exceptions.HTTPError, requests.ConnectionError, requests.Timeout):
            data["path"] = path
            if len(self.cola) < self.queue_size:
                str_data = str(data)
                self.queue = self.cola.enqueue(str_data)
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
        
        if self.cola.count > 0:
            print("Q: ", self.cola.get_jobs())
            queue_id =  self.cola.pop_job_id()
            queue_index = queue_id.index(queue_id)
            print("Position: ", queue_index)
            data = self.cola.fetch_job(job_id=queue_id)
            data = data.to_dict()
            print("PAYLOAD: ", data)
            payload = data["description"]
            path = payload[0]["path"]
            print("DATA: ", path)
            # response  = self.send_api_data(payload=data, path=path)
            # self.validate(response=response, data=payload)
        else:
            print("Cola Vacia")
