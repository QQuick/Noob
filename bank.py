import json
import aioconsole

class Bank:
    show = True
    local = True

    centralHostName = 'localhost' if local else '192.168.2.1'
    centralPortNr = 6666
    centralBankCode = 'noob'
        
    def __init__ (self, bankCode):
        self.bankCode = bankCode
    
    def print (self, *args, end = '\n', show = True):
        if self.show and show:
            print (f'{self.bankCode.upper ()} -', *args, end = end, flush = True)
            
    async def input (self, *args):
        if args:
            self.print (*args, end = '')
        return (await aioconsole.ainput ('')) .lower ()
            
    async def send (self, socket, role, message, show = True):
        self.print (f'Sent {role}: {message}', show = show)
        return await socket.send (json.dumps (message))
        
    async def recv (self, socket, role, show = True):
        message = json.loads (await socket.recv ())
        self.print (f'Received {role}: {message}', show = show)
        return message
            
    def match (self, commandStart, *commandSet):
        for command in commandSet:
            if command.startswith (commandStart):
                return True
        else:
            return False
