import sys
import os
import Server
import time
import random
from enum import IntEnum
from bank import initialize_database
#######   BANKING PROJECT    #######

### Simple Test Case ###
class UserState(IntEnum):
    #only for reference, it may be complex in other testcase.
    NOT_USEING = 1
    CARD_IN_ATM_WITHOUT_APP = 2
    CARD_IN_ATM_WITH_APP_LOGGED_IN = 3
    GET_CARD_BACK = 4
    


class User:
    def __init__(self, id, password, deposit_amount, transfer_amount, withdraw_amount, name = "test"):
        self.id = id
        self.password = password
        self.deposit_amount:int = deposit_amount
        self.transfer_amount:int = transfer_amount
        self.withdraw_amount:int = withdraw_amount
        
        self.finished = False 
        self.finished_print = False
        self.name = name
        self.state = UserState.NOT_USEING

        
    def change_state(self, target_state:UserState)-> str:
        self.state = target_state

    def is_finished(self):
        return self.finished


def testing(server:Server.ZmqServerThread):
    def is_received_new_message(oldTimeStamp:int, oldServerMessage:str, Msgunprocessed:bool = False)->bool:
        if(Msgunprocessed):
            return True
        else:
            if(oldTimeStamp == server.messageTimeStamp and 
            oldServerMessage == server.receivedMessage):
                return False
            else:
                return True
    
    ############ Initialize Customers ############
    users = [User("", "123456", 2000, 500, 1000)] ##There can be many users in testcase.
    timeStamp = -1 #default time stamp is -1
    clientMessage = "" #default received message is ""
    messageUnprocessed = False #Used when receiving new message 
    count = 0
    for user in users:
        server.send_string(server.bindedClient,f"create_account@{user.password}")

    
    ############ Customer timed automata ############
    while(True):
        
        for each_user in users:
            match each_user.state:
                case UserState.NOT_USEING:
                    if(is_received_new_message(timeStamp,clientMessage,messageUnprocessed)):
                        if(not messageUnprocessed):
                            timeStamp = server.messageTimeStamp
                            clientMessage = server.receivedMessage
                        messageUnprocessed = False
                        if(clientMessage.startswith(f"account_created@") ):
                            card_id = clientMessage.split("@")[1]
                            each_user.id = card_id
                            each_user.change_state(UserState.CARD_IN_ATM_WITHOUT_APP)
                            server.send_string(server.bindedClient,f"deposit_cash@{each_user.deposit_amount}")


                case UserState.CARD_IN_ATM_WITHOUT_APP:
                    if(is_received_new_message(timeStamp,clientMessage,messageUnprocessed)):
                        if(not messageUnprocessed):
                            timeStamp = server.messageTimeStamp
                            clientMessage = server.receivedMessage
                        messageUnprocessed = False
                        if(clientMessage == f"cash_deposited@{each_user.deposit_amount}"):
                            print(f"User {each_user.name} deposited {each_user.deposit_amount} Yuan.")
                            server.send_string(server.bindedClient,"open_app")
                            
                        if(clientMessage == "app_opened#1"):
                            print("App 1 is opened.")
                            server.send_string(server.bindedClient,f"log_in@{each_user.id}@{each_user.password}#1")

                        if(clientMessage == f"logged_in@{each_user.id}#1"):
                            print(f"User {each_user.name} Logged in on APP 1")
                            each_user.change_state(UserState.CARD_IN_ATM_WITH_APP_LOGGED_IN)
                            server.send_string(server.bindedClient,f"transfer_money@2023123456@{each_user.transfer_amount}#1")

                case UserState.CARD_IN_ATM_WITH_APP_LOGGED_IN:
                    if(is_received_new_message(timeStamp,clientMessage,messageUnprocessed)):
                        if(not messageUnprocessed):
                            timeStamp = server.messageTimeStamp
                            clientMessage = server.receivedMessage
                        messageUnprocessed = False
                        if(clientMessage == f"money_transfered@{each_user.transfer_amount}#1"):
                            print(f"User {each_user.name} transfered {each_user.transfer_amount} to others.")
                            server.send_string(server.bindedClient,f"withdraw_cash@{each_user.withdraw_amount}@987654")

                        if(clientMessage == "failed@withdraw_cash"):
                            print("Failed to withdraw.")
                            server.send_string(server.bindedClient,f"withdraw_cash@{each_user.withdraw_amount}@{each_user.password}")

                        if(clientMessage == f"cash_withdrawn@{each_user.withdraw_amount}"):
                            print(f"User {user.name} withdrew {each_user.withdraw_amount} Yuan.)")
                            server.send_string(server.bindedClient,"query")

                        if(clientMessage == "query_showed"):
                            print(f"User {user.name} queried")
                            server.send_string(server.bindedClient,"return_card")

                        if(clientMessage == f"card_returned@{each_user.id}"):
                            print(f"User {user.name} get the card back.")
                            each_user.finished = True
                            each_user.change_state(UserState.GET_CARD_BACK)

                case UserState.GET_CARD_BACK:
                    if each_user.is_finished() and not each_user.finished_print:
                        print(f"User {each_user.name} has finished using the system")
                        each_user.finished_print = True
                        count += 1
                            

            
        if(count == len(users)):
            print("PASSED: ALL USERS SUCCESSFULLY USED THE SYSTEM!")
            break

        time.sleep(0.01)




if __name__ == "__main__":
    my_server = Server.ZmqServerThread()
    initialize_database()
    while(True):
        if(len(my_server.clients_addr) == 0):
            continue
        elif(len(my_server.clients_addr) >=2 ):
            print('more than 1 client address stored. server will exit')
            sys.exit()
        else:
            addr = list(my_server.clients_addr)[0]
            msg = input(f"Initiate evaluation for {addr}?: (y/n)\n")
            if msg == 'y':
                my_server.bindedClient = addr
                while True:
                    if my_server.receivedMessage:
                        my_server.process_request(my_server, my_server.receivedMessage)
            else:
                continue