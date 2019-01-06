''' NOOC: Naive Objectionably Opaque Client

A.K.A. Naieve Ontzettend Onveilige Client

The NOOC is a consumer bank emulator to test the NOOB central bank.

First start the NOOB:

    python noob.py

Then start any number of NOOC instances:

    python nooc.py <unique bank code> <value of local coin in euro's>
    
Then open some accounts and perform several transactions, both remote and local.

Note that there may be only one instance with a certain bank code.
If a bank has multiple branches, it should address the central bank from an overarching entity.
In other words, the central bank is for interbank traffic only, not to glue branches together.
While it doesn't make profit, it isn't a charity either...
'''

import sys
import asyncio
import websockets

import bank
    
class Nooc (bank.Bank):
    debug = False
    
    columnWidth = 15
    nrOfColumns = 3
    tableWidth = nrOfColumns * columnWidth + nrOfColumns - 1
    tableSeparator = '=' * tableWidth
    headerUnderline = '-' * tableWidth
    
    class Account:
        def __init__ (self, pin):
            self.pin = pin
            self.balance = 0
        
    def __init__ (self, bankCode, valueOfLocalCoinInEuros):
        super () . __init__ (bankCode)
        
        self.print ('Consumer bank emulator initiated')
        self.noobUrl = f'ws://{self.centralHostName}:{self.centralPortNr}'
        
        self.valueOfLocalCoinInEuros = valueOfLocalCoinInEuros  # All communication with central bank done in Euros
        self.accounts = {}
        
        asyncio.run (self.clientsCreator ())

    async def clientsCreator (self):
        ''' Initiates master and slave connections
        - The master connection is used to perform locally requested transactions on a remote bank
        - The slave connection is used to perform remotely requested transactions on the local bank
        '''
        
        async def roleClient (socket, role, action):
            await self.send (socket, role, ['register', role, self.bankCode])
            if await self.recv (socket, role):
                self.print (f'Registration of {role} accepted by {self.centralBankCode}')   
                while True:
                    await action ()
            else:
                self.print (f'Registration of {role} rejected by {self.centralBankCode}')
        
        async with websockets.connect (self.noobUrl) as self.masterSocket:
             self.print ('Master connection accepted by NOOB')
             async with websockets.connect (self.noobUrl) as self.slaveSocket:
                self.print ('Slave connection accepted by NOOB')
                await asyncio.gather (
                    roleClient (self.slaveSocket, 'slave', self.issueCommandFromRemote),
                    roleClient (self.masterSocket, 'master', self.issueCommandFromLocal)
                )
    
    async def issueCommandFromLocal (self):
        ''' Obtains a command from the console and issues an execution order
        - If the bankcode matches the local bank, the order is executed locally
        - If the bankcode doesn't match this local bank, the order is executed remotely
        '''
        
        command = await self.input ('Open, close, deposit, withdraw, quit or hack: ')
        
        if self.match (command, 'open', 'close', 'deposit', 'withdraw', 'hack'):
            
            # --- Show current account statuses
            
            if self.match (command, 'hack'):
                self.print (f'{self.tableSeparator}')
                self.print (f'{"account nr":{self.columnWidth}}{"pin":{self.columnWidth}}{"balance":{self.columnWidth}}')
                self.print (f'{self.headerUnderline}')
                for accountNr, account in self.accounts.items ():
                    self.print (f'{accountNr:{self.columnWidth}} {account.pin:{self.columnWidth}} {account.balance:{self.columnWidth}}')
                self.print (f'{self.tableSeparator}')
                return
        
            # --- Get user input
            
            pin = await self.input ('Pin: ')
            
            slaveBankCode = await self.input ('Bank code (press [enter] for local bank): ')
            if not slaveBankCode:
                slaveBankCode = self.bankCode
                self.print (f'Bank code {slaveBankCode} assumed')
                
            accountNr = await self.input ('Account number: ')
            
            if self.match (command, 'open', 'close'):
                amount = 0
            else:
                amount = float (await self.input ('Amount: '))
               
            # --- Allow user to verify input, except pincode
            
            self.print (f'Command: {command}')
            self.print (f'Bank code: {slaveBankCode}')
            self.print (f'Account nr: {accountNr}')
            
            if self.match (command, 'deposit', 'withdraw'):
                self.print (f'Amount: {amount}')
                            
            if not self.match (await self.input ('Correct (yes / no): '), 'yes'):   # Stay on safe side
                self.print ('Transaction broken off')
                return
            
            # --- Issue command for local or remote execution
            
            if slaveBankCode == self.bankCode:
                self.print ('Success' if self.executeCommandLocally (command, accountNr, pin, amount) else 'Failure')
            else:
                self.print ('Success' if await self.executeCommandRemotely (slaveBankCode, command, accountNr, pin, amount) else 'Failure')
                
        elif self.match (command, 'quit'):
            for socket, role in ((self.masterSocket , 'master'), (self.slaveSocket, 'slave')):
                await self.send (socket, role, 'disconnect')
                reply = self.recv (socket, role)
            self.print ('\nConsumber bank emulator terminated\n')
            sys.exit (0)
            
        else:
            print ('Unknown command')
            
    async def issueCommandFromRemote (self):
        ''' Obtains a command from the slave socket and issues an execution order
        - The central bank used the bank code on the order it received, to send it to this bank specifially, for local execution
        - Since there's no need for the bank code anymore, the central bank stripped it off
        '''
        await self.send (self.slaveSocket, 'slave', 'query', self.debug)
        command, accountNr, pin, amount = await self.recv (self.slaveSocket, 'slave', self.debug)
        await self.send (self.slaveSocket, 'slave', self.executeCommandLocally (command, accountNr, pin, amount / self.valueOfLocalCoinInEuros), self.debug)
                
    def executeCommandLocally (self, command, accountNr, pin, amount): 
        ''' Executes a command on the local bank
        - Returns True if command succeeds
        - Returns False if command fails
        '''
        if self.match (command, 'open'):
            if accountNr in self.accounts:
                return False
            else:
                self.accounts [accountNr] = self.Account (pin)
                return True
        elif self.match (command, 'close'):
            if accountNr in self.accounts:
                del self.accounts [accountNr]
                return True
            else:
                return False
        elif self.match (command, 'deposit', 'withdraw'):
            if accountNr in self.accounts and self.accounts [accountNr] .pin == pin and amount >= 0:
                if self.match (command, 'deposit'):
                    self.accounts [accountNr] .balance += amount
                    return True
                else:
                    if amount > self.accounts [accountNr] .balance:
                        return False
                    else:
                        self.accounts [accountNr] .balance -= amount
                        return True
        else:
            return False
        
    async def executeCommandRemotely (self, bankCode, command, accountNr, pin, amount):
        '''Executes a command on the remove bank by delegation
        - Returns True if delegated command succeeds
        - Returns False if delegated command fails
        '''
        await self.send (self.masterSocket, 'master', [bankCode, command, accountNr, pin, amount * self.valueOfLocalCoinInEuros])
        return await self.recv (self.masterSocket, 'master')
    
if len (sys.argv) < 3:
    print (f'Usage: python {sys.argv [0]} <bank code> <value of local coin in euro\'s>')
else:
    Nooc (sys.argv [1] .lower (), float (sys.argv [2]))
    