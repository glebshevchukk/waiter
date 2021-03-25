from waiter import WaiterServer
from torchvision import transforms
import torch
from PIL import Image
import numpy as np

config_file = "../configs/localhost.yaml"
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

preprocessors = {'resnet':resnet18_preprocess}
waiter = WaiterServer(config_file=config_file, device=device, preprocessors=preprocessors)