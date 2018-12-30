import sys
import asyncio
import websockets
import aioconsole
import json

import noob_connection_data

centralBankUrl == f'ws://{noob_connection_data.hostName}:{noob_connection_data.portNr}'
    
class Account:
    def __init__ (self, pin):
        self.pin = pin
        self.balance = 0
        
class ConsumerBank:
    def __init__ (self, bankCode, valueOfLocalCoinInEuros):
        print ('\nConsumer bank emulator initiated\n')
    
        self.bankCode = bankCode
        self.valueOfLocalCoinInEuros = valueOfLocalCoinInEuros  # All communication with central bank done in Euros
        accounts = {}
        clientCoroutineObject = self.client ()
        asyncio.run (clientCoroutineObject)

    async def client (self):
        ''' Initiates master and slave connections
        - The master connection is used to perform locally requested transactions on a remote bank
        - The slave connection is used to perform remotely requested transactions on the local bank
        '''
        while True:
            await asyncio.gather (
                async with websockets.connect (centralBankUrl) as self.masterSocket:
                    while True:
                        await (masterSocket.send (json.dumps ('[connect', self.bankCode]))
                        if json.loads (await self.masterSocket.recv ()):
                            print ('NOOB declined master connection')
                        else:
                            print ('NOOB accepted master connection')
                            await issueCommandFromLocal (self)
                            
                async with websockets.connect (centralBankUrl) as self.slaveSocket:
                    while True:
                        await (self.slaveSocket.send (self.bankCode)
                        if json.loads (await self.slaveSocket.recv ()):
                            print ('NOOB declined slave connection')
                        else:
                            print ('NOOB accepted slave connection')
                            await issueCommandFromRemote (self)                            
            )
            
    async def issueCommandFromLocal (self):
        ''' Obtains a command from the console and issues and execution order
        - If the bankcode matches the local bank, the order is executed locally
        - If the bankcode doesn't match this local bank, the order is executed remotely
        '''
        command = await aioconsole.ainput ('Open, close, deposit, withdraw or quit: ') .lower ()
        
        if command in {'open', 'close', 'deposit', 'withdraw'}:
            # --- Get user input
            
            message.pin = await aioconsole.ainput ('Pin: ')  
            print ('\n' * 256)  # Simplicity preferred over security in this demo
            
            message.bankCode = await aioconsole.ainput ('Bank code: (enter=this)') .lower ()
            if not message.bankCode:
                message.bankCode = self.bankCode
                print (f'Bankcode {bankCode} assumed')
                
            message.accountNr = await aioconsole.ainput ('Account number') .lower ()
            
            if command in {'open', 'close'}:
                amount = 0
            else:
                amount = float (await aioconsole.ainput ('Amount: '))
               
            # --- Allow user to verify input, except pincode
            
            print (f'Command: {command}')
            print (f'Bank code: {bankCode}')
            print (f'Account nr: {accountNr}')
            
            if command in {'open', 'close'}:
                print (f'Amount: {amount}')
                
            mistake = await aioconsole.input ('Correct (yes / no)') .lower () != 'yes'  # Stay on the safe side
            
            if mistake:
                print ('Transaction broken off')
                continue
            
            # --- Issue command for local or remote execution
            
            if bankCode == self.bankCode:
                print ('Success' if self.executeCommandLocally (command, accountNr, pin, amount) else 'Failure')
            else:
                print ('Success' if await self.executeCommandRemotely (bankCode, command, accountNr, pin, amount) else 'Failure')
                
        elif command == 'quit':
            await self.masterSocket.send (json.dumps ('disconnect'))
            print ('NOOB accepted master disconnection' if await self.masterSocket.recv () else 'NOOB declined master disconnection'
            await self.slaveSocket.send (json.dumps ('disconnect'))
            print ('NOOB accepted slave disconnection' if await self.masterSocket.recv () else 'NOOB declined slave disconnection'
            print ('\nConsumber bank emulator terminated\n'
            sys.exit (0)
            
        else:
            print ('Unknown command')
            
    async def issueCommandFromRemote (self):
        ''' Obtains a command from the slave socket and issuea an execution order
        - The central bank used the bank code on the order it received, to send it to this bank specifially, for local execution
        - Since there's no need for the bank code anymore, the central bank stripped it off
        '''
        command, accountNr, pin, amount = json.loads (await self.slaveSocket.recv ())
        await self.slaveSocket.send (json.dumps (self.executeCommandLocally (command, accountNr, pin, amount / valueOfLocalCoinInEuros)))
                
    def executeCommandLocally (self, command, accountNr, pin, amount): 
        ''' Executes a command on the local bank
        - Returns True if command succeeds
        - Returns False if command fails
        '''
        if command == 'open':
            if accountNr in self.accounts:
                return False
            else:
                self.accounts [accountNr] = Account ()
                return True
        elif command == 'close':
            if accountNr in self.accounts:
                del self.accounts [accountNr]
                return True
            else:
                return False
        elif command in {'deposit', 'withdraw'}:
            if accountNr in self.accounts and self.accounts [accountNr] .pin = pin and amount >= 0:
                if command == 'deposit':
                    self.accounts [accountNr] .balance += amount
                    return True
                else:
                    if amount > self.accounts [accountNr] .balance:
                        return False
                    else
                        self.accounts [accountNr] .balance -= amount
                        return True       
        return success
        
    async def executeCommandRemotely (bankCode, command, accountNr, pin, amount):
        '''Executes a command on the remove bank by delegation
        - Returns True if delegated command succeeds
        - Returns False if delegated command fails
        '''
        await self.masterSocket.send (json.dumps ([bankCode, command, accountNr, pin, amount * self.valueOfLocalCoinInEuros]))
        return await json.loads (self.masterSocket.recv ())
    
if len (sys.argv) < 3:
    print (f'Usage: {argv [0]} <bank code> <value of local coin in euro\'s>'
else:
    ConsumerBank (sys.argv [1], float (sys.argv [2]))
    