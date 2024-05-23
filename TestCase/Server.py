import time
import zmq
import threading
import sys
import os
import sqlite3

class ZmqServerThread(threading.Thread):
    _port = 27132
    clients_addr=set()

    def __init__(self, server_port:int = None) -> None:
        threading.Thread.__init__(self)
        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.ROUTER)
        self.bindedClient = None
        self._receivedMessage:str = None
        self._messageTimeStamp:int = None # UNIX Time Stamp, should be int

        if(server_port is not None):
            self.port  = server_port

        print("Start hosting at port:{port}".format(port = self._port))
        self.start()


    @property
    def port(self):
        return self._port
    
    @port.setter
    def port(self,value:int):
        if(value < 0 or value > 65535):
            raise ValueError('score must between 0 ~ 65535!')
        self._port = value

    @property
    def messageTimeStamp(self)->int:
        if(self._messageTimeStamp == None):
            return -1
        else:
            return self._messageTimeStamp

    @messageTimeStamp.setter
    def messageTimeStamp(self,value:int):
        self._messageTimeStamp = value

    @property
    def receivedMessage(self)->str:
        if(self._receivedMessage == None):
            return ""
        else:
            return self._receivedMessage

    @receivedMessage.setter
    def receivedMessage(self,value:str):
        self._receivedMessage = value

    #start listening
    def hosting(self, server_port:int = None)-> None:

        if(server_port is not None):
            self.port  = server_port
        self.socket.bind("tcp://{0}:{1}".format("127.0.0.1", self.port))

        while True:
            [address,contents]=self.socket.recv_multipart()
            address_str = address.decode()
            contents_str = contents.decode()
            self.clients_addr.add(address_str)
            self.messageTimeStamp = int(round(time.time() * 1000)) #UNIX Time Stamp
            self.receivedMessage = contents_str
            print("client:[%s] message:%s\n"%(address_str,contents_str))



    def send_string(self,address:str,msg:str =""):
        if not self.socket.closed:
            print("Send to client:[%s] message:%s\n"%(str(address),str(msg)))
            self.socket.send_multipart([address.encode(), msg.encode()]) #send msg to address
        else:
            print("socket is closed,can't send message...")

    #override
    def run(self):
        self.hosting()

    # def process_request(self, address: str, message: str):
    #     if message.startswith("create_account@"):
    #         password = message.split("@")[1]
    #         account_id = self.create_account(password)
    #         self.send_string(address, f"account_created@{account_id}")
    #     elif message.startswith("deposit_cash@"):
    #         amount = float(message.split("@")[1])
    #         self.deposit_cash(amount)
    #         self.send_string(address, f"cash_deposited@{amount}")
    #     elif message.startswith("withdraw_cash@"):
    #         parts = message.split("@")
    #         amount = float(parts[1])
    #         password = parts[2]
    #         self.withdraw_cash(amount, password)
    #         self.send_string(address, f"cash_withdrawn@{amount}")

    # def create_account(self, password: str) -> str:
    #     conn = sqlite3.connect('bank.db')
    #     cursor = conn.cursor()
    #     account_id = self.generate_unique_account_id()
    #     cursor.execute('INSERT INTO accounts (id, password, balance) VALUES (?, ?, ?)', (account_id, password, 0.0))
    #     conn.commit()
    #     conn.close()
    #     return account_id

    # def generate_unique_account_id(self) -> str:
    #     conn = sqlite3.connect('bank.db')
    #     cursor = conn.cursor()
    #     while True:
    #         account_id = str(random.randint(1000000000, 9999999999))
    #         cursor.execute('SELECT id FROM accounts WHERE id = ?', (account_id,))
    #         if cursor.fetchone() is None:
    #             break
    #     conn.close()
    #     return account_id

    # def deposit_cash(self, amount: float):
    #     conn = sqlite3.connect('bank.db')
    #     cursor = conn.cursor()
    #     # Assuming the binded client is currently associated with a specific account
    #     cursor.execute('UPDATE accounts SET balance = balance + ? WHERE id = ?', (amount, self.bindedClient))
    #     cursor.execute('INSERT INTO transactions (account_id, type, amount) VALUES (?, ?, ?)', (self.bindedClient, 'deposit', amount))
    #     conn.commit()
    #     conn.close()

    # def withdraw_cash(self, amount: float, password: str):
    #     conn = sqlite3.connect('bank.db')
    #     cursor = conn.cursor()
    #     cursor.execute('SELECT balance FROM accounts WHERE id = ? AND password = ?', (self.bindedClient, password))
    #     result = cursor.fetchone()
    #     if result and result[0] >= amount:
    #         cursor.execute('UPDATE accounts SET balance = balance - ? WHERE id = ?', (amount, self.bindedClient))
    #         cursor.execute('INSERT INTO transactions (account_id, type, amount) VALUES (?, ?, ?)', (self.bindedClient, 'withdraw', amount))
    #         conn.commit()
    #     conn.close()


