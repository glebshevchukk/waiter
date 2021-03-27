import torch

from flask import jsonify,send_from_directory
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

class Waiter(object):
    def __init__(self,connection_point=None):
        self.connection_point = connection_point

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
        try:
            resp = requests.post(self.connection_point+"/infer/"+model_name,json=json.dumps(numpy_input, cls=NumpyEncoder))
            json_as_np = np.array(resp.json())
            return json_as_np
        except Exception as e:
            print(e)
            return None
