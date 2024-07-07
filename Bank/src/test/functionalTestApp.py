from PyQt5.QtWidgets import QWidget, QMainWindow, QLabel, QPushButton, QMessageBox, QInputDialog, QApplication, QVBoxLayout, QHBoxLayout, QFrame, QGridLayout,QLineEdit
from PyQt5.QtCore import pyqtSignal, Qt ,QTimer
from PyQt5.QtGui import QFont
import sys
import os
# 将项目根目录添加到 PYTHONPATH
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../'))
sys.path.append(project_root)
from src.frontend import APP_UI
from src.frontend import NetClient
from src.frontend import ATM_UI
import sqlite3
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from backend.bank import reset_database
from src.frontend.Controller import Controller
import unittest
from PyQt5.QtTest import QTest
import time
class TestSingleUserAppAndATM(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """Initialize the test environment and set class-level variables"""
        reset_database()
        time.sleep(5)  # Wait for the database to reset
        cls.identity = "Team15"
        cls.zmqThread = NetClient.ZmqClientThread(identity=cls.identity)
        cls.app = QApplication(sys.argv)
        cls.mainWindow:Controller = Controller(cls.zmqThread)
        cls.mainWindow.show()
        pass
    def setUp(self):
        """Initialization of each test case"""
        self.identity = TestSingleUserAppAndATM.identity
        self.zmqThread = TestSingleUserAppAndATM.zmqThread
        self.mainWindow:Controller = TestSingleUserAppAndATM.mainWindow
        self.msgBoxText = ""
        pass
    def tearDown(self):
        """Cleanup after each test case"""
        pass
        

    @classmethod
    def tearDownClass(cls):
        """Cleanup work after all test cases are executed"""
        # Ensure the event loop runs long enough to display the window
        QTest.qWait(1000)  # Delay 1 second to ensure the window is displayed
        print("[Test finished]")
        cls.mainWindow.atm.close()
        cls.mainWindow.close()

    def simulateClickMessage(self,ui_window:QWidget):
        # Find the active message box and click the "OK" button
        active_message_box = ui_window.findChild(QMessageBox)
        if active_message_box:
            ok_button = active_message_box.button(QMessageBox.Ok)
            self.msgBoxText = active_message_box.text()
            if ok_button:
                QTest.mouseClick(ok_button, Qt.LeftButton)

    def simulateInputDialog(self,dialog:QInputDialog, text:str):
        input_field = dialog.findChild(QLineEdit)
        QTest.keyClicks(input_field, text)
        QTest.keyClick(input_field, Qt.Key_Enter)  # Simulate pressing Enter

    def simulateCancelDialog(self,dialog: QInputDialog):
        # Find the Cancel button in the dialog
        input_field = dialog.findChild(QLineEdit)
        QTest.keyClick(input_field, Qt.Key_Escape)  # Simulate pressing Enter

    # def getDispayBalance(self)->float:
    #     "Account ID: {self.current_account_id}\nBalance: ${balance:.2f}"
    #     return float(self.mainWindow.atm.test_dict["l_account"].text().split("$")[1])

    def simulateYesMessage(self,ui_window:QWidget):
        # Find the active message box and click the "Yes" button
        active_message_box = ui_window.findChild(QMessageBox)
        if active_message_box:
            yes_button = active_message_box.button(QMessageBox.Yes)
            if yes_button:
                QTest.mouseClick(yes_button, Qt.LeftButton)
    
    def test_001_preparework(self):
        # Create 1 account on ATM & deposit $1000
        QTest.mouseClick(self.mainWindow.atm.test_dict["b_create"], Qt.LeftButton)
        QTest.qWait(1000)
        QTest.keyClicks(self.mainWindow.atm.test_dict["i_id"], "2024123456")
        QTest.qWait(1000)
        QTest.keyClicks(self.mainWindow.atm.test_dict["i_password"], "123456")
        QTest.qWait(1000)
        QTimer.singleShot(2000, lambda: self.simulateClickMessage(self.mainWindow.atm))
        QTest.mouseClick(self.mainWindow.atm.test_dict["b_confirm"], Qt.LeftButton)
        # Wait for 2s for the message box to appear
        QTimer.singleShot(2000, lambda: self.simulateInputDialog(self.mainWindow.atm.test_dict["d_dialog"], "10"))
        # Wait for 3s for the message box to appear
        QTimer.singleShot(3000, lambda: self.simulateClickMessage(self.mainWindow.atm))
        QTest.mouseClick(self.mainWindow.atm.test_dict["b_deposit"], Qt.LeftButton)
        QTest.qWait(1000)
    def test_002_openAppInController(self):
        # Open the app, id=1
        QTest.mouseClick(self.mainWindow.test_dict["b_open"], Qt.LeftButton)
        QTest.qWait(500)
        self.assertEqual(self.mainWindow.num_apps_opened,1)
    @unittest.skip("no such case since appid is automatically assigned")
    def test_003_openAppTwiceSameAppId(self):
        QTimer.singleShot(2000, lambda: self.simulateInputDialog(self.mainWindow.test_dict["d_dialog"], "1"))
        QTimer.singleShot(3000, lambda: self.simulateClickMessage(self.mainWindow))
        QTest.mouseClick(self.mainWindow.test_dict["b_open"], Qt.LeftButton)
        QTest.qWait(500)
        self.assertEqual(self.msgBoxText,"App with specified ID is already open.")
        self.assertEqual(self.mainWindow.num_apps_opened,1)
    def test_004_openAppAndCloseApp(self):
        QTest.mouseClick(self.mainWindow.test_dict["b_open"], Qt.LeftButton)
        QTest.qWait(500)
        self.assertEqual(self.mainWindow.num_apps_opened,2)
        QTimer.singleShot(4000, lambda: self.simulateInputDialog(self.mainWindow.test_dict["d_dialog"], "2"))
        QTest.mouseClick(self.mainWindow.test_dict["b_close"], Qt.LeftButton)
    def test_005_loginOnApp1(self):
        QTest.mouseClick(self.mainWindow.app_instances["1"].test_dict["b_login"], Qt.LeftButton)
        QTest.qWait(1000)
        QTest.keyClicks(self.mainWindow.app_instances["1"].test_dict["i_id"], "2024123456")
        QTest.keyClicks(self.mainWindow.app_instances["1"].test_dict["i_password"], "123456")
        QTest.qWait(1000)
        QTimer.singleShot(1000, lambda: self.simulateClickMessage(self.mainWindow.app_instances["1"]))
        QTest.mouseClick(self.mainWindow.app_instances["1"].test_dict["b_confirm"], Qt.LeftButton)
        self.assertEqual(self.msgBoxText,"Log in successfully")
    def test_006_loginSameAccountOnSecondApp(self):
        # Open app id = 3
        QTest.mouseClick(self.mainWindow.test_dict["b_open"], Qt.LeftButton)
        QTest.qWait(500)
        # log in on app 2
        QTest.mouseClick(self.mainWindow.app_instances["3"].test_dict["b_login"], Qt.LeftButton)
        QTest.qWait(1000)
        QTest.keyClicks(self.mainWindow.app_instances["3"].test_dict["i_id"], "2024123456")
        QTest.keyClicks(self.mainWindow.app_instances["3"].test_dict["i_password"], "123456")
        QTest.qWait(1000)
        QTimer.singleShot(1000, lambda: self.simulateClickMessage(self.mainWindow.app_instances["1"]))
        QTimer.singleShot(2000, lambda: self.simulateClickMessage(self.mainWindow.app_instances["3"]))
        QTest.mouseClick(self.mainWindow.app_instances["3"].test_dict["b_confirm"], Qt.LeftButton)
        self.assertEqual(self.msgBoxText,"Log in successfully")
    def test_007_changePassword(self):
        # Wait for 2s for the dialog box to appear
        QTimer.singleShot(2000, lambda: self.simulateInputDialog(self.mainWindow.app_instances["3"].test_dict["d_dialog"], "000666"))
        # Wait for 3s for the message box on app to appear
        QTimer.singleShot(3000, lambda: self.simulateClickMessage(self.mainWindow.app_instances["3"]))
        # Wait for 4s to verify the message Box
        QTimer.singleShot(3500, lambda: self.assertEqual(self.msgBoxText, "Password changed successfully"))
        # Wait for 5s for another message box on atm
        QTimer.singleShot(5000, lambda: self.simulateClickMessage(self.mainWindow.atm))
        # Wait for 6s to verify the other message Box
        QTimer.singleShot(6000, lambda: self.assertEqual(self.msgBoxText, "Card returned successfully"))
        # Wait for 7s for another message box on 
        QTimer.singleShot(7000, lambda: self.simulateClickMessage(self.mainWindow.app_instances["3"]))
         # Wait for 8s to verify the other message Box
        QTimer.singleShot(8000, lambda: self.assertEqual(self.msgBoxText, "Logged out successfully"))
        # Click change password button
        QTest.mouseClick(self.mainWindow.app_instances["3"].test_dict["b_change_password"], Qt.LeftButton)
    def test_008_logInUsingNewPassword(self):
        QTest.mouseClick(self.mainWindow.app_instances["3"].test_dict["b_login"], Qt.LeftButton)
        QTest.qWait(1000)
        QTest.keyClicks(self.mainWindow.app_instances["3"].test_dict["i_id"], "2024123456")
        QTest.keyClicks(self.mainWindow.app_instances["3"].test_dict["i_password"], "000666")
        QTest.qWait(1000)
        QTimer.singleShot(1000, lambda: self.simulateClickMessage(self.mainWindow.app_instances["3"]))
        QTest.mouseClick(self.mainWindow.app_instances["3"].test_dict["b_confirm"], Qt.LeftButton)
        self.assertEqual(self.msgBoxText,"Log in successfully")
    def test_009_query(self):
        QTimer.singleShot(2000, lambda: self.simulateClickMessage(self.mainWindow.app_instances["3"]))
        QTest.mouseClick(self.mainWindow.app_instances["3"].test_dict["b_query"], Qt.LeftButton)
        

if __name__ == "__main__":
    unittest.main()
