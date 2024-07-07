import sys
import unittest
from unittest.mock import Mock, patch
from PyQt5.QtTest import QTest
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication,QWidget
from src.elevatorController import ElevatorController
from src.elevator import Elevator
from src.elevatorState import State
from src.direction import Direction 
from src import NetClient

class ElevatorControllerTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """Initialize the test environment and set class-level variables"""
        cls.app = QApplication(sys.argv)
        pass
    def setUp(self):
        self.zmqThread = Mock(spec=NetClient.ZmqClientThread)
        self.elevator1 = Elevator(1,self.zmqThread)
        self.elevator2 = Elevator(2,self.zmqThread)
        self.controller = ElevatorController(self.zmqThread, self.elevator1, self.elevator2)
        # window 1~3 are the windows for the outside panel 
        self.window1 = QWidget()
        self.window2 = QWidget()
        self.window3 = QWidget()  
        self.window4 = QWidget()
        self.simulation_window = QWidget() 
        self.controller = ElevatorController(self.zmqThread,self.elevator1,self.elevator2)
        self.controller.create_window(self.window1,"fB1", up=True, down=False)
        self.controller.create_window(self.window2,"f1", up=True, down=True)
        self.controller.create_window(self.window3,"f2", up=True, down=True)
        self.controller.create_window(self.window4,"f3", up=False, down=True)
        self.controller.create_simulation_window(self.simulation_window)
        self.controller.create_button_dict()
        self.controller.connect()

    def tearDown(self):
        """Cleanup after each test case"""
        self.controller.reset()
        pass
    @classmethod
    def tearDownClass(cls):
        """Cleanup work after all test cases are executed"""
        # Ensure the event loop runs long enough to display the window
        cls.app.quit()
        pass
    
    def test_parseInput_open_door_1(self):
        self.controller.parseInput("open_door#1")
        self.assertTrue(self.elevator1.doorOpenFlag)

    def test_parseInput_open_door_2(self):
        self.controller.parseInput("open_door#2")
        self.assertTrue(self.elevator2.doorOpenFlag)

    def test_parseInput_close_door_1(self):
        self.controller.parseInput("close_door#1")
        self.assertTrue(self.elevator1.doorCloseFlag)

    def test_parseInput_close_door_2(self):
        self.controller.parseInput("close_door#2")
        self.assertTrue(self.elevator2.doorCloseFlag)
    
    def test_parseInput_call_up_B1(self):
        self.controller.parseInput("call_up@-1")
        self.assertEqual(self.controller.button_dict["-1_up"]["state"],"pressed")

    def test_parseInput_call_up_1(self):
        self.controller.parseInput("call_up@1")
        self.assertEqual(self.controller.button_dict["1_up"]["state"],"pressed")

    def test_parseInput_call_up_2(self):
        self.controller.parseInput("call_up@2")
        self.assertEqual(self.controller.button_dict["2_up"]["state"],"pressed")

    def test_parseInput_call_down_1(self):
        self.controller.parseInput("call_down@1")
        self.assertEqual(self.controller.button_dict["1_down"]["state"],"pressed")

    def test_parseInput_call_down_2(self):
        self.controller.parseInput("call_down@2")
        self.assertEqual(self.controller.button_dict["2_down"]["state"],"pressed")

    def test_parseInput_call_down_3(self):
        self.controller.parseInput("call_down@3")
        self.assertEqual(self.controller.button_dict["3_down"]["state"],"pressed")

    def test_parseInput_select_floor_e1_B1(self):
        self.controller.parseInput("select_floor@-1#1")
        self.assertEqual(self.elevator1.fB1_activeFlag,True)
    def test_parseInput_select_floor_e1_1(self):
        self.controller.parseInput("select_floor@1#1")
        self.assertEqual(self.elevator1.f1_activeFlag,False)
    def test_parseInput_select_floor_e1_2(self):
        self.controller.parseInput("select_floor@2#1")
        self.assertEqual(self.elevator1.f2_activeFlag,True)
    def test_parseInput_select_floor_e1_3(self):
        self.controller.parseInput("select_floor@3#1")
        self.assertEqual(self.elevator1.f3_activeFlag,True)
    def test_parseInput_select_floor_e2_B1(self):
        self.controller.parseInput("select_floor@-1#2")
        self.assertEqual(self.elevator2.fB1_activeFlag,True)
    def test_parseInput_select_floor_e2_1(self):
        self.controller.parseInput("select_floor@1#2")
        self.assertEqual(self.elevator2.f1_activeFlag,False)
    def test_parseInput_select_floor_e2_2(self):
        self.controller.parseInput("select_floor@2#2")
        self.assertEqual(self.elevator2.f2_activeFlag,True)
    def test_parseInput_select_floor_e2_3(self):
        self.controller.parseInput("select_floor@3#2")
        self.assertEqual(self.elevator2.f3_activeFlag,True)
    def test_parseInput_reset(self):
        # Init some state
        self.elevator1.currentPos = 3.0
        self.elevator1.addTargetFloor(1)
        self.controller.button_dict["1_up"]["state"] = "pressed"
        self.controller.parseInput("reset")
        self.assertEqual(self.elevator1.currentPos,1.0)
        self.assertEqual(self.controller.button_dict["1_up"]["state"],"not pressed")
        self.assertEqual(self.elevator1.targetFloor,[])

    def test_getNearestStopElevator(self):
        self.elevator1.currentState = State.stopped_door_closed
        self.elevator1.targetFloor = []
        self.elevator1.getCurrentFloor = lambda: 1
        
        self.elevator2.currentState = State.stopped_door_closed
        self.elevator2.targetFloor = []
        self.elevator2.getCurrentFloor = lambda: 3
        
        dist = [99, 99]
        self.controller.getNearestStopElevator(2, dist)
        self.assertEqual(dist, [1, 1])
        
    def test_getNearestElevatorWithDirect(self):
        self.elevator1.currentPos = 1.0
        self.elevator1.currentDirection = Direction.up
        
        self.elevator2.currentPos = 2.6
        self.elevator2.currentDirection = Direction.down
        
        dist = [99, 99]
        self.controller.getNearestElevatorWithDirect(2, Direction.up, dist)
        self.assertEqual(dist[0], 1)
        self.assertEqual(dist[1], 99)
 
        dist = [99, 99]
        self.controller.getNearestElevatorWithDirect(2, Direction.down, dist)
        self.assertEqual(dist[0], 99)
        self.assertAlmostEqual(dist[1], 0.6)

        self.elevator2.currentPos = 2.4
        self.elevator2.currentDirection = Direction.down
        dist = [99, 99]
        self.controller.getNearestElevatorWithDirect(2, Direction.down, dist)
        self.assertEqual(dist[0], 99)
        self.assertAlmostEqual(dist[1], 99)


        
    def test_is_elevator_idle_at_floor(self):
        self.elevator1.currentState = State.stopped_door_closed
        self.elevator1.targetFloor = []
        self.elevator1.getCurrentFloor = lambda: 1
        
        self.assertTrue(self.controller.is_elevator_idle_at_floor(0, 1))
        self.assertFalse(self.controller.is_elevator_idle_at_floor(0, 2))
        
    def test_getElevatorIdleAtSameFloor(self):
        self.elevator1.currentState = State.stopped_door_closed
        self.elevator1.targetFloor = []
        self.elevator1.getCurrentFloor = lambda: 1
        
        self.elevator2.currentState = State.up
        self.elevator2.targetFloor = [3]
        self.elevator2.getCurrentFloor = lambda: 1
        
        dist = [99, 99]
        self.controller.getElevatorIdleAtSameFloor(1, dist)
        self.assertEqual(dist, [0, 99])
        
    def test_tryAssignElevatorId(self):
        self.elevator1.currentState = State.stopped_door_closed
        self.elevator1.targetFloor = []
        self.elevator1.getCurrentFloor = lambda: 1
        
        self.elevator2.currentState = State.stopped_door_closed
        self.elevator2.targetFloor = []
        self.elevator2.getCurrentFloor = lambda: 3
        
        id = self.controller.tryAssignElevatorId(2, Direction.up)
        self.assertEqual(id, 0)
        
    def test_assignTarget(self):
        self.elevator1.addTargetFloor = lambda x: "OK" if x == 3 else "FAIL"
        
        self.assertTrue(self.controller.assignTarget(0, 3))
        self.assertFalse(self.controller.assignTarget(0, 4))
        
        self.assertFalse(self.controller.assignTarget(-1, 3))

    def test_floorArrivedMessage(self):
        # Test case: direction="up", floor=1 (which corresponds to "1"), eid=0 (elevator "#1"), count=2
        direction = "up"
        floor = 1
        eid = 0
        count = 2
        expected_message = "up_floor_arrived@1#1"
        self.controller.floorArrivedMessage(direction, floor, eid, count)
        # Assert zmqThread.sendMsg was called exactly 'count' times with the expected message
        self.assertEqual(self.zmqThread.sendMsg.call_count, count, "sendMsg should be called 'count' times")
        self.zmqThread.sendMsg.assert_called_with(expected_message)
        # Reset mock for next test case
        self.zmqThread.reset_mock()
   
if __name__ == '__main__':
    unittest.main()