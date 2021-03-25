import jsonpickle
import zmq
import time

class ServiceServer(object):
    def __init__(self,db,callback,service_name,service_key="service_list"):
        self.db = db
        self.callback=callback
        self.service_name=service_name
        self.service_key = service_key
        
        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.REP)
        self.port = self.socket.bind_to_random_port("tcp://*")
        self.make_service(service_name,self.port)
        
    def handle_requests(self):
        string = self.socket.recv()
        string= string.decode('utf-8')
        
        msg = jsonpickle.decode(string)
        returned_msg = self.callback(msg)
        returned_msg = jsonpickle.encode(returned_msg)
        self.socket.send_string(returned_msg)

    def make_service(self,service,port):
        self.db.hset(self.service_key, service, port)
        refresh_services(self.db,self.service_key)


class ServiceClient(object):
    def __init__(self,service_name,db,service_key="service_list"):
        self.service_name=service_name
        self.db=db
        self.service_key=service_key
        self.services=refresh_services(self.db,self.service_key)
        self.context = zmq.Context()
        self.refresh_socket()

    def refresh_socket(self):
        self.socket = self.context.socket(zmq.REQ)
        if self.service_name not in self.services:
            print("That service has not been started yet.")
            return
        self.port = int(self.services[self.service_name])
        self.socket.connect("tcp://127.0.0.1:%s"% self.port)
        refresh_services(self.db,self.service_key)
        
    def call(self,callback):
        self.refresh_socket()
        msg = callback()
        msg = jsonpickle.encode(msg)
        self.socket.send_string(msg)
        string = self.socket.recv()
        string= string.decode('utf-8')
        msg = jsonpickle.decode(string)
        return msg


def refresh_services(db,key):
    if db and key and db.exists(key):
        redis_dic = db.hgetall(key)
        dic={}
        for key,val in redis_dic.items():
            key = key.decode('utf-8')
            val = int(val.decode('utf-8'))
            dic[key] = val
        return dic
    return None

    