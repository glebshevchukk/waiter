from waiter.waiter_client import WaiterClient
import numpy as np
from torchvision import transforms, models
from PIL import Image

waiter = WaiterClient()
random_input = np.random.randint(low=0, high=255, size=(224, 224,3), dtype=np.uint8)

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
    return inp.numpy()

processed = resnet18_preprocess(random_input)
result = waiter.call_inference(processed,"resnet")