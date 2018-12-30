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
-  ['withdraw', <bank code : string> <account nr : string>, <pin : string>, <amount in euro's : float>]

Happy banking!
'''

import asyncio
import websockets

import noob_connection_data

class Noob:
    def __init__ (self):
        serverFuture = websockets.serve (self.server, noob_connection_data.hostName, noob_connection_data.portNr)
        asyncio.get_event_loop () .run_until_complete (serverFuture)
        
        asyncio.get_event_loop () .run_forever ()
        
    async def server (self):
              
noob = Noob ()

