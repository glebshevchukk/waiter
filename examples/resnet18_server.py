from waiter.waiter import Waiter
from torchvision import transforms, models
import torch
from PIL import Image
import numpy as np
import os
import sys

config_file = os.path.join(sys.path[0],"localhost.yaml")
device = torch.device("cpu")
resnet18 = models.resnet18()

waiter = Waiter('http://localhost:5000')
#waiter.use_model('resnet',resnet18)

waiter.serve('resnet','./resnet.onnx')
