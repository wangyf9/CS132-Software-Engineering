import os
import sys
import time
from enum import IntEnum
from . import NetClient
from .elevator import Elevator
from .elevatorState import State
from .elevatorController import ElevatorController
from PyQt5.QtCore import QTimer
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QApplication
##Example Code For Elevator Project
#Feel free to rewrite this file!

SIMULATION_SPEED = 100 #ms
#Feel free to design the states of your elevator system.
class ElevatorState(IntEnum):
    up = 0
    down = 1
    stopped_door_closed = 2
    stopped_door_opened = 3
    stopped_opening_door = 4

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
    identity = "Team15" #write your team name here.
    zmqThread = NetClient.ZmqClientThread(identity=identity)


    ############ Initialize Elevator System ############
    status = {
        'timeStamp': -1,  # Used when receiving new message
        'serverMessage': "",  # Used when receiving new message
        'messageUnprocessed': False,  # Used when receiving new message
        'temp_msg': ""
    }
    
    app = QApplication(sys.argv)
    e1 = Elevator(1,zmqThread)
    e2 = Elevator(2,zmqThread)
    # window 1~3 are the windows for the outside panel 
    window1 = QtWidgets.QWidget()
    window2 = QtWidgets.QWidget()
    window3 = QtWidgets.QWidget()
    window4 = QtWidgets.QWidget()  
    simulation_window = QtWidgets.QWidget() 
    controller = ElevatorController(zmqThread,e1,e2)
    controller.create_window(window1,"fB1", up=True, down=False)
    controller.create_window(window2,"f1", up=True, down=True)
    controller.create_window(window3,"f2", up=True, down=True)
    controller.create_window(window4,"f3", up=False, down=True)
    controller.create_simulation_window(simulation_window)
    controller.create_button_dict()
    controller.connect()
    for button_name, info in controller.button_dict.items():
        button = info["button"]
        state = info["state"]
        elevator_id = info["elevatorId"]
    print(f"Button Name: {button_name}, State: {state}, Elevator ID: {elevator_id}")
    window1.show()
    window2.show()
    window3.show()
    window4.show()
    simulation_window.show()
    e1.show()
    e2.show()
    def update(status):
        if(len(zmqThread.buffer)!=0):
            status["temp_msg"] = zmqThread.buffer.pop(0)
        else:
            status["temp_msg"] = ""
        e1.update()
        e2.update()
        controller.update(status["temp_msg"])
    timer = QTimer()
    timer.timeout.connect(lambda: update(status))
    timer.start(SIMULATION_SPEED)
    sys.exit(app.exec_())

            

    '''
    For Other kinds of available serverMessage, see readMe.txt
    '''
    