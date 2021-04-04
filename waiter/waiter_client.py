import torch
import torchvision.models as models
from urllib.parse import urlparse
from pydoc import locate

import requests
import numpy as np
import json
import os
import sys

from torchvision import transforms
from PIL import Image

import pickle
import torch.onnx
from waiter.util import make_identifier, get_api_key, get_checksum, get_time_created, NumpyEncoder
from timeit import default_timer as timer
import socketio

main_server_loc= 'http://localhost:5000'
extension = ".onnx"

sio = socketio.Client()
sio.connect(main_server_loc)

class WaiterClient():
    def __init__(self):
        self.api_key = '7654150c-fc7d-481e-bb75-22d731da4452'
        self.persistent_id = make_identifier()
    
    def call_inference(self,numpy_input,service_name):
        start_time = timer()
        json_as_np = None
        error=None
        success = False
        
        bytesd_input=pickle.dumps(numpy_input)
        info = {'client_id':self.persistent_id,'api_key':self.api_key,'service_name':service_name,'input':bytesd_input}
        resp = sio.call('do_inference',info)
        return json_as_np

    def check_service(self,service_name):
        stats = {"api_key":self.api_key, "service_name":service_name,"server_id":self.persistent_id}
        resp_info = sio.call('service_exists',json.dumps(stats,cls=NumpyEncoder))
        return resp_info

    def on_return_result(self,data):
        print("GOT RESULT BACK!")
