import asyncio
import websockets
import json
import sys
import aioconsole

hostName = 'localhost'
portNr = 8765

serverUrl = f'ws://{hostName}:{portNr}'
    
class TestClient:       
    def __init__ (self, secondName):
        print ('Test client started')
        self.secondName = secondName
        clientCoroutineObject = self.client ()
        asyncio.run (clientCoroutineObject)
        
    async def client (self):
        async def runJohn ():
            counter = 0
            while True:
                answer = await aioconsole.ainput ('John says WHAT?')
                await self.johnSocket.send (json.dumps (f'counter john {self.secondName} is {counter} - {answer}'))
                print (f'john {self.secondName}:', json.loads (await self.johnSocket.recv ()))
                counter += 1

        async def runMary ():
            counter = 0
            while True:
                await asyncio.sleep (0.5)
                await self.marySocket.send (json.dumps (f'counter mary {self.secondName } is {counter}'))
                print (f'mary {self.secondName}:', json.loads (await self.marySocket.recv ()))
                counter -= 1

        async with websockets.connect (serverUrl) as self.johnSocket:
             print ('Connection mary accepted by test server')
             async with websockets.connect (serverUrl) as self.marySocket:
                print ('Connection john accepted by test server')
                await asyncio.gather (
                    runJohn (),
                    runMary ()                         
                )
 
TestClient (sys.argv [1])
    