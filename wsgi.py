from app import app
import uwsgidecorators

from src.apis.acquisition_api import ConsumeAPI

@uwsgidecorators.timer(15)
def job(self):
    cls_aquisition = ConsumeAPI()
    cls_aquisition.empty_queue()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)