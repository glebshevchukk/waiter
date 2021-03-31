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
from waiter.util import make_identifier, NumpyEncoder
import socketio

from timeit import default_timer as timer


main_server_loc= 'http://localhost:5000'

class Waiter(object):
    def __init__(self,connection_point=None):
        self.connection_point = connection_point
        self.identifier = make_identifier()
        self.sio = socketio.Client()
        self.sio.connect(main_server_loc)
        self.send_handshake()


    def send_model(self,model_name,model):
        unique_id = make_identifier()
        file_name = model_name + "-" + unique_id + ".onnx"
        x = torch.randn(1, 3, 224, 224, requires_grad=True)
        torch.onnx.export(model,x, file_name,export_params=True)
        try:
            files = {model_name: open(file_name, 'rb')}
            resp = requests.post(self.connection_point+"/sync",files=files)
        except Exception as e:
            print(e)

    def inference(self,numpy_input,model_name):
        start_time = timer()
        json_as_np = None
        error=None
        success = False
        try:
            resp = requests.post(self.connection_point+"/infer/"+model_name,json=json.dumps(numpy_input, cls=NumpyEncoder))
            json_as_np = np.array(resp.json())
            success = True
        except Exception as e:
            error = str(e)
        end_time = timer()
        elapsed_time = end_time-start_time
        if success:
            batch_size = json_as_np.shape[0]
        else:
            batch_size = 0
        current_time = timer()
        stats = {"sent_time":current_time,"service_id":self.identifier,"elapsed":elapsed_time,"batch_size":batch_size,"success":success,"error":error}
        print(stats)
        self.sio.emit('statistics', json.dumps(stats))
        return json_as_np
        
    def send_handshake(self):
        current_time = timer()
        stats = {"sent_time":current_time,"service_id":self.identifier}
        self.sio.emit('handshake', json.dumps(stats))
       

