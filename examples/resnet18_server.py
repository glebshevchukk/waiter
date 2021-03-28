from waiter.waiter import Waiter
from torchvision import transforms, models
import torch
from PIL import Image
import numpy as np
import os
import sys

config_file = os.path.join(sys.path[0],"localhost.yaml")
device = torch.device("cpu")
model = models.resnet18()

model_name = 'resnet'
waiter = Waiter(connection_point='http://localhost:5000')
waiter.send_model(model_name,model)
