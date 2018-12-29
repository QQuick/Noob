# Naieve Ontzettend Onveilige Client

import sys
import asyncio
import websockets

serverUrl = 'ws://localhost:8765'

id = sys.argv [1]

async def client ():
    while True:
        async with websockets.connect (serverUrl) as websocket:
            name = input ('What\'s your name? ')

            await websocket.send (f'{id} ' + name)
            print(f'>:{id} {name}')

            greeting = await websocket.recv ()
            print(f'<{greeting}')
 
clientCoroutineObject = client ()
asyncio.run (clientCoroutineObject)
