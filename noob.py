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

import sys
import asyncio
import websockets
import traceback

import bank

class Noob (bank.Bank):
    def __init__ (self):
        super () .__init__ (self.centralBankCode)
        
        self.print ('Central bank initiated')
        
        self.commandQueues = {}
        self.replyQueues = {}
        
        # Start socket creator (as opposed to server) and run it until complete, which is never
        serverFuture = websockets.serve (self.server, self.centralHostName, self.centralPortNr)
        asyncio.get_event_loop () .run_until_complete (serverFuture)
        
        # Prevent termination of event loop
        asyncio.get_event_loop () .run_forever ()
        
    def reportUnknownBankCode (self, bankCode):
        self.print (f'Error - Unknown bank code: {bankCode}')
        
    async def server (self, socket, path):
        '''
        Role communication handler
        - Called once for each master and once for each slave
        - Handles the socket belonging to the master or slave that it's called for
        - Remains looping for that master or slave until connection is closed
        - So several calls of this coroutine run concurrently, one per master and one per slave
        '''
        
        try:
            self.print (f'Instantiated socket: {socket}')
            role = 'uncommited'

            command, role, bankCode = await (self.recv (socket, role))
            if command == 'register':
                await self.send (socket, role, True)

                if role == 'master':
                    self.commandQueues [bankCode] = asyncio.Queue ()
                    while True:
                        # Receive command from own master
                        message = await self.recv (socket, role)
                        
                        # Put it in the queue belonging to the right slave
                        try:
                            await self.commandQueues [message [0]] .put ([bankCode] + message [1:])
                            
                            # Get reply of slave from own master queue and send it to master
                            # The master gives a command to only one slave at a time, so he knows who answered
                            await self.send (socket, role, await self.replyQueues [bankCode] .get ())                            
                        except KeyError:
                           self.reportUnknownBankCode (message [0])
                           await self.send (socket, role, False)                            
                        
                else:
                    self.replyQueues [bankCode] = asyncio.Queue ()
                    while True:
                        # Receive query from own slave
                        message = await self.recv (socket, role)
                        
                        # Wait until command in own slave queue
                        try:
                            message = await self.commandQueues [bankCode] .get ()
                        except KeyError:
                            self.reportUnknownBankCode (bankCode)
                        
                        # Send it to own slave
                        await self.send (socket, role, message [1:])
                                               
                        # Get reply from own slave and put it in the right reply queue
                        try:
                            await self.replyQueues [message [0]] .put (await self.recv (socket, role))
                        except:
                            self.reportUnknownBankCode (message [0])
            else:
                self.print (f'Error - Registration expected, got command: {command}')
                await socket.send (json.dumps (False), role)
                sys.exit (1)
        except:
            self.print (traceback.format_exc ())
            sys.exit (1)
              
noob = Noob ()

