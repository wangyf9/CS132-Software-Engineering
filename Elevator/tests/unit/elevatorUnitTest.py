import sys
import unittest
from PyQt5.QtWidgets import QApplication
from PyQt5.QtTest import QTest
from PyQt5.QtCore import Qt
from unittest.mock import MagicMock, patch
from src.elevator import Elevator
from src.elevatorState import State
from src.direction import Direction 
from src import NetClient

class TestElevator(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """Initialize the test environment and set class-level variables"""
        cls.app = QApplication(sys.argv)
        pass
    def setUp(self):
        """Initialization of each test case"""
        self.zmqThreadMock = MagicMock(spec=NetClient.ZmqClientThread)
        self.elevator:Elevator = Elevator(elevatorId=1, zmqThread=self.zmqThreadMock)
    def tearDown(self):
        """Cleanup after each test case"""
        self.elevator.close()

    @classmethod
    def tearDownClass(cls):
        """Cleanup work after all test cases are executed"""
        # Ensure the event loop runs long enough to display the window
        cls.app.quit()
        pass

    def test1_reset(self):
        """Test the reset functionality"""
        # Set some initial state
        self.elevator.currentPos = 2.0
        self.elevator.__currentSpeed = 0.1
        self.elevator.currentDirection = Direction.up
        self.elevator.targetFloor = [3]
        self.elevator.doorSpeed = 0.1
        self.elevator.doorInterval = 0.1
        self.elevator.doorOpenFlag = True
        self.elevator.doorCloseFlag = True
        self.elevator.currentState = State.stopped_opening_door

        # Call the method under test
        self.elevator.reset()

        # Check the state after reset
        self.assertEqual(self.elevator.currentPos, 1.0)
        self.assertEqual(self.elevator.__currentSpeed, 0.1)
        self.assertEqual(self.elevator.currentDirection, Direction.wait)
        self.assertEqual(self.elevator.targetFloor, [])
        self.assertEqual(self.elevator.doorSpeed, 0.1)
        self.assertEqual(self.elevator.doorInterval, 0.0)
        self.assertEqual(self.elevator.doorOpenFlag, False)
        self.assertEqual(self.elevator.doorCloseFlag, False)
        self.assertEqual(self.elevator.currentState, State.stopped_door_closed)
    
    def test2_1_move_up_not_arrive(self):
        """Test the move functionality without changing status"""
        initialPos = 1.1
        # Initialize the elevator status
        self.elevator.currentState = State.up
        self.elevator.currentPos = initialPos
        self.elevator.targetFloor = [2]
        self.elevator.move()
        self.assertAlmostEqual(self.elevator.currentPos, initialPos+self.elevator.getCurrentSpeed())
        self.assertEqual(self.elevator.targetFloor, [2])
        self.assertEqual(self.elevator.currentState, State.up)

    def test2_2_move_down_not_arrive(self):
        """Test the move functionality when moving down"""
        initialPos = 2.4
        self.elevator.currentState = State.down
        self.elevator.currentPos = initialPos
        self.elevator.targetFloor = [1]
        self.elevator.move()
        self.assertAlmostEqual(self.elevator.currentPos, initialPos - self.elevator.getCurrentSpeed())
        self.assertEqual(self.elevator.targetFloor, [1])
        self.assertEqual(self.elevator.currentState, State.down)

    def test2_3_move_up_arrive_at_floor_without_multiple_target(self):
        self.elevator.currentState = State.up
        self.elevator.currentDirection = Direction.up
        self.elevator.currentPos = 3.0 - self.elevator.getCurrentSpeed()
        self.elevator.targetFloor = [3]
        self.elevator.move()
        self.assertEqual(self.elevator.currentPos, 3.0)
        self.assertEqual(self.elevator.targetFloor, [])
        self.assertEqual(self.elevator.currentState, State.stopped_opening_door)
        self.assertEqual(self.elevator.currentDirection, Direction.wait)
    
    def test2_4_move_down_arrive_at_floor_with_multiple_target(self):
        self.elevator.currentState = State.down
        self.elevator.currentDirection = Direction.down
        self.elevator.currentPos = 2.0 + self.elevator.getCurrentSpeed()
        self.elevator.targetFloor = [2,1]
        self.elevator.move()
        self.assertAlmostEqual(self.elevator.currentPos, 2.0)
        self.assertEqual(self.elevator.targetFloor, [1])
        self.assertEqual(self.elevator.currentState, State.stopped_opening_door)
        self.assertEqual(self.elevator.currentDirection, Direction.down)

    def test3_1_openingDoor_openFlag_true_closeFlag_false(self):
        """Test opening door when openFlag is True, closeFlag is True, and not changing status"""
        self.elevator.doorOpenFlag = True
        self.elevator.doorCloseFlag = False
        self.elevator.currentState = State.stopped_opening_door
        interval = 0.0
        self.elevator.doorInterval = interval
        self.elevator.openingDoor()
        self.assertFalse(self.elevator.doorOpenFlag)
        self.assertFalse(self.elevator.doorCloseFlag)
        self.assertEqual(self.elevator.doorInterval,interval+self.elevator.doorSpeed)
        self.assertEqual(self.elevator.currentState, State.stopped_opening_door)
    def test3_2_openingDoor_openFlag_false_closeFlag_true(self):
        """Test opening door when openFlag is False, closeFlag is False, and is changing status"""
        self.elevator.doorOpenFlag = False
        self.elevator.doorCloseFlag = True
        self.elevator.currentState = State.stopped_opening_door
        interval = self.elevator.doorOpenTime - self.elevator.doorSpeed
        self.elevator.doorInterval = interval
        self.elevator.openingDoor()
        self.assertFalse(self.elevator.doorOpenFlag)
        self.assertFalse(self.elevator.doorCloseFlag)
        self.assertEqual(self.elevator.doorInterval,0.0)
        self.assertEqual(self.elevator.currentState, State.stopped_door_opened)

    def test4_1_closingDoor_openFlag_true_closeFlag_false(self):
        """Test closing door when openFlag is True, closeFlag is False, and changing status to opening door"""
        self.elevator.doorOpenFlag = True
        self.elevator.doorCloseFlag = False
        self.elevator.currentState = State.stopped_closing_door
        interval = 0.7
        self.elevator.doorInterval = interval
        self.elevator.closingDoor()
        self.assertFalse(self.elevator.doorOpenFlag)
        self.assertFalse(self.elevator.doorCloseFlag)
        self.assertAlmostEqual(self.elevator.doorInterval,0.3)
        self.assertEqual(self.elevator.currentState, State.stopped_opening_door)

    def test4_2_closingDoor_openFlag_false_closeFlag_false(self):
        self.elevator.doorOpenFlag = False
        self.elevator.doorCloseFlag = False
        self.elevator.currentState = State.stopped_closing_door
        interval = 0.7
        self.elevator.doorInterval = interval
        self.elevator.closingDoor()
        self.assertFalse(self.elevator.doorOpenFlag)
        self.assertFalse(self.elevator.doorCloseFlag)
        self.assertAlmostEqual(self.elevator.doorInterval, 0.8)
        self.assertEqual(self.elevator.currentState, State.stopped_closing_door)
    def test4_3_closingDoor_openFlag_false_closeFlag_true(self):
        """Test closing door when openFlag is False, closeFlag is True, and changing status to door closed"""
        self.elevator.doorOpenFlag = False
        self.elevator.doorCloseFlag = True
        self.elevator.currentState = State.stopped_closing_door
        interval = self.elevator.doorCloseTime - self.elevator.doorSpeed
        self.elevator.doorInterval = interval
        self.elevator.closingDoor()
        self.assertFalse(self.elevator.doorOpenFlag)
        self.assertFalse(self.elevator.doorCloseFlag)
        self.assertEqual(self.elevator.doorInterval,0.0)
        self.assertEqual(self.elevator.currentState, State.stopped_door_closed)

    def test5_1_waitForClosingDoor_openFlag_true_closeFlag_true(self):
        """Test door opened(waiting to close) when openFlag is True, closeFlag is True, and changing status to door closed"""
        self.elevator.doorOpenFlag = True
        self.elevator.doorCloseFlag = True
        self.elevator.currentState = State.stopped_door_opened
        interval = 0.3
        self.elevator.doorInterval = interval
        self.elevator.waitForClosingDoor()
        self.assertFalse(self.elevator.doorOpenFlag)
        self.assertFalse(self.elevator.doorCloseFlag)
        self.assertEqual(self.elevator.doorInterval,0.0)
        self.assertEqual(self.elevator.currentState, State.stopped_door_opened)

    def test5_2_waitForClosingDoor_openFlag_false_closeFlag_false_larger_waiting(self):
        """Test door opened(waiting to close) when openFlag is False, closeFlag is False, and changing status to door closed"""
        self.elevator.doorOpenFlag = False
        self.elevator.doorCloseFlag = False
        self.elevator.currentState = State.stopped_door_opened
        interval = Elevator.elevatorWaitTime - self.elevator.doorSpeed
        self.elevator.doorInterval = interval
        self.elevator.waitForClosingDoor()
        self.assertFalse(self.elevator.doorOpenFlag)
        self.assertFalse(self.elevator.doorCloseFlag)
        self.assertEqual(self.elevator.doorInterval,0.0)
        self.assertEqual(self.elevator.currentState, State.stopped_closing_door)
    
    def test5_3_waitForClosingDoor_openFlag_false_closeFlag_false_less_waiting(self):
        self.elevator.doorOpenFlag = False
        self.elevator.doorCloseFlag = False
        self.elevator.currentState = State.stopped_door_opened
        interval = 0.3
        self.elevator.doorInterval = interval
        self.elevator.waitForClosingDoor()
        self.assertFalse(self.elevator.doorOpenFlag)
        self.assertFalse(self.elevator.doorCloseFlag)
        self.assertEqual(self.elevator.doorInterval,0.4)
        self.assertEqual(self.elevator.currentState, State.stopped_door_opened)
    
    def test5_4waitForClosingDoor_openFlag_false_closeFlag_true(self):
        self.elevator.doorOpenFlag = False
        self.elevator.doorCloseFlag = True
        self.elevator.currentState = State.stopped_door_opened
        interval = 0.3
        self.elevator.doorInterval = interval
        self.elevator.waitForClosingDoor()
        self.assertFalse(self.elevator.doorOpenFlag)
        self.assertFalse(self.elevator.doorCloseFlag)
        self.assertEqual(self.elevator.doorInterval,0.0)
        self.assertEqual(self.elevator.currentState, State.stopped_closing_door)
    
    def test6_floor_arrived_message_up(self):
        """Test the floorArrivedMessage when direction is up"""
        self.elevator.currentDirection = Direction.up
        self.elevator.floorArrivedMessage(floor=2, eid=1)

        expected_message = "floor_arrived@2#1"
        self.zmqThreadMock.sendMsg.assert_called_once_with(expected_message)

    def test7_door_opened_message(self):
        """Test the doorOpenedMessage functionality"""
        self.elevator.doorOpenedMessage(eid=1)
        expected_message = "door_opened#1"
        self.zmqThreadMock.sendMsg.assert_called_once_with(expected_message)

    def test8_door_closed_message(self):
        """Test the doorClosedMessage functionality"""
        self.elevator.doorClosedMessage(eid=1)
        expected_message = "door_closed#1"
        self.zmqThreadMock.sendMsg.assert_called_once_with(expected_message)

    def test9_1_checkTargetFloor_none(self):
        """Test the check target floor functionality: no target floor"""
        self.elevator.currentState = State.stopped_door_closed
        self.elevator.targetFloor = []
        res = self.elevator.checkTargetFloor()
        self.assertFalse(res)
    def test9_2_checkTargetFloor_changeToUp(self): 
        """Test the check target floor functionality: target floor upwards""" 
        self.elevator.currentDirection = Direction.up
        self.elevator.currentState = State.stopped_door_closed
        self.elevator.targetFloor = [3,2]
        self.elevator.currentPos = 1.0
        res = self.elevator.checkTargetFloor()
        self.assertTrue(res)
        self.assertEqual(self.elevator.currentState, State.up)
        self.assertEqual(self.elevator.targetFloor, [2,3])
    def test9_3_checkTargetFloor_changeToDown(self):
        """Test the check target floor functionality: target floor downwards""" 
        self.elevator.currentDirection = Direction.down
        self.elevator.currentState = State.stopped_door_closed     
        self.elevator.targetFloor = [2,1]
        self.elevator.currentPos = 3.0
        res = self.elevator.checkTargetFloor()
        self.assertTrue(res)
        self.assertEqual(self.elevator.currentState, State.down)
        self.assertEqual(self.elevator.targetFloor, [2,1])
    def test9_4_checkTargetFloor_currentFloor(self):
        """Test the check target floor functionality: target floor current"""  
        self.elevator.currentDirection = Direction.up
        self.elevator.currentState = State.stopped_door_closed   
        self.elevator.targetFloor = [1,2]
        self.elevator.currentPos = 1.0

        res = self.elevator.checkTargetFloor()

        self.assertTrue(res)
        expected_message = "floor_arrived@1#1"
        self.zmqThreadMock.sendMsg.assert_called_once_with(expected_message)
        self.assertEqual(self.elevator.currentState, State.stopped_opening_door)
        self.assertEqual(self.elevator.targetFloor, [2])
        self.assertEqual(self.elevator.currentDirection, Direction.up)

    def test10_checkOpenDoor_whenDoorOpenFlagTrue(self):
       
        self.elevator.doorOpenFlag = True
        self.elevator.checkOpenDoor()
        self.assertFalse(self.elevator.doorOpenFlag)
        self.assertEqual(self.elevator.currentState, State.stopped_opening_door)

    def test11_getCurrentFloor(self):
        self.elevator.currentPos = 0.4
        self.assertEqual(self.elevator.getCurrentFloor(), 0)    
        self.elevator.currentPos = 1.0
        self.assertEqual(self.elevator.getCurrentFloor(), 1)

    def test12_1_addTargetFloor_whenFloorAlreadyInTarget(self):
        self.elevator.targetFloor = [2, 3]
        result = self.elevator.addTargetFloor(2)
        self.assertEqual(result, "OK", "Should return 'OK' if floor is already in targetFloor")
        self.assertIn(2, self.elevator.targetFloor, "Floor 2 should still be in targetFloor")

    def test12_2_addTargetFloor_whenDirectionWaitAndFloorAbove(self):
        self.elevator.currentPos = 1
        self.elevator.currentDirection = Direction.wait
        self.elevator.addTargetFloor(3)
        self.assertEqual(self.elevator.currentDirection, Direction.up, "Direction should be set to up")
        self.assertIn(3, self.elevator.targetFloor, "Floor 3 should be added to targetFloor")

    def test12_3_addTargetFloor_whenDirectionWaitAndFloorBelow(self):
        self.elevator.currentPos = 3
        self.elevator.currentDirection = Direction.wait
        self.elevator.addTargetFloor(1)
        self.assertEqual(self.elevator.currentDirection, Direction.down, "Direction should be set to down")
        self.assertIn(1, self.elevator.targetFloor, "Floor 1 should be added to targetFloor")

    def test13_setOpenDoorFlag(self):
        self.elevator.doorOpenFlag = False
        self.elevator.setOpenDoorFlag()
        self.assertTrue(self.elevator.doorOpenFlag, "doorOpenFlag should be set to True")

    def test14_setCloseDoorFlag(self):
        self.elevator.doorCloseFlag = False
        self.elevator.setCloseDoorFlag()
        self.assertTrue(self.elevator.doorCloseFlag, "doorCloseFlag should be set to True")

    def test15_1_getDoorPercentage_whenStoppedClosingDoor(self):
        self.elevator.currentState = State.stopped_closing_door
        self.elevator.doorInterval = 0.2
        expected_percentage = 0.8
        self.assertEqual(self.elevator.getDoorPercentage(), expected_percentage, "Door percentage should be 0.5 when door is halfway through closing")

    def test15_2_getDoorPercentage_whenStoppedOpeningDoor(self):
        self.elevator.currentState = State.stopped_opening_door
        self.elevator.doorInterval = 0.1
        expected_percentage = 0.1
        self.assertEqual(self.elevator.getDoorPercentage(), expected_percentage, "Door percentage should be 0.5 when door is halfway through opening")

    def test15_3_getDoorPercentage_whenStoppedDoorOpened(self):
        self.elevator.currentState = State.stopped_door_opened
        expected_percentage = 1.0
        self.assertEqual(self.elevator.getDoorPercentage(), expected_percentage, "Door percentage should be 1.0 when door is fully opened")

    def test15_4_getDoorPercentage_whenOtherStates(self):
        self.elevator.currentState = State.up
        expected_percentage = 0.0
        self.assertEqual(self.elevator.getDoorPercentage(), expected_percentage, "Door percentage should be 0.0 when elevator is moving")

    def test16_update(self):
        """Test the update functionality"""
        with patch.object(self.elevator, 'move') as mock_move:
            self.elevator.currentState = State.up
            self.elevator.update()
            mock_move.assert_called_once()
        
        with patch.object(self.elevator, 'openingDoor') as mock_openingDoor:
            self.elevator.currentState = State.stopped_opening_door
            self.elevator.update()
            mock_openingDoor.assert_called_once()
        
        with patch.object(self.elevator, 'waitForClosingDoor') as mock_waitForClosingDoor:
            self.elevator.currentState = State.stopped_door_opened
            self.elevator.update()
            mock_waitForClosingDoor.assert_called_once()
        
        with patch.object(self.elevator, 'closingDoor') as mock_closingDoor:
            self.elevator.currentState = State.stopped_closing_door
            self.elevator.update()
            mock_closingDoor.assert_called_once()
        
        with patch.object(self.elevator, 'checkTargetFloor') as mock_checkTargetFloor:
            self.elevator.currentState = State.stopped_door_closed
            self.elevator.update()
            mock_checkTargetFloor.assert_called_once()
if __name__ == "__main__":
    # app = QApplication(sys.argv)
    unittest.main(verbosity=2)
    # app.quit()

