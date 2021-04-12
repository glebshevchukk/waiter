'''
Main class for running Waiter server that can:
1) Perform remote inference
2) Sync models with other servers
'''

#For doing requests
import requests
import numpy as np
import json, os, sys
import socketio
import pickle

#For doing inference
import torch.onnx
import onnxruntime as rt
from waiter.util import make_identifier, get_api_key, get_checksum, get_time_created, NumpyEncoder


EXTENSION = ".onnx"
MODEL_DIR = os.path.dirname(os.path.realpath(__file__)) + "/model_files/"
SERVER_ADDRESS= 'http://127.0.0.1:5000'

class Waiter(object):

    def __init__(self):
        self.api_key = get_api_key()
        self.persistent_id = make_identifier()
        self.models = {}
        self.sio = socketio.Client()

    def setup(self):
        self.call_backs()
        self.sio.connect(SERVER_ADDRESS)

    def loop(self): 
        self.sio.wait()

    def run(self,service_name:str=None,model_path:str=None)->None:
        self.setup()
        self.serve(service_name,model_path)
        self.loop()

    def call_backs(self):
        @self.sio.event
        def run_inference(data):
            key = data['service_name']
            if key not in self.models:
                return_data = {'error':"Model with that service name does not exist."}
                self.sio.emit('send_result',return_data)
            else:
                inp = pickle.loads(data['input'])
                try:
                    sess = rt.InferenceSession(self.models[key])
                    input_name = sess.get_inputs()[0].name
                    label_name = sess.get_outputs()[0].name
                    output = sess.run([label_name], {input_name: inp.astype(np.float32)})[0]
                    return_data = {'client_id':data['client_id'],'client_socket_id':data['client_socket_id'],'output':pickle.dumps(output)}
    
                    self.sio.emit('send_result',return_data)
                except Exception as e:
                    return_data = {'error':e}
                    self.sio.emit('send_result',return_data)
            

    def serve(self,service_name:str,model_path:str=None)->None:
        #if a model isn't specified, we have to pull it from another server
        info = self.check_service(service_name)
        model_path = MODEL_DIR+service_name+EXTENSION

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
        model_path = MODEL_DIR + service_name + EXTENSION
        self.models[service_name] = model_path
        
    def broadcast_model(self,service_name:str)->None:
        model_path = MODEL_DIR+service_name+EXTENSION
        checksum = get_checksum(model_path)
        file_created = get_time_created(model_path)
        stats = {"service_name":service_name,\
                "server_id": self.persistent_id,
                "checksum":checksum,"file_created":file_created,\
                "api_key":self.api_key}
        self.sio.emit('broadcast_service', json.dumps(stats))

    def check_service(self,service_name:str)->dict:
        stats = {"api_key":self.api_key, "service_name":service_name,"server_id":self.persistent_id}
        resp_info = self.sio.call('service_exists',json.dumps(stats,cls=NumpyEncoder))
        return resp_info
       
    #These two use stock POST requests because they're dealing with presumably large files
    def get_model(self,service_name:str)->bool:
        model_path = MODEL_DIR+service_name+EXTENSION
        info = {'server_id':self.persistent_id,'api_key':self.api_key,'service_name':service_name}
        try:
            resp = requests.post(SERVER_ADDRESS+"/api/v1/get_model",json=json.dumps(info))
            with open(model_path, 'wb') as f:
                f.write(resp.content)
        except Exception as e:
            print(e)
            return False

    def send_model(self,service_name:str)->bool:
        model_path = MODEL_DIR+service_name+EXTENSION
        try:
            info = {'server_id':self.persistent_id,'service_name':service_name,'api_key':self.api_key}
            files = [
             ('model', (model_path, open(model_path, 'rb'))),
            ('data', ('data', json.dumps(info), 'application/json')),
            ]
            resp = requests.post(SERVER_ADDRESS+"/api/v1/send_model",files=files)
            return True
        except Exception as e:
            print(e)
            return False
