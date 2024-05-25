import os
import NetClient
import time
import random


##Example Code For Banking Project
#Feel free to rewrite this file!



# This function determines whether a new message has been received
def is_received_new_message(oldTimeStamp:int, oldServerMessage:str, Msgunprocessed:bool = False)->bool:
    if(Msgunprocessed):
        return True
    else:
        if(oldTimeStamp == zmqThread.messageTimeStamp and 
           oldServerMessage == zmqThread.receivedMessage):
            return False
        else:
            return True

if __name__=='__main__':

    ############ Connect the Server ############
    identity = "TeamX" #write your team name here.
    zmqThread = NetClient.ZmqClientThread(identity=identity)


    ############ Initialize Banking System ############
    timeStamp = -1 #Used when receiving new message
    serverMessage = "" #Used when receiving new message
    messageUnprocessed = False #Used when receiving new message 
    

    while(True):
        
        ############ Your Banking system design ############
        ##Example just for the naive testcase
        if(is_received_new_message(timeStamp,serverMessage,messageUnprocessed)):
            if(not messageUnprocessed):
                timeStamp = zmqThread.messageTimeStamp
                serverMessage = zmqThread.receivedMessage
            messageUnprocessed = False

            if(serverMessage == "create_account@123456"):
                card_id = ''.join([str(random.randint(0, 9)) for _ in range(10)])
                zmqThread.sendMsg("account_created@" + card_id)
                

            if(serverMessage == "deposit_cash@2000"):
                zmqThread.sendMsg("cash_deposited@2000")
                

            if(serverMessage == "open_app"):
                zmqThread.sendMsg("app_opened#1")
                

            if(serverMessage == "log_in@"+ card_id + "@123456#1"):
                zmqThread.sendMsg("logged_in@"+ card_id +"#1")
                

            if(serverMessage == "transfer_money@2023123456@500#1"):
                zmqThread.sendMsg("money_transfered@500#1")
                

            if(serverMessage == "withdraw_cash@1000@987654"):
                zmqThread.sendMsg("failed@withdraw_cash")
                

            if(serverMessage == "withdraw_cash@1000@123456"):
                zmqThread.sendMsg("cash_withdrawn@1000")
                

            if(serverMessage == "query"):
                zmqThread.sendMsg("query_showed")
                

            if(serverMessage == "return_card"):
                zmqThread.sendMsg("card_returned@"+ card_id)
                
        time.sleep(0.01)

        
    
        

            

    '''
    For Other kinds of available serverMessage, see readMe.txt
    '''
    