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
from queue import Queue

import uuid

main_server_loc= 'http://localhost:5000'
extension = ".onnx"


class WaiterClient():
    def __init__(self):
        self.api_key = '7654150c-fc7d-481e-bb75-22d731da4452'
        self.persistent_id = make_identifier()
        self.sio = socketio.Client()
        self.call_backs()
        self.sio.connect(main_server_loc)
        self.result = Queue()

    def call_backs(self):
        @self.sio.event
        def return_result(data):
            d = pickle.loads(data)
            self.result.put(d)

    def call_inference(self,numpy_input,service_name,blocking=True):
        start_time = timer()
        json_as_np = None
        error=None
        success = False
        
        bytesd_input=pickle.dumps(numpy_input)
        job_id = str(uuid.uuid4())
        info = {'client_id':self.persistent_id,'api_key':self.api_key,\
            'service_name':service_name,'input':bytesd_input,\
            'job_id':job_id}
        
        self.sio.emit('do_inference',info)
        if blocking:
            returned = self.result.get(block=True)
            return returned
        else:
            return job_id

    def check_service(self,service_name):
        stats = {"api_key":self.api_key, "service_name":service_name,"server_id":self.persistent_id}
        resp_info = self.sio.call('service_exists',json.dumps(stats,cls=NumpyEncoder))
        return resp_info
