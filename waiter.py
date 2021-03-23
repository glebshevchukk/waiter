import torch
from zmq_service import ServiceServer
import uuid
from termcolor import colored

from rich.console import Console
from rich.markdown import Markdown
import hruid
import yaml

def make_identifier():
    generator = hruid.Generator()
    phrase = generator.random()
    return phrase


class Waiter(object):
    def __init__(self,model,checkpoint_path,config_file):
        self.config_file = config_file
        with open(config_file, 'r') as stream:
            self.config = yaml.safe_load(stream)
        self.checkpoint_path = checkpoint_path
        self.service_name = make_identifier()
        self.display_success()
        self.load_model(checkpoint_path)
        self.zmq_server = ServiceServer(db,self.do_inference,self.unique_identifier)
        self.model = model

    def load_model(self,checkpoint_path):
        self.model.load_state_dict(torch.load(checkpoint_path))
        self.model.eval()

    def do_inference(self,inp):
        return self.model(inp)
    
    def display_success(self):
        console = Console()
        with open('success_usage.md') as md:
            text = md.read()
            text = text.replace('{{config_file}}', self.config_file)
            text = text.replace('{{unique_identifier}}', self.service_name)
            text = text.replace('{{computer_address}}', self.config['computer_address'])
            markdown = Markdown(text)
            console.print(markdown)
        console.print("Waiter is running now.", style="bold green")

if __name__ == "__main__":
    config_file = "configs/localhost.yaml"
    waiter = Waiter(model=None,checkpoint_path='test.pyt',config_file=config_file)