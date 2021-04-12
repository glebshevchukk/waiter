from waiter.waiter import Waiter
from torchvision import transforms, models
import torch
from PIL import Image
import numpy as np
import os
import sys

device = torch.device("cpu")
resnet18 = models.resnet18()

waiter = Waiter()
waiter.get_model('resnet')
#waiter.run('resnet','resnet.onnx')