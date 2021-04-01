from flask import Flask, Response, jsonify, request

import json
import numpy as np
import pickle
import onnxruntime as rt
from werkzeug.utils import secure_filename
import os, time
from util import NumpyEncoder

app = Flask('waiter')
app.config['SECRET_KEY'] = 'geronimo'

models = {}

def add_model(model_name,model_file):
    models[model_name] = model_file

def do_inference(key,msg):
    if key not in models:
        return {"msg":"That model does not exist."}
    inp = np.array(json.loads(msg.json))
    try:
        sess = rt.InferenceSession(model_path+models[key])
        input_name = sess.get_inputs()[0].name
        output = sess.run(None, {input_name: inp.astype(np.float32)})[0]
        return json.dumps(output, cls=NumpyEncoder)
    except Exception as e:
        print(e)
        print(f"Error with performing inference on model {key}, returning None")
        return None

@app.route('/infer/<model>',methods=["POST"])
def infer(model):
    if request.method == 'POST':
        return do_inference(model,request)


def run_app():
    app.run()
