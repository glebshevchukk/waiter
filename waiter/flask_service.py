from flask import Flask, Response, jsonify, request


class EndpointAction(object):

    def __init__(self, model,action):
        self.model = model
        self.action = action

    def __call__(self, *args):
        output = self.action(self.model,request) 
        return jsonify(output)


class FlaskAppWrapper(object):
    app = None
    def __init__(self, name):
        self.app = Flask(name)

    def run(self):
        self.app.run()

    def add_endpoint(self, model=None, endpoint=None, endpoint_name=None, handler=None):
        self.app.add_url_rule(endpoint, endpoint_name, EndpointAction(model,handler),methods=["POST"])