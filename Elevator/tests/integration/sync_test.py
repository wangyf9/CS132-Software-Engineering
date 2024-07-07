import sys
import unittest
from PyQt5.QtWidgets import QApplication
from PyQt5.QtTest import QTest
from PyQt5.QtCore import Qt
from src import Server
import os
import time
import random

def testing_serial(server: Server.ZmqServerThread, msgs: list[str], interval: int):
    for msg in msgs:
        server.send_string(server.bindedClient, msg)
        time.sleep(interval)

class FunctionalTest(unittest.TestCase):
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
        FunctionalTest.my_server.send_string(FunctionalTest.my_server.bindedClient, "reset")  # Reset the client
        time.sleep(1)

    def tearDown(self):
        """Cleanup after each test case"""
        FunctionalTest.my_server.send_string(FunctionalTest.my_server.bindedClient, "reset")  # Reset the client
        time.sleep(1)

    @classmethod
    def tearDownClass(cls):
        """Cleanup work after all test cases are executed"""
        cls.my_server.send_string(cls.my_server.bindedClient, "reset")
        time.sleep(1)
        print("[Test] Test Environment Cleaned")

    def test_freeride(self):
        # Passenger A calls the elevator at 1st floor, select 3rd floor
        # After that, passenger B calls the elevator at 2nd floor, want to go up
        # The same elevator should go to 2nd floor and pick him up.
        msgs = [
            "call_up@1",
            "select_floor@3#1",
            "call_up@2"
        ]
        testing_serial(FunctionalTest.my_server, msgs, 1)
        # Hold and wait for the elevator to arrive
        time.sleep(20)
        # Check if the elevator has arrived at 2nd floor & 3rd floor
        print(FunctionalTest.my_server.e1_buffer)
        self.assertTrue("up_floor_arrived@2#1" in FunctionalTest.my_server.e1_buffer)
        self.assertTrue("floor_arrived@3#1" in FunctionalTest.my_server.e1_buffer)

    def test_parallel_moving(self):
        # Passenger A calls the elevator at 1st floor, select 3rd floor
        # After that, passenger B calls the elevator at 2nd floor, want to go down
        # The other elevator should go to 2nd floor
        msgs = [
            "call_up@1",
            "call_down@2",
            "select_floor@3#1",
            "select_floor@1#2"
        ]
        testing_serial(FunctionalTest.my_server, msgs, 2)
        # Hold and wait for the elevator to arrive
        time.sleep(20)
        # Check if the elevator has arrived at 2nd floor & 3rd floor
        print(FunctionalTest.my_server.e1_buffer)
        self.assertTrue("floor_arrived@2#2" in FunctionalTest.my_server.e2_buffer)
        self.assertTrue("floor_arrived@3#1" in FunctionalTest.my_server.e1_buffer)

if __name__ == '__main__':
    unittest.main()
