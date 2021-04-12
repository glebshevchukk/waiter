Waiter is a small Python utility that makes it easier to call remote machine learning models. It lets you serve models previously exported to ONNX format, uses SocketIO to communicate between clients and servers, and uses a central server to coordinate jobs and sync models. 

Quickstart:

```
git clone https://github.com/glebshevchukk/waiter & cd waiter
pip install -e .
waiter register
```

Start up a server, assuming you have a ResNet model saved in 'resnet.onnx' in the current folder:

```
from waiter import WaiterServer
from torchvision import models

server = WaiterServer()
server.run('resnet','resnet.onnx')
```

On another computer, you can now log-in to the same Waiter account from the server:

```
waiter login
```

Now, you can now call the model from a Python client:
```
from waiter import WaiterClient

processed_input = ...
client = WaiterClient()
result = waiter.call_inference(processed,"resnet",blocking=True)
print(result)
```