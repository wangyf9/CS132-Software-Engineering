from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QMessageBox,QWidget
from PyQt5.QtCore import QTimer, Qt

from .elevatorState import State
from .direction import Direction
from . import NetClient
# Elevator
class Elevator(QWidget):
    elevatorWaitTime: float = 3.0
    doorOpenTime: float = 1.0
    doorCloseTime: float = 1.0
    def __init__(self,elevatorId:int,zmqThread:NetClient.ZmqClientThread) -> None:
        super().__init__()
        self.elevatorId = elevatorId
        self.zmqThread = zmqThread
        # Move related variables
        self.currentPos: float = 1.0 # Initially stop at floor 1
        self.__currentSpeed = 0.05
        self.currentDirection: Direction = Direction.wait # Direction record
        self.targetFloor: list[int] = []
        # Door related variables
        self.doorSpeed: float = 0.1
        self.doorInterval: float = 0.0
        self.doorOpenFlag: bool = False
        self.doorCloseFlag: bool = False
        # State
        self.currentState: State = State.stopped_door_closed
        # Init Ui
        self.setupUi()
        return
# State transfer functions
    def reset(self) -> None:
        # Move related variables
        self.currentPos: float = 1.0 # Initially stop at floor 1
        self.__currentSpeed = 0.1
        self.currentDirection: Direction = Direction.wait # Direction record
        self.targetFloor: list[int] = []
        # Door related variables
        self.doorSpeed: float = 0.1
        self.doorInterval: float = 0.0
        self.doorOpenFlag: bool = False
        self.doorCloseFlag: bool = False
        # State
        self.currentState: State = State.stopped_door_closed
        # Reset UI
        self.resetUi()
        return
        
    def move(self) -> None:
        if self.currentState == State.up:
            self.currentPos += self.__currentSpeed
            self.targetFloor.sort(reverse=False)
        elif self.currentState == State.down:
            self.currentPos -= self.__currentSpeed
            self.targetFloor.sort(reverse=True)

        # Check if the elevator has reached the target floor
        if self.currentPos > self.targetFloor[0]-0.01 and self.currentPos < self.targetFloor[0]+0.01:
            # Arrive! transfer state to stopped_door_opening
            arrivedFloor = self.targetFloor.pop(0)
            self.currentPos = float(arrivedFloor)
            self.floorArrivedMessage(arrivedFloor,self.elevatorId)
            #print("elevator: ",self.elevatorId," arrived at floor: ",arrivedFloor)
            # Clear floor ui
            self.clear_floor_ui(arrivedFloor)
            #print("door opening #"+str(self.elevatorId))
            self.currentState = State.stopped_opening_door
            if len(self.targetFloor) == 0:
                #print("direction reset to wait")
                self.currentDirection = Direction.wait
            
        return

    def openingDoor(self) -> None:
        # Ignore Flag
        if self.doorOpenFlag:
            self.doorOpenFlag = False
        if self.doorCloseFlag:
            self.doorCloseFlag = False
        # Keep Opening the door
        self.doorInterval += self.doorSpeed
        if self.doorInterval >= Elevator.doorOpenTime:
            self.doorInterval = 0.0
            #print("door opened #"+str(self.elevatorId))
            self.doorOpenedMessage(self.elevatorId)
            self.currentState = State.stopped_door_opened
        return
    def closingDoor(self) -> None:
        # Ignore Repeated Close Flag
        if self.doorCloseFlag:
            self.doorCloseFlag = False
        # Pay attention to Open Flag
        if self.doorOpenFlag:
            # If press open button, reopen the door immediately
            self.doorInterval = Elevator.doorOpenTime - self.doorInterval
            self.doorOpenFlag = False
            #print("door opening #"+str(self.elevatorId))
            self.currentState = State.stopped_opening_door
            return
        # Keep Closing the door
        self.doorInterval += self.doorSpeed
        if self.doorInterval >= Elevator.doorCloseTime:
            self.doorInterval = 0.0
            #print("door closed #"+str(self.elevatorId))
            self.doorClosedMessage(self.elevatorId)
            self.currentState = State.stopped_door_closed
        return

    def waitForClosingDoor(self) -> None:
        # Open Flag is on, keep opened
        if self.doorOpenFlag:
            self.doorInterval = 0.0
            self.doorOpenFlag = False
            self.doorCloseFlag = False
            return
        # Close? transfer state to closing door
        if self.doorCloseFlag:
            self.doorInterval = 0.0
            self.currentState = State.stopped_closing_door
            self.doorCloseFlag = False
            return
        
        # Keep waiting
        self.doorInterval += self.doorSpeed
        if self.doorInterval >= Elevator.elevatorWaitTime:
            self.doorInterval = 0.0
            #print("door closing #"+str(self.elevatorId))
            self.currentState = State.stopped_closing_door
            
        return
    
