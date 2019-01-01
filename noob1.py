''' NOOB: Naive Objectionably Opaque Bank

A.K.A. Naieve Ontzettend Onveilige Bank

The NOOB is a pure clearing house:

- It doesn't store anything
- It doesn't charge anything
- It doesn't check anything

To get acquainted with how it works,
start several instances if the consumer bank emulator (NOOC),
each with its own bank code and currency conversion rate.

Note that while the NOOB written in Python,
its clients may be written in any language,
as long as they speak JSON over WebSockets.

Clients are required to utilize the NOOB protocol.

It consists of following message types:

- ['connect', <bank code : string>]
- ['disconnect']

- ['open', <bank code : string> <account nr : string>, <pin : string>, <amount in euro's = 0 : float>]
- ['close', <bank code : string> <account nr : string>, <pin : string>, <amount in euro's = 0 : float>]

- ['deposit', <bank code : string> <account nr : string>, <pin : string>, <amount in euro's : float>]
- ['withdraw', <bank code : string> <account nr : string>, <pin : string>, <amount in euro's : float>]

Possible replies are:

- True (meaning success)
- False (meaning failure)

Happy banking!
'''

import asyncio
import websockets
import json
import traceback

import noob_connection_data

debug = True

class Noob:
    def __init__ (self):
        self.print ('Central bank initiated')
        self.commandQueues = {}
        self.replyQueues = {}
        
        # Start socket creator (as opposed to server) and run it until complete, which is never
        serverFuture = websockets.serve (self.server, noob_connection_data.hostName, noob_connection_data.portNr)
        asyncio.get_event_loop () .run_until_complete (serverFuture)
        
        # Prevent termination of event loop
        asyncio.get_event_loop () .run_forever ()
        
    def print (self, *args):
        if debug:
            print ('NOOB -', *args)
            
    async def send (self, socket, message):
        self.print (f'Sent: {message}')
        return await socket.send (json.dumps (message))
        
    async def recv (self, socket):
        message = json.loads (await socket.recv ())
        self.print (f'Received: {message}')
        return message
        
    async def server (self, socket, path):
        '''
        Role communication handler
        - Called once for each master and once for each slave
        - Handles the socket belonging to the master or slave that it's called for
        - Remains looping for that master or slave until connection is closed
        - So several calls of this coroutine run concurrently, one per master and one per slave
        '''
        self.print (f'Instantiated socket: {socket}')
        try:
            command, role, bankCode = await (self.recv (socket))
            
            if command == 'register':
                await self.send (socket, True)

                if role == 'master':
                    self.commandQueues [bankCode] = asyncio.Queue ()
                    while True:
                        # Receive command from own master
                        message = await self.recv (socket)
                        
                        # Put it in the queue belonging to the right slave
                        await self.commandQueues [message [0]] .put ([bankCode] + message [1:])
                        
                        # Get reply of slave from own master queue and send it to master
                        # The master gives a command to only one slave at a time, so he knows who answered
                        await self.send (socket, await self.replyQueues [bankCode] .get ())
                else:
                    self.replyQueues [bankCode] = asyncio.Queue ()
                    while True:
                        # Receive query from own slave
                        message = await self.recv (socket)
                        
                        # Wait until command in own slave queue
                        message = await self.commandQueues [bankCode] .get ()
                        
                        # Send it to own slave
                        await self.send (socket, message [1:])
                                               
                        # Get reply from own slave and put it in the right reply queue
                        await self.replyQueues [message [0]] .put (await self.recv (socket))    
   
            else:
                self.print (f'Error: register command expected')
                await socket.send (json.dumps (False))
                exit (1)
        except:
            print (traceback.format_exc ())
            exit (1)
              
noob = Noob ()

