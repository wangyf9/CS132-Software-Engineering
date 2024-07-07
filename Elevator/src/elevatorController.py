from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QWidget
from PyQt5.QtTest import QTest
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import  QWidget, QVBoxLayout, QGraphicsView, QGraphicsScene, QGraphicsRectItem
from PyQt5.QtCore import Qt, QRectF
from PyQt5.QtGui import QBrush,QColor

from .elevator import Elevator
from .elevatorState import State
from .direction import Direction
from . import NetClient

# Elevator Controller
# This class is responsible for 
# 1. Parsing the command from the server
# 2. Assigning the inner button panel(open, close, select floor) to the elevator, without considering constraints
# 3. Assigning the outer button panel(call up, call down) to the elevator, considering which task to assign to which elevator
class ElevatorController():

    
    def __init__(self,zmqThread:NetClient.ZmqClientThread,elevator1,elevator2) -> None:
        # Initialize two elevators
        self.elevators: list[Elevator] = []
        self.elevators.append(elevator1)
        self.elevators.append(elevator2)
        self.outPanels:list[dict] = []
        # Client to send msg to server
        self.zmqThread = zmqThread
    def parseInput(self, command: str) -> None:
        """
        open_door#1: open the door of elevator 1
        close_door#1: close the door of elevator 1
        call_up: ["-1", "1", "2"], //For example, call_up@1 means a user on the first floor presses the button to call the elevator to go upwards.
        call_down: ["3", "2", "1"], //For instance, call_down@3 signifies a user on the third floor pressing the button to call the elevator to go downwards.
        select_floor: ["-1#1", "-1#2", "1#1", "1#2", "2#1", "2#2", "3#1", "3#2"], //For example, select_floor@2#1 means a user in elevator #1 selects to go to the second floor.
        reset: When your elevator system receives a reset signal, it should reset the elevator's state machine to its initial state.
        """
        if command == "": return
        # Parse the command, convert command to clicking button
        command_parts = command.split('@')
        action = command_parts[0]
        if action == "open_door#1":
            QTest.mouseClick(self.elevators[0].open, Qt.LeftButton)
            pass
        elif action == "open_door#2":
            QTest.mouseClick(self.elevators[1].open, Qt.LeftButton)
            pass
        elif action == "close_door#1":
            QTest.mouseClick(self.elevators[0].closeButton, Qt.LeftButton)
            pass
        elif action == "close_door#2":
            QTest.mouseClick(self.elevators[1].closeButton, Qt.LeftButton)
            pass
        elif action == "call_up":
            floor = int(command_parts[1])
            if floor == -1:
                QTest.mouseClick(self.button_dict["-1_up"]["button"], Qt.LeftButton)
            elif floor == 1:
                QTest.mouseClick(self.button_dict["1_up"]["button"], Qt.LeftButton)
            elif floor == 2:
                QTest.mouseClick(self.button_dict["2_up"]["button"], Qt.LeftButton)
            pass
        elif action == "call_down":
            floor = int(command_parts[1])
            if floor == 1:
                QTest.mouseClick(self.button_dict["1_down"]["button"], Qt.LeftButton)
            elif floor == 2:
                QTest.mouseClick(self.button_dict["2_down"]["button"], Qt.LeftButton)
            elif floor == 3:
                QTest.mouseClick(self.button_dict["3_down"]["button"], Qt.LeftButton)
            pass
        elif action == "select_floor":
            floor,eid = command_parts[1].split('#')
            eid = int(eid)-1
            floor = int(floor)
            if floor == -1:
                QTest.mouseClick(self.elevators[eid].fB1, Qt.LeftButton)
            elif floor == 1:
                QTest.mouseClick(self.elevators[eid].f1, Qt.LeftButton)
            elif floor == 2:
                QTest.mouseClick(self.elevators[eid].f2, Qt.LeftButton)
            elif floor == 3:
                QTest.mouseClick(self.elevators[eid].f3, Qt.LeftButton)
            pass
        elif action == "reset":
            self.reset()
            pass
    def reset(self) -> None:
        for elevator in self.elevators:
            elevator.reset()
        # Reset all buyttons
        for button_name, info in self.button_dict.items():
            button = info["button"]
            button.setStyleSheet("background-color: none;")
            self.button_dict[button_name]["state"] = "not pressed"
            self.button_dict[button_name]["elevatorId"] = -1
            self.button_dict[button_name]["count"] = 0
    def getNearestStopElevator(self, floor: int, dist) :
        # find the nearest elevator accrording to the floor that is requesting
        # return index of the elevator; return -1 if no elevator is available

        if(self.elevators[0].currentState == State.stopped_door_closed and len(self.elevators[0].targetFloor)==0):
            dist[0] = abs(self.elevators[0].getCurrentFloor() - floor)
        if(self.elevators[1].currentState == State.stopped_door_closed and len(self.elevators[1].targetFloor)==0):
            dist[1] = abs(self.elevators[1].getCurrentFloor() - floor)

    def getNearestElevatorWithDirect(self,floor,direction:Direction,dist):

        if floor == 2 :
            if direction == Direction.up:
                if self.elevators[0].currentPos < 1.5 and self.elevators[0].currentDirection == Direction.up:
                    dist[0] = abs(self.elevators[0].currentPos - floor)
                if self.elevators[1].currentPos < 1.5 and self.elevators[1].currentDirection == Direction.up:
                    dist[1] = abs(self.elevators[1].currentPos - floor)
            elif direction == Direction.down:
                if self.elevators[0].currentPos >= 2.5 and self.elevators[0].currentDirection == Direction.down:
                    dist[0] = abs(self.elevators[0].currentPos - floor)
                if self.elevators[1].currentPos >= 2.5 and self.elevators[1].currentDirection == Direction.down:
                    dist[1] = abs(self.elevators[1].currentPos - floor)
        elif floor == 1:
            if direction == Direction.up:
                if self.elevators[0].currentPos < 0.5 and self.elevators[0].currentDirection == Direction.up:
                    dist[0] = abs(self.elevators[0].currentPos - floor)
                if self.elevators[1].currentPos < 0.5 and self.elevators[1].currentDirection == Direction.up:
                    dist[1] = abs(self.elevators[1].currentPos - floor)
            elif direction == Direction.down:
                if self.elevators[0].currentPos >= 1.5 and self.elevators[0].currentDirection == Direction.down:
                    dist[0] = abs(self.elevators[0].currentPos - floor)
                if self.elevators[1].currentPos >= 1.5 and self.elevators[1].currentDirection == Direction.down:
                    dist[1] = abs(self.elevators[1].currentPos - floor)
        else:
            if self.elevators[0].currentDirection == direction:
                dist[0] = abs(self.elevators[0].currentPos - floor)
            if self.elevators[1].currentDirection == direction:
                dist[1] = abs(self.elevators[1].currentPos - floor)

    def is_elevator_idle_at_floor(self,idex, floor):
        """Check if an elevator is idle at a specific floor"""
        return (self.elevators[idex].currentState != State.up and self.elevators[idex].currentState != State.down 
                and len(self.elevators[idex].targetFloor) == 0 and self.elevators[idex].getCurrentFloor() == floor)
    
    def getElevatorIdleAtSameFloor(self,floor,dist):
        # find the nearest elevator accrording to the floor that is requesting
        # return index of the elevator; return -1 if no elevator is available
        if self.is_elevator_idle_at_floor(0, floor):
            dist[0] = 0
        if self.is_elevator_idle_at_floor(1, floor):
            dist[1] = 0

    def tryAssignElevatorId(self,floor,direction:Direction):
        dist = [99,99]
        id = -1
        self.getElevatorIdleAtSameFloor(floor,dist)        
        self.getNearestElevatorWithDirect(floor,direction,dist)
        self.getNearestStopElevator(floor,dist)
        id = dist.index(min(dist))
        if min(dist) == 99:
            return -1
        if floor == 2:
            if direction == Direction.up:
                # 2_up
                if self.button_dict["2_down"]["elevatorId"] != id:
                    pass
                else:
                    if(self.button_dict["2_down"]["state"] == "waiting"):
                        return -1
                    else:
                        pass
            elif direction == Direction.down:
                # 2_down
                if self.button_dict["2_up"]["elevatorId"] != id:
                    pass
                else:
                    if(self.button_dict["2_up"]["state"] == "waiting"):
                        return -1
                    else:
                        pass
            if (self.is_elevator_idle_at_floor(0, floor)) and (self.is_elevator_idle_at_floor(1, floor)):
                if self.button_dict["2_up"]["elevatorId"] == self.button_dict["2_down"]["elevatorId"]:
                    self.button_dict["2_up"]["elevatorId"] = 0
                    self.button_dict["2_down"]["elevatorId"] = 1
                else:
                    pass
        elif floor == 1:
            if direction == Direction.up:
                # 1_up
                if self.button_dict["1_down"]["elevatorId"] != id:
                    pass
                else:
                    if(self.button_dict["1_down"]["state"] == "waiting"):
                        return -1
                    else:
                        pass
            elif direction == Direction.down:
                # 1_down
                if self.button_dict["1_up"]["elevatorId"] != id:
                    pass
                else:
                    if(self.button_dict["1_up"]["state"] == "waiting"):
                        return -1
                    else:
                        pass
            if (self.is_elevator_idle_at_floor(0, floor)) and (self.is_elevator_idle_at_floor(1, floor)):
                if self.button_dict["1_up"]["elevatorId"] == self.button_dict["1_down"]["elevatorId"]:
                    self.button_dict["1_up"]["elevatorId"] = 0
                    self.button_dict["1_down"]["elevatorId"] = 1
                else:
                    pass
        if self.assignTarget(id,floor):
            return id  
        return -1  
    
    def assignTarget(self,eid:int,floor:int)->bool:
        if eid != -1:
            if self.elevators[eid].addTargetFloor(floor) == "OK":
                return True
            else:
                return False
        else:
            return False
    
    def update(self,msg:str) -> None:
        self.updateLCD()
        self.updateButtonText()
        self.update_simulation_window()
        if msg != "":
            self.parseInput(msg)
        for button_name, info in self.button_dict.items():
            button = info["button"]
            state = info["state"]
            elevator_id = info["elevatorId"]
            floor = info["floor"]
            if floor == -1:
                floor = 0
            direction = info["direction"]
            freeRideDirection = info["freeRideDirection"]
            count = info["count"]
            # Release control of the elevator if the elevator has left the floor
            if elevator_id != -1 and state == "not pressed":
                if not (self.elevators[elevator_id].currentPos > floor-0.01 and self.elevators[elevator_id].currentPos < floor+0.01):
                    self.button_dict[button_name]["elevatorId"] = -1
            if state == "pressed":
                # first check if the button still has control of specific elevator
                if elevator_id != -1:
                    # just open the door.
                    self.elevators[elevator_id].setOpenDoorFlag()
                    self.button_dict[button_name]["state"] = "not pressed"
                    self.floorArrivedMessage(direction,floor,elevator_id,count)
                    self.button_dict[button_name]["count"] = 0
                    button.setStyleSheet("background-color: none;")
                else:
                    # Get an available elevator
                    eid = self.tryAssignElevatorId(floor,freeRideDirection)
                    if eid != -1:
                        # Change Button State
                        self.button_dict[button_name]["state"] = "waiting"
                        self.button_dict[button_name]["elevatorId"] = eid
                        # Also remove ensure only this button has control of elevator with this eid
                        # for b_name,info_item in self.button_dict.items():
                        #     if self.button_dict[b_name]["elevatorId"] == eid and b_name != button_name:
                        #         self.button_dict[b_name]["elevatorId"] = -1
                pass
            elif state == "waiting":
                # Check is the elevator that the button is waiting has arrived.
                if self.elevators[elevator_id].currentPos > floor-0.01 and self.elevators[elevator_id].currentPos < floor+0.01:
                    self.button_dict[button_name]["state"] = "not pressed"
                    self.floorArrivedMessage(direction,floor,elevator_id,count)
                    self.button_dict[button_name]["count"] = 0
                    # do not release the control of that elevator until that elevator actually leaves that floor
                    # self.button_dict[button_name]["elevatorId"] = -1
                    button.setStyleSheet("background-color: none;")        
        return
    
    def floorArrivedMessage(self, direction:str,floor: int, eid: int,count:int) -> None:
        floors = ["-1", "1", "2", "3"]
        elevators = ["#1", "#2"]
        floor_str = floors[floor]
        elevator_str = elevators[eid]

        message = f"{direction}_floor_arrived@{floor_str}{elevator_str}"
        print(message)
        for _ in range(count):
            self.zmqThread.sendMsg(message)

