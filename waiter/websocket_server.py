from flask import Flask, render_template
from flask_socketio import SocketIO
import json
from collections import defaultdict

app = Flask("waiter_main")
app.config['SECRET_KEY'] = 'geronimo'
socketio = SocketIO(app)
cache = defaultdict(list)

@socketio.on('handshake')
def handle_handshake(data):
    info = json.loads(data)
    run_id = info['id']
    if run_id not in cache:
        cache[run_id] = []

@socketio.on('statistics')
def handle_statistics(data):
    stats = json.loads(data)
    if 'id' in stats:
        id = stats['id']
        cache[id].append(stats)

    
if __name__ == '__main__':
    socketio.run(app,port=3000)