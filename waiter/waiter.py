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
import onnxruntime as rt
from waiter.util import make_identifier, get_api_key, get_checksum, get_time_created, NumpyEncoder
import socketio

from timeit import default_timer as timer

extension = ".onnx"
model_dir = os.path.dirname(os.path.realpath(__file__)) + "/model_files/"
main_server_loc= 'http://127.0.0.1:5000'

class Waiter():

    def __init__(self):
        self.api_key = get_api_key()
        self.persistent_id = make_identifier()
        self.models = {}
        self.sio = socketio.Client()

    def setup(self):
        self.call_backs()
        self.sio.connect(main_server_loc)

    def loop(self): 
        self.sio.wait()

    def run(self,service_name=None,model_path=None):
        self.setup()
        self.serve(service_name,model_path)
        self.loop()

    def call_backs(self):
        @self.sio.event
        def run_inference(data):
            key = data['service_name']
            if key not in self.models:
                print("Model with that service name does not exist.")
                return

            inp = pickle.loads(data['input'])
            try:
                sess = rt.InferenceSession(self.models[key])
                input_name = sess.get_inputs()[0].name
                label_name = sess.get_outputs()[0].name
                output = sess.run([label_name], {input_name: inp.astype(np.float32)})[0]

                return_data = {'client_id':data['client_id'],'client_socket_id':data['client_socket_id'],'output':pickle.dumps(output)}
            
                self.sio.emit('send_result',return_data)
            except Exception as e:
                print(e)
                print(f"Error with performing inference on model {key}, returning None")
            

    def serve(self,service_name,model_path=None):
        #if a model isn't specified, we have to pull it from another server
        info = self.check_service(service_name)
        model_path = model_dir+service_name+extension

        if model_path == None:
            if not bool(info['exists']):
                print("That service does not exist anywhere. Please either sync or upload the model for it.")
            else:
                self.get_model(service_name)
                print(f"Service {service_name} has been successfully pulled and you can now use it. ")
        #if a model is specified, we just serve it
        else:
            #if it isn't the latest model, we should pull the latest one
            if bool(info['exists']) and not info['checksum'] == get_checksum(model_path):
                self.get_model(service_name)
                print(f"Service {service_name} has been successfully updated")
        self.broadcast_model(service_name)
        model_path = model_dir + service_name + extension
        self.models[service_name] = model_path
        
    def broadcast_model(self,service_name):
        model_path = model_dir+service_name+extension
        checksum = get_checksum(model_path)
        file_created = get_time_created(model_path)
        stats = {"service_name":service_name,\
                "server_id": self.persistent_id,
                "checksum":checksum,"file_created":file_created,\
                "api_key":self.api_key}
        self.sio.emit('broadcast_service', json.dumps(stats))

    def check_service(self,service_name):
        stats = {"api_key":self.api_key, "service_name":service_name,"server_id":self.persistent_id}
        resp_info = self.sio.call('service_exists',json.dumps(stats,cls=NumpyEncoder))
        return resp_info
       
    #These two use stock POST requests because they're dealing with presumably large files
    def get_model(self,service_name):
        model_path = model_dir+service_name+extension
        info = {'server_id':self.persistent_id,'api_key':self.api_key,'service_name':service_name}
        resp = requests.post(main_server_loc+"/api/v1/get_model",json=json.dumps(info))
        with open(model_path, 'wb') as f:
            f.write(resp.content)

    def send_model(self,service_name):
        model_path = model_dir+service_name+extension
        print(model_path)
        try:
            info = {'server_id':self.persistent_id,'service_name':service_name,'api_key':self.api_key}
            files = [
             ('model', (model_path, open(model_path, 'rb'))),
            ('data', ('data', json.dumps(info), 'application/json')),
            ]
            resp = requests.post(main_server_loc+"/api/v1/send_model",files=files)
        except Exception as e:
            print(e)