############## UI Related Code ##############
    def create_window(self, window:QWidget,title, up, down):
        verticalLayout = QtWidgets.QVBoxLayout(window)
        if title == "fB1":
            window.setGeometry(500,700,250,150)
        elif title == "f1":
            window.setGeometry(500,500,250,150)
        elif title == "f2": 
            window.setGeometry(500,300,250,150)
        elif title == "f3":
            window.setGeometry(500,100,250,150)
        window.resize(250, 150)
        controls = {}

        lcd_layout = QtWidgets.QHBoxLayout()
        verticalLayout.addLayout(lcd_layout)

        # Use QLabel instead of QLCDNumber
        e1 = QtWidgets.QLabel()
        e1.setText(str(1))
        font = QtGui.QFont()
        font.setFamily("Times New Roman")
        font.setPointSize(20)
        e1.setFont(font)
        e1.setAlignment(QtCore.Qt.AlignCenter)
        e1.setStyleSheet("border: 2px solid black; background-color: lightgray;")
        lcd_layout.addWidget(e1)
        controls['e1'] = e1

        e2 = QtWidgets.QLabel()
        e2.setText(str(1))
        e2.setFont(font)
        e2.setAlignment(QtCore.Qt.AlignCenter)
        e2.setStyleSheet("border: 2px solid black; background-color: lightgray;")
        lcd_layout.addWidget(e2)
        controls['e2'] = e2
        if up:
            up_button = QtWidgets.QPushButton("Up")
            up_button.setObjectName("Up")
            verticalLayout.addWidget(up_button)
            controls['up'] = up_button

        if down:
            down_button = QtWidgets.QPushButton("Down")
            down_button.setObjectName("Down")
            verticalLayout.addWidget(down_button)
            controls['down'] = down_button

        window.setWindowTitle(title)

        self.outPanels.append(controls)

    def create_button_dict(self):
        self.button_dict = {
            "-1_up": {
                "button": self.outPanels[0]['up'],
                "state": "not pressed", # not pressed / pressed / waiting
                "elevatorId": -1,
                "floor": -1,
                "direction": "up",
                "freeRideDirection":Direction.up,
                "count": 0
            },

            "1_up": {
                "button": self.outPanels[1]['up'],
                "state": "not pressed", # not pressed / pressed / waiting
                "elevatorId": -1,
                "floor": 1,
                "direction": "up",
                "freeRideDirection":Direction.up,
                "count": 0
            },

            "1_down": {
                "button": self.outPanels[1]['down'],
                "state": "not pressed",
                "elevatorId": -1,
                "floor": 1,
                "direction": "down",
                "freeRideDirection":Direction.down,
                "count": 0
            },

            "2_up": {
                "button": self.outPanels[2]['up'],
                "state": "not pressed",
                "elevatorId": -1,
                "floor": 2,
                "direction": "up",
                "freeRideDirection":Direction.up,
                "count": 0
            },
            "2_down": {
                "button": self.outPanels[2]['down'],
                "state": "not pressed",
                "elevatorId": -1,
                "floor": 2,
                "direction": "down",
                "freeRideDirection":Direction.down,
                "count": 0
            },
            "3_down": {
                "button": self.outPanels[3]['down'],
                "state": "not pressed",
                "elevatorId": -1,
                "floor": 3,
                "direction": "down",
                "freeRideDirection":Direction.up,
                "count": 0
            }
        }

    def create_simulation_window(self, window: QWidget):
        width = 300
        height = 600
        window.setWindowTitle('Elevator Simulation')
        window.setGeometry(100, 100, width, height)
        layout = QVBoxLayout()
        
        scene = QGraphicsScene()
        scene.setSceneRect(0, 0, 300, 600)
        window.setGeometry(100, 100, int(1.1 * width), int(1.1 * height))
        view = QGraphicsView(scene)
        
        # Define elevator parameters
        elevator_width = width / 4
        elevator_height = height / 12  # Adjusted for 6 floors (including -1 floor)
        door_width = elevator_width / 2

        # Floor positions, including -1 floor and adjusting all positions upward
        floor_mult = [2/12, 5/12, 8/12, 11/12]  # Adjusted multipliers for new floor layout
        for mult in floor_mult:
            floor_left = QGraphicsRectItem(width / 8, mult * height, elevator_width, elevator_height)
            floor_right = QGraphicsRectItem(5 * width / 8, mult * height, elevator_width, elevator_height)
            scene.addItem(floor_left)
            scene.addItem(floor_right)

        # Left Elevator
        left_elevator_x = width / 8
        left_elevator_y = 8 * height / 12  # Elevator starts at the first floor (adjusted)
        left_elevator_rect = QRectF(left_elevator_x, left_elevator_y, elevator_width, elevator_height)
        
        # Left Elevator Doors
        left_door1 = QGraphicsRectItem(left_elevator_x, left_elevator_y, door_width, elevator_height)
        left_door2 = QGraphicsRectItem(left_elevator_x + door_width, left_elevator_y, door_width, elevator_height)
        
        # Right Elevator
        right_elevator_x = 5 * width / 8
        right_elevator_y = 8 * height / 12  # Elevator starts at the first floor (adjusted)
        right_elevator_rect = QRectF(right_elevator_x, right_elevator_y, elevator_width, elevator_height)
        
        # Right Elevator Doors
        right_door1 = QGraphicsRectItem(right_elevator_x, right_elevator_y, door_width, elevator_height)
        right_door2 = QGraphicsRectItem(right_elevator_x + door_width, right_elevator_y, door_width, elevator_height)
        
        # Set colors for doors
        left_door1.setBrush(QBrush(QColor(200, 200, 200)))
        left_door2.setBrush(QBrush(QColor(200, 200, 200)))
        right_door1.setBrush(QBrush(QColor(200, 200, 200)))
        right_door2.setBrush(QBrush(QColor(200, 200, 200)))
        
        # Add doors to scene
        scene.addItem(left_door1)
        scene.addItem(left_door2)
        scene.addItem(right_door1)
        scene.addItem(right_door2)
        
        layout.addWidget(view)
        window.setLayout(layout)
        self.simualtion_window = window
        self.e1_sim_left: QGraphicsRectItem = left_door1
        self.e1_sim_right: QGraphicsRectItem = left_door2
        self.e2_sim_left: QGraphicsRectItem = right_door1
        self.e2_sim_right: QGraphicsRectItem = right_door2
        

    def posToWin(self, pos: float):
        return (-3.0 * pos / 8.0 + 5.0 / 4.0) * 400.0 - 350.0

    def update_simulation_window(self):
        e1_sim_left_x = 0
        e1_sim_right_x = 0
        e2_sim_left_x = 0
        e2_sim_right_x = 0
        door_width = 1 / 8 * 300
        percent_1 = self.elevators[0].getDoorPercentage()
        percent_2 = self.elevators[1].getDoorPercentage()
        self.e1_sim_left.setPos(e1_sim_left_x - door_width * percent_1, self.posToWin(self.elevators[0].currentPos))
        self.e1_sim_right.setPos(e1_sim_right_x + door_width * percent_1, self.posToWin(self.elevators[0].currentPos))
        self.e2_sim_left.setPos(e2_sim_left_x - door_width * percent_2, self.posToWin(self.elevators[1].currentPos))
        self.e2_sim_right.setPos(e2_sim_right_x + door_width * percent_2, self.posToWin(self.elevators[1].currentPos))

        
    # Connect the button to the elevator controller
    def connect(self):
        self.button_dict["-1_up"]["button"].clicked.connect(self.on_B1_up_clicked)
        self.button_dict["1_up"]["button"].clicked.connect(self.on_1_up_clicked)
        self.button_dict["1_down"]["button"].clicked.connect(self.on_1_down_clicked)
        self.button_dict["2_up"]["button"].clicked.connect(self.on_2_up_clicked)
        self.button_dict["2_down"]["button"].clicked.connect(self.on_2_down_clicked)
        self.button_dict["3_down"]["button"].clicked.connect(self.on_3_down_clicked)
    def on_B1_up_clicked(self):
        print("-1_up clicked")
        self.button_dict["-1_up"]["count"] += 1
        if self.button_dict["-1_up"]["state"] == "not pressed":
            self.button_dict["-1_up"]["button"].setStyleSheet("background-color: yellow;")
            self.button_dict["-1_up"]["state"] = "pressed"
        return
    def on_1_down_clicked(self):
        print("1_down clicked")
        self.button_dict["1_down"]["count"] += 1
        if self.button_dict["1_down"]["state"] == "not pressed":
            self.button_dict["1_down"]["button"].setStyleSheet("background-color: yellow;")
            self.button_dict["1_down"]["state"] = "pressed"
        return
    def on_1_up_clicked(self):
        print("1_up clicked")
        self.button_dict["1_up"]["count"] += 1
        if self.button_dict["1_up"]["state"] == "not pressed":
            self.button_dict["1_up"]["button"].setStyleSheet("background-color: yellow;")
            self.button_dict["1_up"]["state"] = "pressed"
        return
    def on_2_up_clicked(self): 
        print("2_up clicked")
        self.button_dict["2_up"]["count"] += 1
        if self.button_dict["2_up"]["state"] == "not pressed":
            self.button_dict["2_up"]["button"].setStyleSheet("background-color: yellow;")
            self.button_dict["2_up"]["state"] = "pressed"
        return
    def on_2_down_clicked(self):
        print("2_down clicked")
        self.button_dict["2_down"]["count"] += 1
        if self.button_dict["2_down"]["state"] == "not pressed":
            self.button_dict["2_down"]["button"].setStyleSheet("background-color: yellow;")
            self.button_dict["2_down"]["state"] = "pressed"
        return
    def on_3_down_clicked(self):
        print("3_down clicked")
        self.button_dict["3_down"]["count"] += 1
        if self.button_dict["3_down"]["state"] == "not pressed":
            self.button_dict["3_down"]["button"].setStyleSheet("background-color: yellow;")
            self.button_dict["3_down"]["state"] = "pressed"
        return
    def updateLCD(self):
        for i in range(4):
            if self.elevators[0].getCurrentFloor() == 0:
                self.outPanels[i]['e1'].setText(str(-1))
            else:
                self.outPanels[i]['e1'].setText(str(self.elevators[0].getCurrentFloor()))
            if self.elevators[1].getCurrentFloor() == 0:
                self.outPanels[i]['e2'].setText(str(-1))
            else:
                self.outPanels[i]['e2'].setText(str(self.elevators[1].getCurrentFloor()))
        return
    
    # Debug Util Function
    def updateButtonText(self):
        for button_name, info in self.button_dict.items():
            # self.button_dict[button_name]["button"].setText(f"{info['state']} E{info['elevatorId']} Count:{info['count']}")
            pass
# if __name__=='__main__':
#     print(ElevatorController("","","").posToWin(3.0))