import unittest
from src import Server
import time
import sys

def testing_serial(server: Server.ZmqServerThread, msgs: list[str], intervals: list[int]):
    for msg, interval in zip(msgs, intervals):
        server.send_string(server.bindedClient, msg)
        time.sleep(interval)

class DoorFunctionalTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.my_server = Server.ZmqServerThread()
        while True:
            if len(cls.my_server.clients_addr) == 0:
                continue
            elif len(cls.my_server.clients_addr) >= 2:
                print('more than 1 client address stored. server will exit')
                sys.exit()
            else:
                addr = list(cls.my_server.clients_addr)[0]
                msg = input(f"Initiate evaluation for {addr}?: (y/n)\n")
                if msg == 'y':
                    cls.my_server.bindedClient = addr
                    break
        print("[Test] Test Environment Initialized")

    def setUp(self):
        DoorFunctionalTest.my_server.send_string(DoorFunctionalTest.my_server.bindedClient, "reset")
        time.sleep(1)

    def tearDown(self):
        """Cleanup after each test case"""
        
        DoorFunctionalTest.my_server.send_string(DoorFunctionalTest.my_server.bindedClient, "reset")  # Reset the client
        DoorFunctionalTest.my_server.e1_buffer = []  # Clear e1_buffer
        DoorFunctionalTest.my_server.e2_buffer = []  # Clear e2_buffer
        print("_"*50)
        time.sleep(1)
        
    @classmethod
    def tearDownClass(cls):
        """Cleanup work after all test cases are executed"""
        DoorFunctionalTest.my_server.send_string(DoorFunctionalTest.my_server.bindedClient, "reset")
        DoorFunctionalTest.my_server.e1_buffer = []  # Clear e1_buffer
        DoorFunctionalTest.my_server.e2_buffer = []  # Clear e2_buffer
        time.sleep(1)
        print("[Test] Test Environment Cleaned")

    def assert_messages_in_order(self, buffer, expected_msgs):
        buffer_copy = buffer[:]
        for msg in expected_msgs:
            if msg in buffer_copy:
                buffer_copy.remove(msg)
            else:
                self.fail(f"Message '{msg}' not found in buffer")
        return buffer_copy

    def test_door_function1(self):
        # Passenger A at the first floor presses the external up button, the door of Elevator 1 opens, 
        # Passenger A enters and presses the internal button 2.
        # When the door is about to close, click the open door button, the door opens.
        # Wait for the door to close again, Elevator 1 goes up, Passenger A arrives at the second floor.
        msgs = ["call_up@1", "select_floor@2#1", "open_door#1"]
        intervals = [0.5, 4.8, 13]
        testing_serial(DoorFunctionalTest.my_server, msgs, intervals)
        expected_msgs = ["floor_arrived@1#1", "up_floor_arrived@1#1", "door_opened#1", "door_opened#1",
                         "door_closed#1","floor_arrived@2#1", "door_opened#1", "door_closed#1"]
        DoorFunctionalTest.my_server.e1_buffer = self.assert_messages_in_order(DoorFunctionalTest.my_server.e1_buffer, expected_msgs)
        assert not DoorFunctionalTest.my_server.e1_buffer, "e1_buffer is not empty at the end of the test"
        assert not DoorFunctionalTest.my_server.e2_buffer, "e2_buffer is not empty at the end of the test"

    def test_door_function2(self):
        # Passenger A at the first floor presses the external up button, the door of Elevator 1 opens,
        # Passenger A enters and presses the internal button 2.
        # While the door is open and waiting, click the open door button 3 times in a row, the door stays open.
        # Wait for the door to close again, Elevator 1 goes up, Passenger A arrives at the second floor.
        msgs = ["call_up@1", "select_floor@2#1","open_door#1","open_door#1","open_door#1"]
        intervals = [0.5, 3, 1, 1 ,13]
        testing_serial(DoorFunctionalTest.my_server, msgs, intervals)
        expected_msgs = ["floor_arrived@1#1", "up_floor_arrived@1#1", "door_opened#1", 
                        "door_closed#1","floor_arrived@2#1", "door_opened#1", "door_closed#1",]
        DoorFunctionalTest.my_server.e1_buffer = self.assert_messages_in_order(DoorFunctionalTest.my_server.e1_buffer, expected_msgs)
        assert not DoorFunctionalTest.my_server.e1_buffer, "e1_buffer is not empty at the end of the test"
        assert not DoorFunctionalTest.my_server.e2_buffer, "e2_buffer is not empty at the end of the test"

    def test_door_function3(self):
        # Passenger A at the first floor presses the external up button, the door of Elevator 1 opens, 
        # Passenger A enters and presses the internal button 2.
        # When the door is about to open, click the close door button, the door continues to open.
        # Wait for the door to close again, Elevator 1 goes up, Passenger A arrives at the second floor.
        msgs = ["call_up@1","close_door#1","select_floor@2#1"]
        intervals = [0.5, 0, 13]
        testing_serial(DoorFunctionalTest.my_server, msgs, intervals)
        expected_msgs = ["floor_arrived@1#1", "up_floor_arrived@1#1", "door_opened#1", 
                        "door_closed#1","floor_arrived@2#1", "door_opened#1", "door_closed#1",]
        DoorFunctionalTest.my_server.e1_buffer = self.assert_messages_in_order(DoorFunctionalTest.my_server.e1_buffer, expected_msgs)
        assert not DoorFunctionalTest.my_server.e1_buffer, "e1_buffer is not empty at the end of the test"
        assert not DoorFunctionalTest.my_server.e2_buffer, "e2_buffer is not empty at the end of the test"

    def test_door_function4(self):
        #Passenger A inside Elevator 1 and Passenger B inside Elevator 2 press the internal button 3 with a 0.5s interval, both elevators start moving up simultaneously.
        # Passenger C at the second floor, presses the external up button at the second floor.
        # After Elevator 1, which started first, stops at the third floor, 
        # Passenger A continuously clicks the open door button 3 times.
        # Elevator 2 continues to the second floor, Passenger C enters the elevator.
        msgs = ["select_floor@3#1","select_floor@3#2","call_up@2" , "open_door#1","open_door#1","open_door#1"]
        intervals = [0.5, 1.1 ,5 , 1 ,1 ,10]
        testing_serial(DoorFunctionalTest.my_server, msgs, intervals)
        expected_msgs = ["floor_arrived@3#1", "door_opened#1" ,"door_closed#1"]
                        
        DoorFunctionalTest.my_server.e1_buffer = self.assert_messages_in_order(DoorFunctionalTest.my_server.e1_buffer, expected_msgs)
        expected_msgs = ["floor_arrived@3#2","door_opened#2" ,"door_closed#2",
                         "floor_arrived@2#2","up_floor_arrived@2#2","door_opened#2","door_closed#2"]
        DoorFunctionalTest.my_server.e2_buffer = self.assert_messages_in_order(DoorFunctionalTest.my_server.e2_buffer, expected_msgs)
        assert not DoorFunctionalTest.my_server.e1_buffer, "e1_buffer is not empty at the end of the test"
        assert not DoorFunctionalTest.my_server.e2_buffer, "e2_buffer is not empty at the end of the test"
    


if __name__ == '__main__':
    unittest.main()
