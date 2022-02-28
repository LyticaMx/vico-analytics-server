"""Module to write the path of a new process"""

# Libraries
from flask import Flask, request, Response

# Modules
from src.apis.acquisition_api import ConsumeAPI


# create app
app = Flask(__name__)

@app.route('/', defaults={'path': ''})
@app.route("/<path:path>", methods=['GET', 'POST'])
def main_acquisition(path):
    """Execute process to send requests to acquisition_api"""

    payload_data = request.form.to_dict()
    payload_file = request.files
    cls_aquisition = ConsumeAPI()
    response, status = cls_aquisition.main(data=payload_data, file_=payload_file, path=path)

    return Response(response, status)


if __name__ == "__main__":
    app.run()