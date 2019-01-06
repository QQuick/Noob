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

Clients are required to utilize the NOOB protocol:

Master role
===========
Remotely opening an ABNA account from bank INGB happens by sending to the NOOB:
	["ABNA", "open", 300400, 1234, 0]
    
Remotely closing this ABNA account from bank INGB happens by sending to the NOOB:
	["ABNA", "close", 300400, 1234, 0]
    
Deposing 1000 local coins on this ABNA account from bank INGB happens by sending to the NOOB:
	["ABNA", "deposit", 300400, 1234, 1000]
    
Withdrawing 199.50 local coins from this ABNA account from bank INGB happens by sending to the NOOB:
	["ABNA", "withdraw", 300400, 1234, 199.50]
    
The hack command allows inspecting all local accounts on a NOOC.

Slave role
==========
All commands received by the slave are the same as the ones sent by the master, only with the first (bank code) parameter omitted.

Replies
=======
All commands for both roles are replied upon:
	[True] means succes, [False] means failure.
    

Happy banking!
'''

import sys
import asyncio
import websockets
import traceback

import bank

class Noob (bank.Bank):
    class RegistrationError (Exception):
        pass

    def __init__ (self):
        super () .__init__ (self.centralBankCode)
        
        self.print ('Central bank initiated (type q(uit) to exit)')
        
        # Create message queues
        self.commandQueues = {}
        self.replyQueues = {}
        
        # Start servers creator (as opposed to server) and run it until complete, which is never
        serverFuture = websockets.serve (self.roleServer, self.centralHostName, self.centralPortNr)
        asyncio.get_event_loop () .run_until_complete (serverFuture)
        
        # Start command interpreter
        asyncio.get_event_loop () .run_until_complete (self.commandInterpreter ())
        
        # Prevent termination of event loop, since role servers subscribed to it
        asyncio.get_event_loop () .run_forever ()
    
    async def commandInterpreter (self):
        while True:
            command = await self.input ()
            if self.match (command, 'quit'):
                exit (0)
                
    def reportUnknownBankCode (self, bankCode):
        self.print (f'Error - Unknown bank code: {bankCode}')
        
    async def roleServer (self, socket, path):
        '''
        Role communication handler
        - Called once for each master and once for each slave
        - Handles the socket belonging to the master or slave that it's called for
        - Remains looping for that master or slave until connection is closed
        - So several calls of this coroutine run concurrently, one per master and one per slave
        '''
        
        try:
            self.print (f'Instantiated socket: {socket}')

            command, role, bankCode = None, None, None
            command, role, bankCode = await (self.recv (socket, role))
            
            if command == 'register':
                await self.send (socket, role, True)

                if role == 'master':
                    self.commandQueues [bankCode] = asyncio.Queue ()    # This will also replace an abandoned queue by an empty one
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
                    self.replyQueues [bankCode] = asyncio.Queue ()      # This will also replace an abandoned queue by an empty one
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
                raise self.RegistrationError ()
        except self.RegistrationError:
            try:
                await socket.send (json.dumps (False), role)            # Try to notify client
            except:
                pass                                                    # Escape if client closed connection
                
            self.print (f'Error: registration expected, got command: {command}')
        except websockets.exceptions.ConnectionClosed:
            self.print (f'Error: connection closed by {bankCode} as {role}')
        except Exception:
            self.print (f'Error: in serving {bankCode} as {role}\n{traceback.format_exc ()}')
              
noob = Noob ()

