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
        self.slaveSockets = {}
        
        # Start socket creator (as opposed to server) and run it until complete, which is never
        serverFuture = websockets.serve (self.server, noob_connection_data.hostName, noob_connection_data.portNr)
        asyncio.get_event_loop () .run_until_complete (serverFuture)
        
        # Prevent termination of event loop
        asyncio.get_event_loop () .run_forever ()
        
    def print (self, *args):
        if debug:
            print ('NOOB -', *args)

    async def server (self, socket, path):
        ''' Called once for each master or slave
        '''
        self.print ('Server function entered')
        try:
            command, role, bankCode = json.loads (await socket.recv ())
            self.print (f'Received command: {command} {role} {bankCode}')
            if command == 'register':
                await socket.send (json.dumps (True))
                if role == 'slave':
                    self.slaveSockets [bankCode] = socket
                    self.print (f'Slave sockets: {self.slaveSockets}')
                else:
                    while True:
                        bankCode, command, accountNr, pin, amount = json.loads (await socket.recv ()) #############
                        await self.slaveSockets [bankCode] .send (json.dumps ([command, accounNr, pin, amount]))
                        await socket.send (await self.slaveSockets [bankCode] .recv ()) # skip dumps and loads, since they cancel out
            else:
                self.print (f'Unexpected command {command} from {role} {bankCode} instead of registration')
                await socket.send (json.dumps (False))
                return
        except:
            print (traceback.format_exc ())
            exit (1)
              
noob = Noob ()

