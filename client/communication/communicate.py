import requests
import time

from api_define import *


class BaseCommunicate:
    def __init__(self, device_key):
        self.m_device_key = device_key

    @staticmethod
    def get_timestamp():
        millis = int(round(time.time() * 1000))
        return millis

    def get_body_data(self, data=None):
        timestamp = self.get_timestamp()
        body = {
            'timestamp': timestamp,
            'deviceName': 'Test',
            'productKey': self.m_device_key
        }
        if data:
            body.update(data)
        return body

    def get_device_info(self):
        request = requests.post(GET_DEVICE_INFO, data=self.get_body_data())
        print(request.text)
        print(request.headers)


if __name__ == '__main__':
    connection = BaseCommunicate('pPrIkmvSP89JYo_xrGwPwbEVR6wRZO-cixisuDuGlDM')
    connection.get_device_info()


