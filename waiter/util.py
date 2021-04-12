'''
Util file containing useful helpers for keeping track of identification, etc.
'''

from termcolor import colored
from rich.console import Console
from rich.markdown import Markdown
import hruid, uuid
import os, sys, uuid, json, yaml
import numpy as np
import hashlib
import datetime

class NumpyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        return json.JSONEncoder.default(self, obj)

def make_identifier()->str:
    '''This identifier should stay the same for each computer'''
    return str(uuid.UUID(int=uuid.getnode()))

def display_success(self):
    console = Console()
    with open(os.path.join(sys.path[0],'success_usage.md')) as md:
        text = md.read()
        text = text.replace('{{config_file}}', self.config_file)
        text = text.replace('{{unique_identifier}}', self.service_name)
        text = text.replace('{{computer_address}}', self.config['computer_address'])
        markdown = Markdown(text)
        console.print(markdown)
    console.print("Waiter is running now.", style="bold green")

def get_api_key()->str:
    with open(os.path.dirname(os.path.realpath(__file__))+"/.WAITER","r") as f:
        return str(f.readline())

def get_checksum(model_file:str)->str:
    with open(model_file, "rb") as f:
        file_hash = hashlib.blake2b()
        while chunk := f.read(8192):
            file_hash.update(chunk)
    return file_hash.hexdigest()

def get_time_created(file:str)->float:
    dt=os.path.getmtime(file)
    return dt