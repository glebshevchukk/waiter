from waiter import WaiterClient
import numpy as np

waiter = WaiterClient('http://localhost:5000/infer/resnet')
random_input = np.random.randint(low=0, high=255, size=(224, 224, 3), dtype=np.uint8)
result = waiter.inference(random_input)
print(result)