# Sending Msg
    def floorArrivedMessage(self, floor: int, eid: int) -> None:
        directions = ["up", "down", ""]
        floors = ["-1", "1", "2", "3"]
        elevators = ["#1", "#2"]

        direction_str = directions[self.currentDirection.value]
        floor_str = floors[floor]
        elevator_str = elevators[eid - 1]  # Adjusting elevator index to start from 1

        message = f"floor_arrived@{floor_str}{elevator_str}"
        #print(message)
        self.zmqThread.sendMsg(message)

    def doorOpenedMessage(self,eid: int) -> None:
        elevators = ["#1", "#2"]
        elevator_str = elevators[eid - 1]
        message = f"door_opened{elevator_str}"
        self.zmqThread.sendMsg(message)
        
    def doorClosedMessage(self,eid: int) -> None:
        elevators = ["#1", "#2"]
        elevator_str = elevators[eid - 1]
        message = f"door_closed{elevator_str}"
        self.zmqThread.sendMsg(message)
    
    def checkTargetFloor(self) -> bool:
        if len(self.targetFloor) == 0:
            return False
        # If there is a target floor, begin to move
        if self.targetFloor[0] > self.currentPos:
            #[3,2]
            self.currentState = State.up
            self.targetFloor.sort(reverse=(self.currentDirection == Direction.down))
            #[2,3]
        elif self.targetFloor[0] < self.currentPos:
            #[2,1]
            self.currentState = State.down
            self.targetFloor.sort(reverse=(self.currentDirection == Direction.down))
            #[1,2]
        elif self.targetFloor[0] == self.currentPos:
            self.targetFloor.remove(int(self.currentPos))
            self.clear_floor_ui(floor=int(self.currentPos))
            self.floorArrivedMessage(self.getCurrentFloor(),self.elevatorId)
            self.currentState = State.stopped_opening_door
        return True   
    def checkOpenDoor(self) -> None:
        if self.doorOpenFlag:
            self.doorOpenFlag = False
            self.currentState = State.stopped_opening_door
        return


# Util function inside class
    def getCurrentFloor(self) -> int:
        return round(self.currentPos)
    
            
