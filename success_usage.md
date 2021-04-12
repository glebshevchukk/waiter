Waiter has been successfully started using config from {{config_file}} you can now:            
1. Query any of the models from any other Python program on this computer or from another computer:
```
from waiter import WaiterClient
client = WaiterClient('{{computer_address}}/infer/{{unique_identifier}}/MODEL_NAME')
output = client.inference(...)
```
2. Run inference over an API by sending input data as a JSON to:
```
{{computer_address}}/infer/{{unique_identifier}}/MODEL_NAME
```
<!-- 3. Sync this model to another computer by running the following on the other computer:
```
from waiter import WaiterClient
client = WaiterClient('{{unique_identifier}}')
client.sync({{computer_address}}/waiter/sync/)
``` -->

<!-- 3. Visualize deployment statistics and logs at:
```
waiter.ai/viz/{{unique_identifier}}
``` -->