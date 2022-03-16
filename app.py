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
    else:
        data = request.json

    data = {**{"request_type": request.mimetype}, **data}

    cls_api.enqueue_or_write_to_a_file(path=path, data=data)
    message_info = {"message": "Request accepted"}
    return make_response(jsonify(message_info), 202)


if __name__ == "__main__":
    app.run()
