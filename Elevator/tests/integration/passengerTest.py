import sys
import os
from src import Server
import time
import random
from enum import IntEnum
#######   ELEVATOR PROJECT    #######

### Simple Test Case ###
class PassengerState(IntEnum):
    #only for reference, it may be complex in other testcase.
    IN_ELEVATOR_1_AT_TARGET_FLOOR = 1
    IN_ELEVATOR_1_AT_OTHER_FLOOR = 2
    IN_ELEVATOR_2_AT_TARGET_FLOOR = 3
    IN_ELEVATOR_2_AT_OTHER_FLOOR = 4
    OUT_ELEVATOR_0_AT_TARGET_FLOOR = 5
    OUT_ELEVATOR_0_AT_OTHER_FLOOR = 6


class Passenger:
    def __init__(self, start_floor, target_floor,name = "test"):
        self.start_floor:int = start_floor
        self.target_floor:int = target_floor
        self.direction = "up" if self.target_floor >self.start_floor else "down"
        self._elevator_code = -1
        self.current_floor = start_floor
        self.finished = False if self.target_floor != self.start_floor else True
        self.finished_print = False
        self.name = name
        self.matching_signal = f"up_floor_arrived@{self.current_floor}" if self.direction == "up" else f"down_floor_arrived@{self.current_floor}"
        self.state = PassengerState.OUT_ELEVATOR_0_AT_OTHER_FLOOR

        
    def change_state(self, target_state:PassengerState)-> str:
        self.state = target_state

    def is_finished(self):
        return self.finished
    def set_elevator_code(self,value):
        self._elevator_code = value
    def get_elevator_code(self):
        return self._elevator_code


def testing(server:Server.ZmqServerThread):
    def is_received_new_message(oldTimeStamp:int, oldServerMessageLength:int)->bool:
        if(oldTimeStamp == server.messageTimeStamp and 
        oldServerMessageLength == len(server.receivedMessage)):
            return False
        else:
            return True
    
    ############ Initialize Passengers ############
    passengers = [Passenger(3, -1,"A"),Passenger(2, 3,"B"),Passenger(1, 3,"C")] ##There can be many passengers in testcase.
    timeStamp = -1 #default time stamp is -1
    clientMessage = 0 #default received message length is 0
    count = 0
    server.send_string(server.bindedClient,"reset")

    time.sleep(1)


    timecount = 0

    
    for passenger in passengers:

        server.send_string(server.bindedClient,f"call_up@{passenger.current_floor}" if passenger.target_floor > passenger.current_floor else f"call_down@{passenger.current_floor}")
        time.sleep(0.5)


    
    ############ Passenger timed automata ############


    while(True):
        timecount += 1
        for each_passenger in passengers:


            match each_passenger.state:

                case PassengerState.OUT_ELEVATOR_0_AT_OTHER_FLOOR:
                    if(is_received_new_message(timeStamp,clientMessage)):
                        timeStamp = server.messageTimeStamp
                        clientMessage = server.receivedMessage
                        if(clientMessage.startswith(each_passenger.matching_signal) and each_passenger.current_floor == each_passenger.start_floor):
                            each_passenger.set_elevator_code(int(clientMessage.split("#")[-1]))
                            continue
                        
                        if(clientMessage == f"door_opened#{each_passenger.get_elevator_code()}"):
                            print(f"Passenger {each_passenger.name} is Entering the elevator {each_passenger.get_elevator_code()}")
                            
                            if(each_passenger.get_elevator_code() == 1):
                                each_passenger.change_state(PassengerState.IN_ELEVATOR_1_AT_OTHER_FLOOR)
                            elif(each_passenger.get_elevator_code() == 2):
                                each_passenger.change_state(PassengerState.IN_ELEVATOR_2_AT_OTHER_FLOOR)
                            server.send_string(server.bindedClient,f"select_floor@{each_passenger.target_floor}#{each_passenger.get_elevator_code()}")
                            continue
                    else:
                        continue

                case PassengerState.IN_ELEVATOR_1_AT_OTHER_FLOOR:
                    if(is_received_new_message(timeStamp,clientMessage)):
                        timeStamp = server.messageTimeStamp
                        clientMessage = server.receivedMessage
                        if(clientMessage.endswith(f"floor_arrived@{each_passenger.target_floor}#{each_passenger.get_elevator_code()}")):
                            each_passenger.current_floor = each_passenger.target_floor
                            each_passenger.change_state(PassengerState.IN_ELEVATOR_1_AT_TARGET_FLOOR)
                            continue

                case PassengerState.IN_ELEVATOR_2_AT_OTHER_FLOOR:
                    # Not exec in this naive testcase
                    if(is_received_new_message(timeStamp,clientMessage)):
                        timeStamp = server.messageTimeStamp
                        clientMessage = server.receivedMessage
                        if(clientMessage.endswith(f"floor_arrived@{each_passenger.target_floor}#{each_passenger.get_elevator_code()}")):
                            each_passenger.current_floor = each_passenger.target_floor
                            each_passenger.change_state(PassengerState.IN_ELEVATOR_2_AT_TARGET_FLOOR)
                            continue

                case PassengerState.IN_ELEVATOR_1_AT_TARGET_FLOOR:
                    if(is_received_new_message(timeStamp,clientMessage)):
                        timeStamp = server.messageTimeStamp
                        clientMessage = server.receivedMessage
                        if(clientMessage == f"door_opened#1"):
                            print(f"Passenger {each_passenger.name} is Leaving the elevator")
                            each_passenger.change_state(PassengerState.OUT_ELEVATOR_0_AT_TARGET_FLOOR)
                            each_passenger.finished = True
                            continue


                case PassengerState.IN_ELEVATOR_2_AT_TARGET_FLOOR:
                    if(is_received_new_message(timeStamp,clientMessage)):
                        timeStamp = server.messageTimeStamp
                        clientMessage = server.receivedMessage
                        if(clientMessage == f"door_opened#2"):
                            print(f"Passenger {each_passenger.name} is Leaving the elevator")
                            each_passenger.change_state(PassengerState.OUT_ELEVATOR_0_AT_TARGET_FLOOR)
                            each_passenger.finished = True
                            continue



                case PassengerState.OUT_ELEVATOR_0_AT_TARGET_FLOOR:
                    if each_passenger.is_finished() and not each_passenger.finished_print:
                        print(f"Passenger {each_passenger.name} has arrived at the target floor.")
                        each_passenger.finished_print = True
                        count += 1
            
        if(count == len(passengers)):
            print("PASSED: ALL PASSENGERS HAS ARRIVED AT THE TARGET FLOOR!")
            time.sleep(1)
            server.send_string(server.bindedClient,"reset")
            break
        
        if(timecount > 100):
            timecount = 0





if __name__ == "__main__":
    my_server = Server.ZmqServerThread()
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
                testing(my_server)
            else:
                continue