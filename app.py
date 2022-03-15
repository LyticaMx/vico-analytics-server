"""Module to write the path of a new process"""

# Libraries
from flask import Flask, jsonify, make_response, request

# Modules
from src.apis.request_queue import RequestQueuer

# create app
app = Flask(__name__)


@app.route("/", defaults={"path": ""})
@app.route("/<path:path>", methods=["GET", "POST"])
def main_consume_api(path):
    """Execute process to send requests to api"""

    cls_api = RequestQueuer()
    if request.json is None:
        payload_data = request.form.to_dict()
        payload_file = request.files
        binary_image = cls_api.validate_request(file_=payload_file)
        data = cls_api.format_request(data={**payload_data, **binary_image})
        if cls_api.queue.count < cls_api.queue_size:
            cls_api.queued = cls_api.queue_requests(path=path, data=data)
        else:
            cls_api.write_request_to_file(path=path, data=data)
    else:
        cls_api.queue_requests(path=path, data=request.json)

    message_info = {"message": "Request accepted"}
    return make_response(jsonify(message_info), 202)


if __name__ == "__main__":
    app.run()
