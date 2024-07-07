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
class TestMultipleUserTransfer(unittest.TestCase):
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
        self.identity = TestMultipleUserTransfer.identity
        self.zmqThread = TestMultipleUserTransfer.zmqThread
        self.mainWindow:Controller = TestMultipleUserTransfer.mainWindow
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

    def getDispayBalance(self,id:int)->float:
        # "Account ID: {self.current_account_id}\nBalance: ${balance:.2f}"
        return float(self.mainWindow.app_instances[str(id)].test_dict["l_account"].text().split("$")[1])

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
        QTest.keyClicks(self.mainWindow.atm.test_dict["i_id"], "2024111111")
        QTest.qWait(1000)
        QTest.keyClicks(self.mainWindow.atm.test_dict["i_password"], "111111")
        QTest.qWait(1000)
        QTimer.singleShot(1000, lambda: self.simulateClickMessage(self.mainWindow.atm))
        QTest.mouseClick(self.mainWindow.atm.test_dict["b_confirm"], Qt.LeftButton)
        # Wait for 2s for the message box to appear
        QTimer.singleShot(1000, lambda: self.simulateInputDialog(self.mainWindow.atm.test_dict["d_dialog"], "10"))
        # Wait for 3s for the message box to appear
        QTimer.singleShot(2000, lambda: self.simulateClickMessage(self.mainWindow.atm))
        QTest.mouseClick(self.mainWindow.atm.test_dict["b_deposit"], Qt.LeftButton)
        QTest.qWait(1000)
        QTimer.singleShot(1000, lambda: self.simulateClickMessage(self.mainWindow.atm))
        QTest.mouseClick(self.mainWindow.atm.test_dict["b_return"], Qt.LeftButton)

        # Create second account on ATM & deposit $1000
        QTest.mouseClick(self.mainWindow.atm.test_dict["b_create"], Qt.LeftButton)
        QTest.qWait(1000)
        QTest.keyClicks(self.mainWindow.atm.test_dict["i_id"], "2024222222")
        QTest.qWait(1000)
        QTest.keyClicks(self.mainWindow.atm.test_dict["i_password"], "222222")
        QTest.qWait(1000)
        QTimer.singleShot(2000, lambda: self.simulateClickMessage(self.mainWindow.atm))
        QTest.mouseClick(self.mainWindow.atm.test_dict["b_confirm"], Qt.LeftButton)
        # Wait for 2s for the message box to appear
        QTimer.singleShot(1000, lambda: self.simulateInputDialog(self.mainWindow.atm.test_dict["d_dialog"], "10"))
        # Wait for 3s for the message box to appear
        QTimer.singleShot(2000, lambda: self.simulateClickMessage(self.mainWindow.atm))
        QTest.mouseClick(self.mainWindow.atm.test_dict["b_deposit"], Qt.LeftButton)
        QTest.qWait(1000)
        QTimer.singleShot(1000, lambda: self.simulateClickMessage(self.mainWindow.atm))
        QTest.mouseClick(self.mainWindow.atm.test_dict["b_return"], Qt.LeftButton)

        # Create third account on ATM & deposit $1000
        QTest.mouseClick(self.mainWindow.atm.test_dict["b_create"], Qt.LeftButton)
        QTest.qWait(1000)
        QTest.keyClicks(self.mainWindow.atm.test_dict["i_id"], "2024333333")
        QTest.qWait(1000)
        QTest.keyClicks(self.mainWindow.atm.test_dict["i_password"], "333333")
        QTest.qWait(1000)
        QTimer.singleShot(1000, lambda: self.simulateClickMessage(self.mainWindow.atm))
        QTest.mouseClick(self.mainWindow.atm.test_dict["b_confirm"], Qt.LeftButton)
        # Wait for 2s for the message box to appear
        QTimer.singleShot(1000, lambda: self.simulateInputDialog(self.mainWindow.atm.test_dict["d_dialog"], "10"))
        # Wait for 3s for the message box to appear
        QTimer.singleShot(2000, lambda: self.simulateClickMessage(self.mainWindow.atm))
        QTest.mouseClick(self.mainWindow.atm.test_dict["b_deposit"], Qt.LeftButton)
        QTest.qWait(1000)
        QTimer.singleShot(1000, lambda: self.simulateClickMessage(self.mainWindow.atm))
        QTest.mouseClick(self.mainWindow.atm.test_dict["b_return"], Qt.LeftButton)
    def test_002_openAppInController(self):
        # Open the app, id=1
        QTest.mouseClick(self.mainWindow.test_dict["b_open"], Qt.LeftButton)
        self.mainWindow.app_instances["1"].move(10, 100)
        QTest.qWait(500)
        QTest.mouseClick(self.mainWindow.test_dict["b_open"], Qt.LeftButton)
        self.mainWindow.app_instances["2"].move(600, 100)
        QTest.qWait(500)
        QTest.mouseClick(self.mainWindow.test_dict["b_open"], Qt.LeftButton)
        self.mainWindow.app_instances["3"].move(1200, 100)
        QTest.qWait(500)
    def test_003_loginOnAppAndCheckBalance(self):
        QTest.mouseClick(self.mainWindow.app_instances["1"].test_dict["b_login"], Qt.LeftButton)
        QTest.qWait(1000)
        QTest.keyClicks(self.mainWindow.app_instances["1"].test_dict["i_id"], "2024111111")
        QTest.keyClicks(self.mainWindow.app_instances["1"].test_dict["i_password"], "111111")
        QTest.qWait(1000)
        QTimer.singleShot(1000, lambda: self.simulateClickMessage(self.mainWindow.app_instances["1"]))
        QTest.mouseClick(self.mainWindow.app_instances["1"].test_dict["b_confirm"], Qt.LeftButton)
        self.assertEqual(self.msgBoxText,"Log in successfully")
        self.assertEqual(self.getDispayBalance(1),1000.00)

        QTest.mouseClick(self.mainWindow.app_instances["2"].test_dict["b_login"], Qt.LeftButton)
        QTest.qWait(1000)
        QTest.keyClicks(self.mainWindow.app_instances["2"].test_dict["i_id"], "2024222222")
        QTest.keyClicks(self.mainWindow.app_instances["2"].test_dict["i_password"], "222222")
        QTest.qWait(1000)
        QTimer.singleShot(1000, lambda: self.simulateClickMessage(self.mainWindow.app_instances["2"]))
        QTest.mouseClick(self.mainWindow.app_instances["2"].test_dict["b_confirm"], Qt.LeftButton)
        self.assertEqual(self.msgBoxText,"Log in successfully")
        self.assertEqual(self.getDispayBalance(2),1000.00)

        QTest.mouseClick(self.mainWindow.app_instances["3"].test_dict["b_login"], Qt.LeftButton)
        QTest.qWait(1000)
        QTest.keyClicks(self.mainWindow.app_instances["3"].test_dict["i_id"], "2024333333")
        QTest.keyClicks(self.mainWindow.app_instances["3"].test_dict["i_password"], "333333")
        QTest.qWait(1000)
        QTimer.singleShot(1000, lambda: self.simulateClickMessage(self.mainWindow.app_instances["3"]))
        QTest.mouseClick(self.mainWindow.app_instances["3"].test_dict["b_confirm"], Qt.LeftButton)
        self.assertEqual(self.msgBoxText,"Log in successfully")
        self.assertEqual(self.getDispayBalance(3),1000.00)
    def test_004_tranfer_1_to_2_int(self):
        amount = 100
        # Wait for 1s for the dialog box to appear (input accountID)
        QTimer.singleShot(1000, lambda: self.simulateInputDialog(self.mainWindow.app_instances["1"].test_dict["d_dialog"], "2024222222"))
        # Wait for 2s for the message box to appear (input money)
        QTimer.singleShot(2000, lambda: self.simulateInputDialog(self.mainWindow.app_instances["1"].test_dict["d_dialog"], str(amount)))
        # Wait for 3s for the message box to appear
        QTimer.singleShot(3000, lambda: self.simulateClickMessage(self.mainWindow.app_instances["1"]))

        QTest.mouseClick(self.mainWindow.app_instances["1"].test_dict["b_transfer"], Qt.LeftButton)
        self.assertTrue(self.msgBoxText.startswith(f"${amount:.2f} transferred successfully"))
        self.assertEqual(self.getDispayBalance(1),900.00)
        self.assertEqual(self.getDispayBalance(2),1100.00)
    def test_005_tranfer_2_to_3_int(self):
        amount = 200
        # Wait for 1s for the dialog box to appear (input accountID)
        QTimer.singleShot(1000, lambda: self.simulateInputDialog(self.mainWindow.app_instances["2"].test_dict["d_dialog"], "2024333333"))
        # Wait for 2s for the message box to appear (input money)
        QTimer.singleShot(2000, lambda: self.simulateInputDialog(self.mainWindow.app_instances["2"].test_dict["d_dialog"], str(amount)))
        # Wait for 3s for the message box to appear
        QTimer.singleShot(3000, lambda: self.simulateClickMessage(self.mainWindow.app_instances["2"]))

        QTest.mouseClick(self.mainWindow.app_instances["2"].test_dict["b_transfer"], Qt.LeftButton)
        self.assertTrue(self.msgBoxText.startswith(f"${amount:.2f} transferred successfully"))
        self.assertEqual(self.getDispayBalance(2),900.00)
        self.assertEqual(self.getDispayBalance(3),1200.00)
    def test_006_tranfer_3_to_1_int(self):
        amount = 300
        # Wait for 1s for the dialog box to appear (input accountID)
        QTimer.singleShot(1000, lambda: self.simulateInputDialog(self.mainWindow.app_instances["3"].test_dict["d_dialog"], "2024111111"))
        # Wait for 2s for the message box to appear (input money)
        QTimer.singleShot(2000, lambda: self.simulateInputDialog(self.mainWindow.app_instances["3"].test_dict["d_dialog"], str(amount)))
        # Wait for 3s for the message box to appear
        QTimer.singleShot(3000, lambda: self.simulateClickMessage(self.mainWindow.app_instances["3"]))

        QTest.mouseClick(self.mainWindow.app_instances["3"].test_dict["b_transfer"], Qt.LeftButton)
        self.assertTrue(self.msgBoxText.startswith(f"${amount:.2f} transferred successfully"))
        self.assertEqual(self.getDispayBalance(3),900.00)
        self.assertEqual(self.getDispayBalance(1),1200.00)
    def test_007_tranfer_1_to_2_float(self):
        amount = 100.5
        # Wait for 1s for the dialog box to appear (input accountID)
        QTimer.singleShot(1000, lambda: self.simulateInputDialog(self.mainWindow.app_instances["1"].test_dict["d_dialog"], "2024222222"))
        # Wait for 2s for the message box to appear (input money)
        QTimer.singleShot(2000, lambda: self.simulateInputDialog(self.mainWindow.app_instances["1"].test_dict["d_dialog"], str(amount)))
        # Wait for 3s for the message box to appear
        QTimer.singleShot(3000, lambda: self.simulateClickMessage(self.mainWindow.app_instances["1"]))

        QTest.mouseClick(self.mainWindow.app_instances["1"].test_dict["b_transfer"], Qt.LeftButton)
        self.assertTrue(self.msgBoxText.startswith(f"${amount:.2f} transferred successfully"))
        self.assertEqual(self.getDispayBalance(1),1099.5)
        self.assertEqual(self.getDispayBalance(2),1000.50)
    def test_008_tranfer_2_to_3_float(self):
        amount = 200.99
        # Wait for 1s for the dialog box to appear (input accountID)
        QTimer.singleShot(1000, lambda: self.simulateInputDialog(self.mainWindow.app_instances["2"].test_dict["d_dialog"], "2024333333"))
        # Wait for 2s for the message box to appear (input money)
        QTimer.singleShot(2000, lambda: self.simulateInputDialog(self.mainWindow.app_instances["2"].test_dict["d_dialog"], str(amount)))
        # Wait for 3s for the message box to appear
        QTimer.singleShot(3000, lambda: self.simulateClickMessage(self.mainWindow.app_instances["2"]))

        QTest.mouseClick(self.mainWindow.app_instances["2"].test_dict["b_transfer"], Qt.LeftButton)
        self.assertTrue(self.msgBoxText.startswith(f"${amount:.2f} transferred successfully"))
        self.assertEqual(self.getDispayBalance(2),799.51)
        self.assertEqual(self.getDispayBalance(3),1100.99)
    def test_009_tranfer_3_to_1_float(self):
        amount = 1100.99
        # Wait for 1s for the dialog box to appear (input accountID)
        QTimer.singleShot(1000, lambda: self.simulateInputDialog(self.mainWindow.app_instances["3"].test_dict["d_dialog"], "2024111111"))
        # Wait for 2s for the message box to appear (input money)
        QTimer.singleShot(2000, lambda: self.simulateInputDialog(self.mainWindow.app_instances["3"].test_dict["d_dialog"], str(amount)))
        # Wait for 3s for the message box to appear
        QTimer.singleShot(3000, lambda: self.simulateClickMessage(self.mainWindow.app_instances["3"]))

        QTest.mouseClick(self.mainWindow.app_instances["3"].test_dict["b_transfer"], Qt.LeftButton)
        self.assertTrue(self.msgBoxText.startswith(f"${amount:.2f} transferred successfully"))
        self.assertEqual(self.getDispayBalance(3),0)
        self.assertEqual(self.getDispayBalance(1),2200.49)
    def test_010_queryall(self):
        QTimer.singleShot(2000, lambda: self.simulateClickMessage(self.mainWindow.app_instances["1"]))
        QTest.mouseClick(self.mainWindow.app_instances["1"].test_dict["b_query"], Qt.LeftButton)
        QTimer.singleShot(2000, lambda: self.simulateClickMessage(self.mainWindow.app_instances["2"]))
        QTest.mouseClick(self.mainWindow.app_instances["2"].test_dict["b_query"], Qt.LeftButton)
        QTimer.singleShot(2000, lambda: self.simulateClickMessage(self.mainWindow.app_instances["3"]))
        QTest.mouseClick(self.mainWindow.app_instances["3"].test_dict["b_query"], Qt.LeftButton)
        

if __name__ == "__main__":
    unittest.main()