# Utility Functions for controller & button panel inside this elevator
    # Reveive outer request from controller
    def addTargetFloor(self, floor: int) -> str:
        if floor in self.targetFloor:
            return "OK"
        # Determine the direction of the elevator when adding the first target floor
        if self.currentDirection == Direction.wait:
            if(self.currentPos < floor):
                self.currentDirection = Direction.up # up
            elif(self.currentPos > floor): # down
                self.currentDirection = Direction.down
        self.targetFloor.append(floor)
        self.targetFloor.sort(reverse=(self.currentDirection == Direction.down))
        #print("current target floor: ",self.targetFloor)
        return "OK"
    def setOpenDoorFlag(self) -> None:
        self.doorOpenFlag = True
        return
    def setCloseDoorFlag(self) -> None:
        self.doorCloseFlag = True
        return
    def getDoorPercentage(self) -> float:
        # opened -> 1.0; closed -> 0.0
        if self.currentState == State.stopped_closing_door:
            return 1.0 - self.doorInterval/Elevator.doorCloseTime
        elif self.currentState == State.stopped_opening_door:
            return self.doorInterval/Elevator.doorOpenTime
        elif self.currentState == State.stopped_door_opened:
            return 1.0
        else:
            return 0.0
    def update(self) -> None:
        self.updateUi()
        if self.currentState == State.up or self.currentState == State.down:
            #print("elevator: ",self.elevatorId," is moving",self.currentState.name)
            self.move()
            pass
        elif self.currentState == State.stopped_opening_door:
            self.openingDoor()
            pass
        elif self.currentState == State.stopped_door_opened:
            self.waitForClosingDoor()
            pass
        elif self.currentState == State.stopped_closing_door:
            self.closingDoor()
            pass
        elif self.currentState == State.stopped_door_closed:
            # Find if Controller give new command to this elevator
            hasTarget = self.checkTargetFloor()
            # If door is already closed， user can still exit or enter by request opening door.
            if not hasTarget:
                self.checkOpenDoor()
            pass
        return
    

    """UI Related functions"""
    def setupUi(self):
        self.setObjectName("InsideWidget")
        self.setGeometry(500+self.elevatorId*300,100,222,289)
        # Ui related flag
        self.fB1_activeFlag = False
        self.f1_activeFlag = False
        self.f2_activeFlag = False
        self.f3_activeFlag = False

        layout = QtWidgets.QVBoxLayout(self)
        self.label = QtWidgets.QLabel("E#" + str(self.elevatorId))
        layout.addWidget(self.label)
        # self.label2 = QtWidgets.QLabel("State#" + str(self.elevatorId))
        self.label2 = QtWidgets.QLabel()
        layout.addWidget(self.label2)

        # Use QLabel instead of QLCDNumber
        self.lcd_label = QtWidgets.QLabel()
        self.set_lcd_value(1)  # default value is 1
        font = QtGui.QFont()
        font.setFamily("Times New Roman")
        font.setPointSize(20)
        self.lcd_label.setFont(font)
        self.lcd_label.setAlignment(QtCore.Qt.AlignCenter)
        self.lcd_label.setStyleSheet("border: 2px solid black; background-color: lightgray;")
        layout.addWidget(self.lcd_label)
        button_layout = QtWidgets.QVBoxLayout()
        layout.addLayout(button_layout)

        self.f3 = QtWidgets.QPushButton("3")
        self.f3.clicked.connect(self.on_f3_clicked)
        button_layout.addWidget(self.f3)

        self.f2 = QtWidgets.QPushButton("2")
        self.f2.clicked.connect(self.on_f2_clicked)
        button_layout.addWidget(self.f2)

        self.f1 = QtWidgets.QPushButton("1")
        self.f1.clicked.connect(self.on_f1_clicked)
        button_layout.addWidget(self.f1)

        self.fB1 = QtWidgets.QPushButton("-1")
        self.fB1.clicked.connect(self.on_fB1_clicked)
        button_layout.addWidget(self.fB1)

        control_layout = QtWidgets.QHBoxLayout()
        layout.addLayout(control_layout)

        self.open = QtWidgets.QPushButton("<|>")
        self.open.clicked.connect(self.on_open_clicked)
        control_layout.addWidget(self.open)

        self.closeButton = QtWidgets.QPushButton(">|<")
        self.closeButton.clicked.connect(self.on_close_clicked)
        control_layout.addWidget(self.closeButton)

        # ReTranslate UI
        _translate = QtCore.QCoreApplication.translate
        self.setWindowTitle(_translate("InsideWidget", "Elevator#" + str(self.elevatorId)))
        self.label.setText(_translate("InsideWidget", "E#" + str(self.elevatorId)))

    def on_fB1_clicked(self):
        if self.fB1_activeFlag:
            return
        else:
            if self.floorbutton_clicked(self.fB1,0):
                self.fB1_activeFlag = True

    def on_f1_clicked(self):
        if self.f1_activeFlag:
            return
        else:
            if self.floorbutton_clicked(self.f1,1):
                self.f1_activeFlag = True

    def on_f2_clicked(self):
        if self.f2_activeFlag:
            return
        else:
            if self.floorbutton_clicked(self.f2,2):
                self.f2_activeFlag = True

    def on_f3_clicked(self):
        if self.f3_activeFlag:
            return
        else:
            if self.floorbutton_clicked(self.f3,3):
                self.f3_activeFlag = True

    def floorbutton_clicked(self, button: QtWidgets.QPushButton, floor: int) -> bool:
        if self.currentPos < floor:
            direction = Direction.up  # up
        elif self.currentPos > floor:  # down
            direction = Direction.down
        else:
            direction = Direction.wait  # same
        if self.currentDirection == direction or self.currentDirection == Direction.wait:
            if self.getCurrentFloor() == floor:
                return False
            button.setStyleSheet("background-color: yellow;")
            self.addTargetFloor(floor)  # 如果电梯向上，从小到大[2,3],反之[2,1]
            return True
        else:
            return False

    def resetUi(self):
        self.fB1_activeFlag = False
        self.f1_activeFlag = False
        self.f2_activeFlag = False
        self.f3_activeFlag = False
        self.fB1.setStyleSheet("background-color: none;")
        self.f1.setStyleSheet("background-color: none;")
        self.f2.setStyleSheet("background-color: none;")
        self.f3.setStyleSheet("background-color: none;")
        self.set_lcd_value(1)

    def updateUi(self):
        if self.getCurrentFloor() == 0:
            self.set_lcd_value(-1)
        else:
            self.set_lcd_value(self.getCurrentFloor())

    def clear_floor_ui(self, floor: int):
        if floor == 0:
            self.fB1_activeFlag = False
            self.fB1.setStyleSheet("background-color: none;")
        elif floor == 1:
            self.f1_activeFlag = False
            self.f1.setStyleSheet("background-color: none;")
        elif floor == 2:
            self.f2_activeFlag = False
            self.f2.setStyleSheet("background-color: none;")
        elif floor == 3:
            self.f3_activeFlag = False
            self.f3.setStyleSheet("background-color: none;")

    def on_open_clicked(self):
        self.setOpenDoorFlag()

    def on_close_clicked(self):
        self.setCloseDoorFlag()

    # Other util functions

    def set_lcd_value(self, value):
        self.lcd_label.setText(str(value))

    def getCurrentSpeed(self) -> float:
        return self.__currentSpeed
