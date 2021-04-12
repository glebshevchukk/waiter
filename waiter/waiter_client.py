'''
Client runner file that lets us send remote requests over to
the inference server over SocketIO.
'''
import requests
import numpy as np
import json, os, sys
import pickle
from waiter.util import make_identifier, get_api_key, get_checksum, get_time_created, NumpyEncoder

import socketio
from queue import Queue
import uuid

SERVER_ADDRESS= 'http://localhost:5000'

class WaiterClient(object):
    def __init__(self):
        self.api_key = get_api_key()
        self.persistent_id = make_identifier()
        self.sio = socketio.Client()
        self.call_backs()
        self.sio.connect(SERVER_ADDRESS)
        self.result = Queue()

    def call_backs(self):
        @self.sio.event
        def return_result(data):
            d = pickle.loads(data['output'])
            self.result.put(d)

    def call_inference(self,numpy_input:np.ndarray,service_name:str,blocking:bool=True)->dict|str:
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

    def check_service(self,service_name:str)->dict:
        stats = {"api_key":self.api_key, "service_name":service_name,"server_id":self.persistent_id}
        resp_info = self.sio.call('service_exists',json.dumps(stats,cls=NumpyEncoder))
        return resp_info
