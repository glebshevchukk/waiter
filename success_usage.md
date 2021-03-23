Waiter has been successfully started using config from {{config_file}} you can now:            
1. Query this model from any other Python program on this computer:
```
from waiter import WaiterClient
client = WaiterClient('{{unique_identifier}}')
output = client.inference(...)
```
2. Run inference over an API by sending input data as a JSON to:
```
{{computer_address}}/waiter/infer/{{unique_identifier}}
```
3. Call this model from another computer by running the following on the other computer:
```
from waiter import WaiterClient
client = WaiterClient()
client.use({{computer_address}}/waiter/infer/{{unique_identifier}})
output = client.inference(...)
```
<!-- 3. Sync this model to another computer by running the following on the other computer:
```
from waiter import WaiterClient
client = WaiterClient('{{unique_identifier}}')
client.sync({{computer_address}}/waiter/sync/)
``` -->

4. Visualize deployment statistics and logs at:
```
waiter.ai/viz/{{unique_identifier}}
```