from flask import Flask, Response, jsonify, request
import json
import numpy as np
import pickle
import onnxruntime as rt
from werkzeug.utils import secure_filename
import os
from util import NumpyEncoder

app = Flask('waiter')
models = {}
model_path = "./model_files/"

for p in os.listdir(model_path):
    k = p[:p.find('-')]
    models[k] = p

def do_inference(key,msg):
    print(models)
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

@app.route('/sync',methods=["POST"])
def sync():
    if request.method == 'POST':
        #TODO: Add extra verification against tampering
        info = request.files
        
        for model in info.keys():
            f = info[model]
            f.save(model_path+secure_filename(f.filename))   
            models[model] = f.filename     
    return {"msg": "Sync successful."}


@app.route('/infer/<model>',methods=["POST"])
def infer(model):
    if request.method == 'POST':
        return do_inference(model,request)

if __name__ == "__main__":  
    app.run(host='0.0.0.0')
