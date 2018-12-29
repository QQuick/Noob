# Naieve Ontzettend Onveilige Bank

import asyncio
import websockets

async def server (websocket, path):
    name = await websocket.recv ()
    print (f"< {name}")

    greeting = f'Hello {name}!'

    await websocket.send (greeting)
    print (f'>{greeting}')

serverFuture = websockets.serve (server, 'localhost', 8765)
asyncio.get_event_loop () .run_until_complete (serverFuture)

asyncio.get_event_loop () .run_forever ()
