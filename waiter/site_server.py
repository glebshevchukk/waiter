import websockets
import asyncio
import jsonpickle

async def send_statistics(websocket, path,sleep_time=5):
    while True:
        try:
            data = sub.single_subscribe(topics)
            data = jsonpickle.encode(data)
            
            await websocket.send(data)
            time.sleep(sleep_time)
        except websockets.ConnectionClosed:
            print("Connection to client closed.")
            return

start_server = websockets.serve(send_statistics, "localhost", 3000)

asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()