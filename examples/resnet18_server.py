from waiter.waiter import Waiter
from torchvision import transforms, models
import torch
from PIL import Image
import numpy as np
import os
import sys

config_file = os.path.join(sys.path[0],"localhost.yaml")
device = torch.device("cpu")

image_compose = transforms.Compose([
    transforms.Resize(256),
    transforms.CenterCrop(224),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
])
def resnet18_preprocess(inp):
    inp = inp.astype(np.uint8)
    inp = Image.fromarray(inp)
    inp = image_compose(inp)
    if len(inp.shape) != 4:
        inp = inp.unsqueeze(0)
    return inp

model = models.resnet18()

model_name = 'resnet'
waiter = Waiter(connection_point='http://localhost:5000')
waiter.send_model(model_name,model)
