import torch
import uuid
from termcolor import colored

from rich.console import Console
from rich.markdown import Markdown
import hruid
import yaml

from waiter.flask_service import FlaskAppWrapper
from flask import jsonify
import torchvision.models as models
from urllib.parse import urlparse
from pydoc import locate

import requests
import numpy as np
import json

from torchvision import transforms
from PIL import Image

class NumpyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        return json.JSONEncoder.default(self, obj)

def is_url(url):
  try:
    result = urlparse(url)
    return all([result.scheme, result.netloc])
  except ValueError:
    return False

def make_identifier():
    generator = hruid.Generator()
    phrase = generator.random()
    return phrase

def load_model(model, checkpoint_path, device):
    model.load_state_dict(torch.load(checkpoint_path))
    model.eval()
    model = model.to(device)
    return model

def parse_models(models,device):
    all_models = {}
    for model in models:
        model_dic = model['model']
        try: 
            loaded = locate(model_dic['class'])
        except:
            print(f"Could not locate a class named {model_dic['class']}, skipping.")
            continue
        loaded_inst = loaded()
        if model_dic['checkpoint_path']:
            loaded_inst = load_model(loaded_inst,model_dic['checkpoint_path'], device)
        all_models[model_dic['name']] = loaded_inst
    return all_models


class WaiterServer(object):
    def __init__(self,config_file,device,preprocessors):
        self.config_file = config_file
        self.device = device
        self.preprocessors = preprocessors

        with open(config_file, 'r') as stream:
            self.config = yaml.safe_load(stream)
  
        self.service_name = make_identifier()
        self.models = parse_models(self.config['models'], device)
        self.display_success()
        self.start_web_server()

    def start_web_server(self):
        a = FlaskAppWrapper('waiter')
        for model in self.models.keys():
            url_path = 'infer/'+model 
            #url_path = 'infer/'+self.service_name+"/"+model 
            a.add_endpoint(model=model,endpoint='/' + url_path, endpoint_name=url_path, handler=self.do_inference)
        a.run()

    def do_inference(self,key,msg,input_type='long'):
        if key not in self.models:
            return "That model does not exist."
        inp = np.array(json.loads(msg.json))
        if self.preprocessors[key]:
            inp = self.preprocessors[key](inp)
        try:
            output = self.models[key](inp)
            output = output.detach().numpy()
            return json.dumps(output, cls=NumpyEncoder)
        except Exception as e:
            print(e)
            print(f"Error with performing inference on model {key}, returning None")
            return None
    
    def display_success(self):
        console = Console()
        with open('/Users/glebshevchuk/dev/waiter/success_usage.md') as md:
            text = md.read()
            text = text.replace('{{config_file}}', self.config_file)
            text = text.replace('{{unique_identifier}}', self.service_name)
            text = text.replace('{{computer_address}}', self.config['computer_address'])
            markdown = Markdown(text)
            console.print(markdown)
        console.print("Waiter is running now.", style="bold green")

class WaiterClient(object):
    def __init__(self,connection_point=None):
        self.connection_point = connection_point
    
    def inference(self,numpy_input):
        try:
            resp = requests.post(self.connection_point,json=json.dumps(numpy_input, cls=NumpyEncoder))
 
            json_as_np = np.array(json.loads(resp.json()))
            return json_as_np
        except Exception as e:
            print(e)
            return None
