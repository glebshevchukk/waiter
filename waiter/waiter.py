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
from waiter.flask_service import add_model,run_app
import socketio

from timeit import default_timer as timer

extension = ".onnx"
model_dir = "./model_files/"
main_server_loc= 'http://localhost:5000'
sio = socketio.Client()
sio.connect(main_server_loc)

class Waiter(object):
    def __init__(self):
        self.api_key = get_api_key()
        self.server_id = sio.sid()

    def serve(self,service_name,model_path=None):
        #if a model isn't specified, we have to pull it from another server
        info = self.check_service(service_name)
        if model_path == None:
            if not bool(info['exists']):
                print("That service does not exist anywhere. Please either sync or upload the model for it.")
            else:
                self.get_model(service_name)
                print(f"Service {service_name} has been successfully pulled and you can now use it. ")
        #if a model is specified, we just serve it
        else:
            #if it isn't the latest model, we should pull the latest one
            if bool(info['exists']) and not info['checksum'] == get_checksum(service_name):
                self.get_model(service_name)
                print(f"Service {service_name} has been successfully updated")
        self.broadcast_model(service_name)
        model_path = model_dir + service_name + extension
        add_model(service_name,model_path)
    
    def start(self):
        run_app()

    def inference(self,numpy_input,service_name):
        start_time = timer()
        json_as_np = None
        error=None
        success = False
        try:
            resp = requests.post(main_server_loc+"/infer/"+service_name,json=json.dumps(numpy_input, cls=NumpyEncoder))
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
        stats = {"sent_time":current_time,"elapsed":elapsed_time,"batch_size":batch_size,"success":success,"error":error}
        sio.emit('statistics', json.dumps(stats))
        return json_as_np
        
    def send_handshake(self):
        current_time = timer()
        stats = {"sent_time":current_time,"server_id":self.identifier}
        sio.emit('handshake', json.dumps(stats))

    def broadcast_model(self,service_name):
        model_path = model_dir+service_name+extension
        checksum = get_checksum(model_path)
        file_created = get_time_created(model_path)
        stats = {"service_name":service_name,\
                "checksum":checksum,"file_created":file_created,\
                "api_key":self.api_key}
        sio.emit('broadcast_service', json.dumps(stats))

    def check_service(self,service_name):
        stats = {"api_key":self.api_key, "service_name":service_name}
        resp = sio.call('service_exists',json.dumps(stats))

        resp_info = json.loads(resp.data)
        return resp_info
       
    def get_model(self,service_name):
        model_path = model_dir+service_name+extension
        info = {'api_key':self.api_key,'service_name':service_name}
        resp = requests.post(main_server_loc+"/get_model",json.dumps(info))
        with open(model_path, 'wb') as f:
            f.write(resp.content)


    @sio.on("send_model")
    def send_model(self, service_name):
        model_path = model_dir+service_name+extension
        try:
            files = {service_name: open(model_path, 'rb')}
            info = {'service_name':service_name,'api_key':self.api_key}
            resp = requests.post(main_server_loc+"/sync",files=files)
        except Exception as e:
            print(e)
        