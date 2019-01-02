import json
import aioconsole

class Bank:
    show = True

    centralHostName = 'localhost'
    centralPortNr = 8765
    centralBankCode = 'noob'
        
    def __init__ (self, bankCode):
        self.bankCode = bankCode
    
    def print (self, *args, end = '\n', show = True):
        if self.show and show:
            print (f'{self.bankCode.upper ()} -', *args, end = end, flush = True)
            
    async def input (self, *args):
        self.print (*args, end = '')
        return (await aioconsole.ainput ('')) .lower ()
            
    async def send (self, socket, role, message, show = True):
        self.print (f'Sent {role}: {message}', show = show)
        return await socket.send (json.dumps (message))
        
    async def recv (self, socket, role, show = True):
        message = json.loads (await socket.recv ())
        self.print (f'Received {role}: {message}', show = show)
        return message
