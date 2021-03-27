from termcolor import colored

from rich.console import Console
from rich.markdown import Markdown
import hruid
import os, sys, uuid, json, yaml
import numpy as np

class NumpyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        return json.JSONEncoder.default(self, obj)

def make_identifier():
    generator = hruid.Generator()
    phrase = generator.random()
    return phrase

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