''' NOOB: Naive Objectionably Opaque Bank

A.K.A. Naieve Ontzettend Onveilige Bank

The NOOB is a pure clearing house:

- It doesn't store anything
- It doesn't charge anything
- It doesn't check anything

To get acquainted with how it works,
start several instances if the consumer bank emulator,
each with its own bank code and currency conversion rate.

Note that while it's written in Python,
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

import noob_connection_data

debug = True

def debugPrint (*args):
    if debug:
        print (args)

class Noob:
    def __init__ (self):
        clientSockets = {}
        
        # Wait for connection request and call server on a fresh socket if it occurs
        serverFuture = websockets.serve (self.server, noob_connection_data.hostName, noob_connection_data.portNr)
        asyncio.get_event_loop () .run_until_complete (serverFuture)
        
        # Prevent termination of program
        asyncio.get_event_loop () .run_forever ()
        
    async def server (self, socket, path):
        command, role, bankCode = await socket.recv ()
        if command == 'register':
            if not bankCode in clientSockets:
                clientSockets [bankCode] = {}
                
            if role in {'master', 'slave'}:
                if role in clientSockets [bankCode]:
                    debugPrint (f'Duplicate registration declined from {role} {bankCode}'*)
                    await socket.send (json.dumps (False)
                else:            
                    debugPrint (f'Registration accepted from {role} {bankCode}')
                    clientSockets [bankCode][role] = socket
                    await socket.send (json.dumps (True))
            else:
                debugPrint (f'Unknown role {role} for {bankCode}')
                await socket.send (json.dumps (False)  
        else:
            debugPrint (f'Unexpected command {command} from {role} {bankCode} instead of registration')
            await socket.send (json.dumps (False))
            return
            
        if role == 'master':
            while True:
                bankCode, command, accountNr, pin, amount = json.loads (await socket.recv ())
                await slaveSockets [bankCode] .send (json.dumps ([command, accounNr, pin, amount]))
                await socket.send (await slaveSocket [bankCode] .recv ()) # Skip decoding and recoding, since they cancel out
              
noob = Noob ()

