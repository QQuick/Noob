import asyncio
import websockets
import json

hostName = 'localhost'
portNr = 8765

class TestServer:
    def __init__ (self):
        print ('Test server started')   
        self.slaveSockets = {}
        
        # Start socket creator (as opposed to server) and run it until complete, which is never
        serverFuture = websockets.serve (self.server, hostName, portNr)
        asyncio.get_event_loop () .run_until_complete (serverFuture)
        
        # Prevent termination of event loop
        asyncio.get_event_loop () .run_forever ()
        
    # Called once for each johnSocket or marySocket
    async def server (self, socket, path):
        print ('Server function entered')
        
        while True:
            message = json.loads (await socket.recv ())
            if message == 'quit':
                break
            await socket.send (json.dumps (f'echo - {message}'))
          
testServer = TestServer ()

