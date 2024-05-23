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

    def process_request(self, address: str, message: str):
        parts = message.split('@')
        command = parts[0]
        params = parts[1:]

        if command == "create_account":
            account_id = params[0]
            password = params[1]
            if not account_id.isdigit() or len(account_id) != 10:
                self.send_string(address, "error@A@Account ID must consist of 10 digits")
                return
            if self.account_exists(account_id):
                self.send_string(address, "error@A@Account already exists")
                return
            if not (len(password) >= 8 and any(c.isupper() for c in password) and any(c.islower() for c in password) and any(c.isdigit() for c in password)):
                self.send_string(address, "error@A@Password must be at least 8 characters long and include uppercase letters, lowercase letters, and numbers")
                return
            self.create_account(account_id, password)
            self.send_string(address, "success@Account created successfully")
        
        elif command == "log_in":
            account_id = params[0]
            password = params[1]
            if not self.account_exists(account_id):
                self.send_string(address, "error@A@Invalid account ID")
                return
            if not self.verify_password(account_id, password):
                self.send_string(address, "error@B@Invalid password")
                return
            self.send_string(address, "success@Login successful")

        elif command == "deposit_cash":
            account_id = params[0]
            amount = float(params[1])
            if not self.account_exists(account_id):
                self.send_string(address, "error@Invalid account ID")
                return
            if amount <= 0 or amount > 50000:
                self.send_string(address, "error@Deposit amount must be between $0.01 and $50000.00")
                return
            starting_balance, ending_balance = self.deposit_cash(account_id, amount)
            self.send_string(address, f"success@${amount:.2f} deposited successfully. Balance: {starting_balance} -> {ending_balance}")

        elif command == "return_card":
            self.send_string(address, "success@Card returned successfully")

        elif command == "change_password":
            account_id = params[0]
            new_password = params[1]

            old_password = self.get_password(account_id)
            if new_password == old_password:
                self.send_string(address, "error@New password cannot be the same as the old password")
                return
            if not (len(new_password) >= 8 and any(c.isupper() for c in new_password) and any(c.islower() for c in new_password) and any(c.isdigit() for c in new_password)):
                self.send_string(address, "error@New password must be at least 8 characters long and include uppercase letters, lowercase letters, and numbers")
                return
            self.change_password(account_id, new_password)
            self.send_string(address, "success@Password changed successfully")

        elif command == "transfer_money":
            sender_id = params[0]
            receiver_id = params[1]
            amount = float(params[2])

            if not receiver_id.isdigit() or len(receiver_id) != 10:
                self.send_string(address, "error@Receiver's account ID must consist of 10 digits")
                return
            
            if not self.account_exists(sender_id):
                self.send_string(address, "error@Invalid sender account ID")
                return
            
            if amount <= 0 or amount > 50000:
                self.send_string(address, "error@Transfer amount must be between $0.01 and $50000.00")
                return
            
            if not self.has_sufficient_balance(sender_id, amount):
                self.send_string(address, "error@Insufficient account balance for transfer")
                return
            
            sender_starting_balance, sender_ending_balance, receiver_starting_balance, receiver_ending_balance = self.transfer_money(sender_id, receiver_id, amount)
            self.send_string(address, f"success@${amount:.2f} transferred successfully. Sender balance: {sender_starting_balance} -> {sender_ending_balance}, Receiver balance: {receiver_starting_balance} -> {receiver_ending_balance}")
        
        elif command == "withdraw_cash":
            account_id = params[0]
            amount = float(params[1])

            if amount <= 0 or amount > 50000:
                self.send_string(address, "error@Transfer amount must be between $0.01 and $50000.00")
                return
            
            if not self.has_sufficient_balance(account_id, amount):
                self.send_string(address, "error@Insufficient account balance for withdrawal")
                return
            
            starting_balance, ending_balance = self.withdraw_cash(account_id, amount)
            self.send_string(address, f"success@${amount:.2f} withdrawn successfully. Balance: {starting_balance} -> {ending_balance}")
        
        elif command == "close_account":
            account_id = params[0]

            if not self.has_zero_balance(account_id):
                self.send_string(address, "error@Account balance must be zero to close the account")
                return
            self.close_account(account_id)
            self.send_string(address, "success@Account closed successfully")   

        elif command == "query":
            account_id = params[0]

            account_info, transactions = self.query_account(account_id)
            transactions_text = f"Password: {account_info[0]}\nBalance: ${account_info[1]:.2f}\n\nTransactions:\n"
            for transaction in transactions:
                transactions_text += (f"{transaction[2]} - {transaction[0]}: ${transaction[1]:.2f} "
                                      f"(Starting Balance: ${transaction[3]:.2f}, Ending Balance: ${transaction[4]:.2f})\n")
            self.send_string(address, f"success@{transactions_text}")
            
    def account_exists(self, account_id: str) -> bool:
        conn = sqlite3.connect('bank.db')
        cursor = conn.cursor()
        cursor.execute('SELECT 1 FROM accounts WHERE id = ?', (account_id,))
        exists = cursor.fetchone() is not None
        conn.close()
        return exists
    
    def verify_password(self, account_id: str, password: str) -> bool:
        conn = sqlite3.connect('bank.db')
        cursor = conn.cursor()
        cursor.execute('SELECT password FROM accounts WHERE id = ?', (account_id,))
        result = cursor.fetchone()
        conn.close()
        if result is None:
            return False
        return result[0] == password
    
    def has_sufficient_balance(self, account_id: str, amount: float) -> bool:
        conn = sqlite3.connect('bank.db')
        cursor = conn.cursor()
        cursor.execute('SELECT balance FROM accounts WHERE id = ?', (account_id,))
        result = cursor.fetchone()
        conn.close()
        if result is None:
            return False
        return result[0] >= amount
    
    def has_zero_balance(self, account_id: str) -> bool:
        conn = sqlite3.connect('bank.db')
        cursor = conn.cursor()
        cursor.execute('SELECT balance FROM accounts WHERE id = ?', (account_id,))
        result = cursor.fetchone()
        conn.close()
        if result is None:
            return False
        return result[0] == 0

    def get_password(self, account_id: str) -> str:
        conn = sqlite3.connect('bank.db')
        cursor = conn.cursor()
        cursor.execute('SELECT password FROM accounts WHERE id = ?', (account_id,))
        result = cursor.fetchone()
        conn.close()
        if result is None:
            return ""
        return result[0]
    
    def create_account(self, account_id: str, password: str):
        conn = sqlite3.connect('bank.db')
        cursor = conn.cursor()
        cursor.execute('INSERT INTO accounts (id, password, balance) VALUES (?, ?, 0)', (account_id, password))
        conn.commit()
        conn.close()

    def deposit_cash(self, account_id: str, amount: float):
        conn = sqlite3.connect('bank.db')
        cursor = conn.cursor()

        # 获取存款前的余额
        cursor.execute('SELECT balance FROM accounts WHERE id = ?', (account_id,))
        starting_balance = cursor.fetchone()[0]

        # 执行存款操作
        ending_balance = starting_balance + amount
        cursor.execute('UPDATE accounts SET balance = ? WHERE id = ?', (ending_balance, account_id))
        cursor.execute('INSERT INTO transactions (account_id, type, amount, starting_balance, ending_balance) VALUES (?, ?, ?, ?, ?)', (account_id, 'deposit', amount, starting_balance, ending_balance))

        conn.commit()
        conn.close()

        return starting_balance, ending_balance

    def change_password(self, account_id: str, new_password: str):
        conn = sqlite3.connect('bank.db')
        cursor = conn.cursor()
        cursor.execute('UPDATE accounts SET password = ? WHERE id = ?', (new_password, account_id))
        conn.commit()
        conn.close()

    def transfer_money(self, sender_id: str, receiver_id: str, amount: float):
        conn = sqlite3.connect('bank.db')
        cursor = conn.cursor()

        # 获取转账前的余额
        cursor.execute('SELECT balance FROM accounts WHERE id = ?', (sender_id,))
        sender_starting_balance = cursor.fetchone()[0]
        cursor.execute('SELECT balance FROM accounts WHERE id = ?', (receiver_id,))
        receiver_starting_balance = cursor.fetchone()[0]

        # 执行转账操作
        cursor.execute('UPDATE accounts SET balance = balance - ? WHERE id = ?', (amount, sender_id))
        cursor.execute('UPDATE accounts SET balance = balance + ? WHERE id = ?', (amount, receiver_id))
        cursor.execute('INSERT INTO transactions (account_id, type, amount, starting_balance, ending_balance) VALUES (?, ?, ?, ?, ?)', (sender_id, 'transfer_out', amount, sender_starting_balance, sender_starting_balance - amount))
        cursor.execute('INSERT INTO transactions (account_id, type, amount, starting_balance, ending_balance) VALUES (?, ?, ?, ?, ?)', (receiver_id, 'transfer_in', amount, receiver_starting_balance, receiver_starting_balance + amount))

        # 获取转账后的余额
        cursor.execute('SELECT balance FROM accounts WHERE id = ?', (sender_id,))
        sender_ending_balance = cursor.fetchone()[0]
        cursor.execute('SELECT balance FROM accounts WHERE id = ?', (receiver_id,))
        receiver_ending_balance = cursor.fetchone()[0]

        conn.commit()
        conn.close()

        return sender_starting_balance, sender_ending_balance, receiver_starting_balance, receiver_ending_balance
    
    def withdraw_cash(self, account_id: str, amount: float):
        conn = sqlite3.connect('bank.db')
        cursor = conn.cursor()

        # 获取取款前的余额
        cursor.execute('SELECT balance FROM accounts WHERE id = ?', (account_id,))
        starting_balance = cursor.fetchone()[0]

        # 执行取款操作
        ending_balance = starting_balance - amount
        cursor.execute('UPDATE accounts SET balance = ? WHERE id = ?', (ending_balance, account_id))
        cursor.execute('INSERT INTO transactions (account_id, type, amount, starting_balance, ending_balance) VALUES (?, ?, ?, ?, ?)', (account_id, 'withdraw', amount, starting_balance, ending_balance))

        conn.commit()
        conn.close()

        return starting_balance, ending_balance
    
    def close_account(self, account_id: str):
        conn = sqlite3.connect('bank.db')
        cursor = conn.cursor()
        cursor.execute('DELETE FROM accounts WHERE id = ?', (account_id,))
        conn.commit()
        conn.close()

    def query_account(self, account_id: str):
        conn = sqlite3.connect('bank.db')
        cursor = conn.cursor()
        cursor.execute("SELECT password, balance FROM accounts WHERE id = ?", (account_id,))
        account_info = cursor.fetchone()
        cursor.execute("SELECT type, amount, date, starting_balance, ending_balance FROM transactions WHERE account_id = ?", (account_id,))
        transactions = cursor.fetchall()
        conn.close()
        return account_info, transactions