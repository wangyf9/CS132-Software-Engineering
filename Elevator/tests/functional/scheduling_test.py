import sys
import unittest
from src import Server
import time

def testing_serial(server: Server.ZmqServerThread, msgs: list[str], intervals: list[int]):
    for msg, interval in zip(msgs, intervals):
        server.send_string(server.bindedClient, msg)
        time.sleep(interval)

class SchedulingFunctionalTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """Initialize the test environment and set class-level variables"""
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
        SchedulingFunctionalTest.my_server.send_string(SchedulingFunctionalTest.my_server.bindedClient, "reset")  # Reset the client
        time.sleep(1)

    def tearDown(self):
        """Cleanup after each test case"""
        
        SchedulingFunctionalTest.my_server.send_string(SchedulingFunctionalTest.my_server.bindedClient, "reset")  # Reset the client
        SchedulingFunctionalTest.my_server.e1_buffer = []  # Clear e1_buffer
        SchedulingFunctionalTest.my_server.e2_buffer = []  # Clear e2_buffer
        print("_"*50)
        time.sleep(1)
        
    @classmethod
    def tearDownClass(cls):
        """Cleanup work after all test cases are executed"""
        SchedulingFunctionalTest.my_server.send_string(SchedulingFunctionalTest.my_server.bindedClient, "reset")
        SchedulingFunctionalTest.my_server.e1_buffer = []  # Clear e1_buffer
        SchedulingFunctionalTest.my_server.e2_buffer = []  # Clear e2_buffer
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

    def test_scheduling1(self):
        # Passenger A calls the elevator at 1st floor, select 3rd floor
        # After 1 seconds, passenger B calls the elevator at 2nd floor, want to go up
        # The same elevator should go to 2nd floor and pick him up.
        msgs = ["call_up@1", "select_floor@3#1"]
        intervals = [5, 1]
        testing_serial(SchedulingFunctionalTest.my_server, msgs, intervals)
        expected_msgs = ["floor_arrived@1#1", "up_floor_arrived@1#1", "door_opened#1","door_closed#1"]
        SchedulingFunctionalTest.my_server.e1_buffer = self.assert_messages_in_order(SchedulingFunctionalTest.my_server.e1_buffer, expected_msgs)
        msgs =["call_up@2"]
        intervals = [14]
        testing_serial(SchedulingFunctionalTest.my_server, msgs, intervals)
        expected_msgs = ['floor_arrived@2#1', 'up_floor_arrived@2#1', 'door_opened#1', 
                         'door_closed#1', 'floor_arrived@3#1', 'door_opened#1','door_closed#1']
        SchedulingFunctionalTest.my_server.e1_buffer = self.assert_messages_in_order(SchedulingFunctionalTest.my_server.e1_buffer, expected_msgs)
        assert not SchedulingFunctionalTest.my_server.e1_buffer, "e1_buffer is not empty at the end of the test"
        assert not SchedulingFunctionalTest.my_server.e2_buffer, "e2_buffer is not empty at the end of the test"

    def test_scheduling2(self):
        # Passenger A calls the elevator at 1st floor, select 3rd floor
        # After 1.5 seconds, passenger B calls the elevator at 2nd floor, want to go up
        # The elevator 2 should go to 2nd floor and pick him up.
        msgs = ["call_up@1", "select_floor@3#1"]
        intervals = [5, 1.5]
        testing_serial(SchedulingFunctionalTest.my_server, msgs, intervals)
        expected_msgs = ["floor_arrived@1#1", "up_floor_arrived@1#1", "door_opened#1","door_closed#1"]
        SchedulingFunctionalTest.my_server.e1_buffer = self.assert_messages_in_order(SchedulingFunctionalTest.my_server.e1_buffer, expected_msgs)
        msgs =["call_up@2", "select_floor@3#2"]
        intervals = [7, 8]
        testing_serial(SchedulingFunctionalTest.my_server, msgs, intervals)
        expected_msgs = ['floor_arrived@3#1', 'door_opened#1','door_closed#1']
        SchedulingFunctionalTest.my_server.e1_buffer = self.assert_messages_in_order(SchedulingFunctionalTest.my_server.e1_buffer, expected_msgs)
        expected_msgs = ['floor_arrived@2#2', 'up_floor_arrived@2#2', 'door_opened#2', 
                         'door_closed#2', 'floor_arrived@3#2', 'door_opened#2','door_closed#2']
        SchedulingFunctionalTest.my_server.e2_buffer = self.assert_messages_in_order(SchedulingFunctionalTest.my_server.e2_buffer, expected_msgs)
        assert not SchedulingFunctionalTest.my_server.e1_buffer, "e1_buffer is not empty at the end of the test"
        assert not SchedulingFunctionalTest.my_server.e2_buffer, "e2_buffer is not empty at the end of the test"
    def test_scheduling3(self):
        
        # Passenger A and B at 2nd floor press the external buttons up and down simultaneously
        # After the elevator doors close, passenger A and B at 2nd floor press the external buttons up and down simultaneously again
        # Passenger A enters elevator 1 and presses the internal button 3
        # Passenger B enters elevator 2 and presses the internal button 1
        msgs = ["call_up@2", "call_down@2"]
        intervals = [0, 8]
        testing_serial(SchedulingFunctionalTest.my_server, msgs, intervals)
        expected_msgs = ["floor_arrived@2#1", "up_floor_arrived@2#1", "door_opened#1","door_closed#1"]                
        SchedulingFunctionalTest.my_server.e1_buffer = self.assert_messages_in_order(SchedulingFunctionalTest.my_server.e1_buffer, expected_msgs)
        expected_msgs =["floor_arrived@2#2", "down_floor_arrived@2#2", "door_opened#2","door_closed#2"]
        SchedulingFunctionalTest.my_server.e2_buffer = self.assert_messages_in_order(SchedulingFunctionalTest.my_server.e2_buffer, expected_msgs)
        
        msgs = ["call_down@2", "call_up@2", "select_floor@3#1", "select_floor@-1#2"]
        intervals = [0, 5, 0, 12]
        testing_serial(SchedulingFunctionalTest.my_server, msgs, intervals)
        expected_msgs = ["up_floor_arrived@2#1", "door_opened#1","door_closed#1"
                         ,"floor_arrived@3#1", "door_opened#1","door_closed#1"]
        SchedulingFunctionalTest.my_server.e1_buffer = self.assert_messages_in_order(SchedulingFunctionalTest.my_server.e1_buffer, expected_msgs)
        expected_msgs = ["down_floor_arrived@2#2", "door_opened#2","door_closed#2"
                            ,"floor_arrived@-1#2", "door_opened#2","door_closed#2"]
        SchedulingFunctionalTest.my_server.e2_buffer = self.assert_messages_in_order(SchedulingFunctionalTest.my_server.e2_buffer, expected_msgs)
        assert not SchedulingFunctionalTest.my_server.e1_buffer, "e1_buffer is not empty at the end of the test"
        assert not SchedulingFunctionalTest.my_server.e2_buffer, "e2_buffer is not empty at the end of the test"

    def test_scheduling4(self):
        # Passenger A in elevator 1 and passenger B in elevator 2 press the internal button 3 with an interval of 0.5s, both elevators start moving up
        # Passenger C at the 2nd floor presses the external button up
        # Elevator 1, which arrived floor3 first, go to the 2nd floor, passenger C enters the elevator
        # Elevator 2 continues to stop at floor 3
        msgs = ["select_floor@3#1","select_floor@3#2","call_up@2"]
        intervals = [0.5, 1.1 , 15]
        testing_serial(SchedulingFunctionalTest.my_server, msgs, intervals)
        expected_msgs = ["floor_arrived@3#1", "door_opened#1" ,"door_closed#1",
                         "floor_arrived@2#1","up_floor_arrived@2#1","door_opened#1","door_closed#1"]
        SchedulingFunctionalTest.my_server.e1_buffer = self.assert_messages_in_order(SchedulingFunctionalTest.my_server.e1_buffer, expected_msgs)
        expected_msgs = ["floor_arrived@3#2","door_opened#2" ,"door_closed#2"]
        SchedulingFunctionalTest.my_server.e2_buffer = self.assert_messages_in_order(SchedulingFunctionalTest.my_server.e2_buffer, expected_msgs)
        assert not SchedulingFunctionalTest.my_server.e1_buffer, "e1_buffer is not empty at the end of the test"
        assert not SchedulingFunctionalTest.my_server.e2_buffer, "e2_buffer is not empty at the end of the test"

    def test_scheduling5(self):
        # Passenger B in elevator 2 presses the internal button -1, elevator 2 moves down to -1 floor
        # Passenger A in elevator 1 presses the internal button 3, elevator 1 moves to the 3rd floor
        # Passenger A presses the internal button -1 in the elevator, passenger B presses the internal button 3 in the elevator, 
        # The elevators start to run
        # Passenger D at the 1st floor presses the external button down, passenger C at the 2nd floor presses the external button up
        # Elevator 1 stops at the 1st floor, passenger D enters
        # Elevator 2 stops at the 2nd floor, passenger C enters
        # Elevator 1 arrives at -1 floor, elevator 2 arrives at the 3rd floor, passengers A, B, C, and D reach their target floors
        msgs = ["select_floor@-1#2","select_floor@3#1"]
        intervals = [0.5, 10]
        testing_serial(SchedulingFunctionalTest.my_server, msgs, intervals)
        expected_msgs = ["floor_arrived@3#1", "door_opened#1" ,"door_closed#1"]
        SchedulingFunctionalTest.my_server.e1_buffer = self.assert_messages_in_order(SchedulingFunctionalTest.my_server.e1_buffer, expected_msgs)
        expected_msgs = ["floor_arrived@-1#2","door_opened#2" ,"door_closed#2"]
        SchedulingFunctionalTest.my_server.e2_buffer = self.assert_messages_in_order(SchedulingFunctionalTest.my_server.e2_buffer, expected_msgs)
        msgs = ["select_floor@-1#1","select_floor@3#2","call_down@1","call_up@2"]
        intervals = [0,0,0,20]
        testing_serial(SchedulingFunctionalTest.my_server, msgs, intervals)
        expected_msgs = ["floor_arrived@1#1","down_floor_arrived@1#1","door_opened#1","door_closed#1",
                         "floor_arrived@-1#1","door_opened#1","door_closed#1"]
        SchedulingFunctionalTest.my_server.e1_buffer = self.assert_messages_in_order(SchedulingFunctionalTest.my_server.e1_buffer, expected_msgs)
        
        expected_msgs = ["floor_arrived@2#2","up_floor_arrived@2#2","door_opened#2","door_closed#2",
                         "floor_arrived@3#2","door_opened#2","door_closed#2"]
        SchedulingFunctionalTest.my_server.e2_buffer = self.assert_messages_in_order(SchedulingFunctionalTest.my_server.e2_buffer, expected_msgs)
        assert not SchedulingFunctionalTest.my_server.e1_buffer, "e1_buffer is not empty at the end of the test"
        assert not SchedulingFunctionalTest.my_server.e2_buffer, "e2_buffer is not empty at the end of the test"

    def test_scheduling6(self):
        # Passenger A in elevator 1 presses the internal button 3, the elevator starts moving up
        # After elevator 1 passes the 2nd floor, passenger A presses the internal button 2, no response
        # Elevator 1 continues to run and arrives at the 3rd floor
        msgs = ["select_floor@3#1","select_floor@2#1"]
        intervals = [2.1, 10]
        testing_serial(SchedulingFunctionalTest.my_server, msgs, intervals)
        expected_msgs = ["floor_arrived@3#1", "door_opened#1" ,"door_closed#1"]
        SchedulingFunctionalTest.my_server.e1_buffer = self.assert_messages_in_order(SchedulingFunctionalTest.my_server.e1_buffer, expected_msgs)

        assert not SchedulingFunctionalTest.my_server.e1_buffer, "e1_buffer is not empty at the end of the test"
        assert not SchedulingFunctionalTest.my_server.e2_buffer, "e2_buffer is not empty at the end of the test"

    def test_scheduling7(self):
        # Passenger A in elevator 1 presses the internal button 3, the elevator starts moving up
        # 1.5s after elevator 1 starts running, passenger A presses the internal button 2, there is no response because elevator 1 is near the 2nd floor and cannot stop
        # Elevator 1 continues to run and arrives at the 3rd floor
        msgs = ["select_floor@3#1","select_floor@2#1"]
        intervals = [1.8, 10]
        testing_serial(SchedulingFunctionalTest.my_server, msgs, intervals)
        expected_msgs = ["floor_arrived@3#1", "door_opened#1" ,"door_closed#1"]
        SchedulingFunctionalTest.my_server.e1_buffer = self.assert_messages_in_order(SchedulingFunctionalTest.my_server.e1_buffer, expected_msgs)

        assert not SchedulingFunctionalTest.my_server.e1_buffer, "e1_buffer is not empty at the end of the test"
        assert not SchedulingFunctionalTest.my_server.e2_buffer, "e2_buffer is not empty at the end of the test"

    def test_scheduling8(self):
        # Passenger A in elevator 1 presses the internal button 3, the elevator starts moving up
        # 1s after elevator 1 starts running, passenger A presses the internal button 2, the light on the 2nd floor lights up
        # Elevator 1 stops at the 2nd floor, then elevator 1 continues to run and arrives at the 3rd floor
        msgs = ["select_floor@3#1","select_floor@2#1"]
        intervals = [0.5,20]
        testing_serial(SchedulingFunctionalTest.my_server, msgs, intervals)
        expected_msgs =  ["floor_arrived@2#1","door_opened#1","door_closed#1",
                        "floor_arrived@3#1", "door_opened#1" ,"door_closed#1"]
        SchedulingFunctionalTest.my_server.e1_buffer = self.assert_messages_in_order(SchedulingFunctionalTest.my_server.e1_buffer, expected_msgs)

        assert not SchedulingFunctionalTest.my_server.e1_buffer, "e1_buffer is not empty at the end of the test"
        assert not SchedulingFunctionalTest.my_server.e2_buffer, "e2_buffer is not empty at the end of the test"

   

if __name__ == '__main__':
    unittest.main()
