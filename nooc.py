''' NOOC: Naive Objectionably Opaque Client

A.K.A. Naieve Ontzettend Onveilige Client

The NOOC is a consumer bank emulator to test the NOOB central bank

First start the NOOB

    python noob.py

Then start any number of NOOC instances:

    python nooc.py <bank code of the instance> <value of local coin in euro's>
    
Then perform some transactions, both remote and local

There may be only one instance with a certain bank code
If a bank has multiple branches, it should address the central bank from an overarching entity
In other words, the central bank is for interbank traffic only, not to glue branches together
While it doesn't make profit, it isn't a charity either...
'''

import sys
import asyncio
import websockets
import aioconsole
import json

import noob_connection_data

noobUrl = f'ws://{noob_connection_data.hostName}:{noob_connection_data.portNr}'
    
class Nooc:
    class Account:
        def __init__ (self, pin):
            self.pin = pin
            self.balance = 0
        
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
        
        async def connectMaster ():
            async with websockets.connect (noobUrl) as self.masterSocket:
                await aioconsole.ainput (f'Master socket: {self.masterSocket}\n')
                while True:
                    print ('Master loop, await send')
                    await self.masterSocket.send (json.dumps (['register', 'master', self.bankCode]))
                    
                    print ('Master loop, await receive')
                    if json.loads (await self.masterSocket.recv ()):
                        print ('NOOB accepted master connection')
                        await self.issueCommandFromLocal (self)
                    else:
                        print ('NOOB declined master connection')
                
        async def connectSlave ():
            async with websockets.connect (noobUrl) as self.slaveSocket:
                await aioconsole.ainput (f'Slave socket: {self.slaveSocket}\n')
                while True:
                    print ('Slave loop, await send')
                    await self.slaveSocket.send (json.dumps (['register', 'slave', self.bankCode]))
                    
                    print ('Slave loop, await receive')
                    if json.loads (await self.slaveSocket.recv ()):
                        print ('NOOB accepted slave connection')
                        await self.issueCommandFromRemote ()           
                    else:
                        print ('NOOB declined slave connection')
        
        await asyncio.gather (
            connectMaster (),
            connectSlave ()                         
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
                return
            
            # --- Issue command for local or remote execution
            
            if bankCode == self.bankCode:
                print ('Success' if self.executeCommandLocally (command, accountNr, pin, amount) else 'Failure')
            else:
                print ('Success' if await self.executeCommandRemotely (bankCode, command, accountNr, pin, amount) else 'Failure')
                
        elif command == 'quit':
            await self.masterSocket.send (json.dumps ('disconnect'))
            print ('NOOB accepted master disconnection' if await self.masterSocket.recv () else 'NOOB declined master disconnection')
            await self.slaveSocket.send (json.dumps ('disconnect'))
            print ('NOOB accepted slave disconnection' if await self.masterSocket.recv () else 'NOOB declined slave disconnection')
            print ('\nConsumber bank emulator terminated\n')
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
            if accountNr in self.accounts and self.accounts [accountNr] .pin == pin and amount >= 0:
                if command == 'deposit':
                    self.accounts [accountNr] .balance += amount
                    return True
                else:
                    if amount > self.accounts [accountNr] .balance:
                        return False
                    else:
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
    print (f'Usage: python {sys.argv [0]} <bank code> <value of local coin in euro\'s>')
else:
    Nooc (sys.argv [1], float (sys.argv [2]))
    