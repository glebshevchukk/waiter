from waiter.waiter import Waiter
import numpy as np

waiter = Waiter('http://localhost:5000')
random_input = np.random.randint(low=0, high=255, size=(1,3,224, 224), dtype=np.uint8)
result = waiter.inference(random_input,"resnet")
print(result)