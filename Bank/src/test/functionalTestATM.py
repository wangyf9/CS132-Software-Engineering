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

class TestSingleUserATM(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """Initialize the test environment and set class-level variables"""
        reset_database()
        time.sleep(5)  # Wait for the database to reset
        cls.identity = "Team15"
        cls.zmqThread = NetClient.ZmqClientThread(identity=cls.identity)
        cls.app = QApplication(sys.argv)
        cls.mainWindow = Controller(cls.zmqThread)
        cls.mainWindow.show()
        pass
    def setUp(self):
        """Initialization of each test case"""
        self.identity = TestSingleUserATM.identity
        self.zmqThread = TestSingleUserATM.zmqThread
        self.mainWindow = TestSingleUserATM.mainWindow
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
        pass


    def test_001_create_account_common(self):
        # Click create account button
        print("[Test-001]")
        QTest.mouseClick(self.mainWindow.atm.test_dict["b_create"], Qt.LeftButton)
        QTest.qWait(1000)
        QTest.keyClicks(self.mainWindow.atm.test_dict["i_id"], "2024123456")
        QTest.qWait(1000)
        QTest.keyClicks(self.mainWindow.atm.test_dict["i_password"], "123456")
        QTest.qWait(1000)
        # Wait for 2s for the message box to appear
        QTimer.singleShot(2000, lambda: self.simulateClickMessage(self.mainWindow.atm))
        QTest.mouseClick(self.mainWindow.atm.test_dict["b_confirm"], Qt.LeftButton)
        self.assertEqual(self.msgBoxText, "Account created successfully")
    def test_002_deposit_common(self):
        print("[Test-002]")
        # get start balance:
        start_balance = self.getDispayBalance()
        # Click deposit button
        # Wait for 2s for the message box to appear
        QTimer.singleShot(2000, lambda: self.simulateInputDialog(self.mainWindow.atm.test_dict["d_dialog"], "10"))
        # Wait for 3s for the message box to appear
        QTimer.singleShot(3000, lambda: self.simulateClickMessage(self.mainWindow.atm))
        QTest.mouseClick(self.mainWindow.atm.test_dict["b_deposit"], Qt.LeftButton)
        QTest.qWait(1000)
        self.assertTrue(self.msgBoxText.startswith("$1000.00 deposited successfully"))
        # get end balance:
        end_balance = self.getDispayBalance()
        self.assertEqual(start_balance + 1000.00, end_balance)
    @unittest.skip("input line no longer support input zero and confirm")
    def test_003_deposit_zero(self):
        print("[Test-003]")
        # Click deposit button
        # Wait for 2s for the dialog box to appear
        QTimer.singleShot(2000, lambda: self.simulateInputDialog(self.mainWindow.atm.test_dict["d_dialog"], "0"))
        # Wait for 3s for the message box to appear
        QTimer.singleShot(3000, lambda: self.simulateClickMessage(self.mainWindow.atm))
        # Wait for 4s to cancel the dialog
        QTimer.singleShot(4000, lambda: self.simulateCancelDialog(self.mainWindow.atm.test_dict["d_dialog"]))
        QTest.mouseClick(self.mainWindow.atm.test_dict["b_deposit"], Qt.LeftButton)
        QTest.qWait(1000)
        self.assertTrue(self.msgBoxText.startswith("Deposit amount must be between $0.01 and $50000.00"))
    @unittest.skip("input line no longer support input negative")
    def test_004_deposit_negative(self):
        print("[Test-004]")
        # Click deposit button
        # Wait for 2s for the dialog box to appear
        QTimer.singleShot(2000, lambda: self.simulateInputDialog(self.mainWindow.atm.test_dict["d_dialog"], "-1"))
        # Wait for 3s for the message box to appear
        QTimer.singleShot(3000, lambda: self.simulateClickMessage(self.mainWindow.atm))
        # Wait for 4s to cancel the dialog
        QTimer.singleShot(4000, lambda: self.simulateCancelDialog(self.mainWindow.atm.test_dict["d_dialog"]))
        QTest.mouseClick(self.mainWindow.atm.test_dict["b_deposit"], Qt.LeftButton)
        QTest.qWait(1000)
        self.assertTrue(self.msgBoxText.startswith("Deposit amount must be between $0.01 and $50000.00"))
    @unittest.skip("input line no longer support over limit")
    def test_005_deposit_over_limit(self):
        print("[Test-005]")
        # Click deposit button
        # Wait for 2s for the dialog box to appear
        QTimer.singleShot(2000, lambda: self.simulateInputDialog(self.mainWindow.atm.test_dict["d_dialog"], "501"))
        # Wait for 3s for the message box to appear
        QTimer.singleShot(3000, lambda: self.simulateClickMessage(self.mainWindow.atm))
        # Wait for 4s to cancel the dialog
        QTimer.singleShot(4000, lambda: self.simulateCancelDialog(self.mainWindow.atm.test_dict["d_dialog"]))
        QTest.mouseClick(self.mainWindow.atm.test_dict["b_deposit"], Qt.LeftButton)
        QTest.qWait(1000)
        self.assertTrue(self.msgBoxText.startswith("Deposit amount must be between $0.01 and $50000.00"))
    def test_006_withdraw_common(self):
        print("[Test-006]")
        # get start balance:
        start_balance = self.getDispayBalance()
        # Click withdraw button
        # Wait for 2s for the dialog box to appear
        QTimer.singleShot(2000, lambda: self.simulateInputDialog(self.mainWindow.atm.test_dict["d_dialog"], "5"))
        # Wait for 3s for the message box to appear
        QTimer.singleShot(3000, lambda: self.simulateClickMessage(self.mainWindow.atm))
        QTest.mouseClick(self.mainWindow.atm.test_dict["b_withdraw"], Qt.LeftButton)
        QTest.qWait(1000)
        self.assertTrue(self.msgBoxText.startswith("$500.00 withdrawn successfully"))
        # get end balance:
        end_balance = self.getDispayBalance()
        self.assertEqual(start_balance - 500.00, end_balance)
    @unittest.skip("input line no longer support input zero and confirm")
    def test_007_withdraw_zero(self):
        print("[Test-007]")
        # Click withdraw button
        # Wait for 2s for the dialog box to appear
        QTimer.singleShot(2000, lambda: self.simulateInputDialog(self.mainWindow.atm.test_dict["d_dialog"], "0"))
        # Wait for 3s for the message box to appear
        QTimer.singleShot(3000, lambda: self.simulateClickMessage(self.mainWindow.atm))
        # Wait for 4s to cancel the dialog
        QTimer.singleShot(4000, lambda: self.simulateCancelDialog(self.mainWindow.atm.test_dict["d_dialog"]))
        QTest.mouseClick(self.mainWindow.atm.test_dict["b_withdraw"], Qt.LeftButton)
        QTest.qWait(1000)
        self.assertTrue(self.msgBoxText.startswith("Withdrawal amount must be between $0.01 and $50000.00"))
    @unittest.skip("input line no longer support input negative")
    def test_008_withdraw_negative(self):
        print("[Test-008]")
        # Click withdraw button
        # Wait for 2s for the dialog box to appear
        QTimer.singleShot(2000, lambda: self.simulateInputDialog(self.mainWindow.atm.test_dict["d_dialog"], "-1"))
        # Wait for 3s for the message box to appear
        QTimer.singleShot(3000, lambda: self.simulateClickMessage(self.mainWindow.atm))
        # Wait for 4s to cancel the dialog
        QTimer.singleShot(4000, lambda: self.simulateCancelDialog(self.mainWindow.atm.test_dict["d_dialog"]))
        QTest.mouseClick(self.mainWindow.atm.test_dict["b_withdraw"], Qt.LeftButton)
        QTest.qWait(1000)
        self.assertTrue(self.msgBoxText.startswith("Withdrawal amount must be between $0.01 and $50000.00"))
    @unittest.skip("input line no longer support over limit")
    def test_009_withdraw_over_limit(self):
        print("[Test-009]")
        # Click withdraw button
        # Wait for 2s for the dialog box to appear
        QTimer.singleShot(2000, lambda: self.simulateInputDialog(self.mainWindow.atm.test_dict["d_dialog"], "501"))
        # Wait for 3s for the message box to appear
        QTimer.singleShot(3000, lambda: self.simulateClickMessage(self.mainWindow.atm))
        # Wait for 4s to cancel the dialog
        QTimer.singleShot(4000, lambda: self.simulateCancelDialog(self.mainWindow.atm.test_dict["d_dialog"]))
        QTest.mouseClick(self.mainWindow.atm.test_dict["b_withdraw"], Qt.LeftButton)
        QTest.qWait(1000)
        self.assertTrue(self.msgBoxText.startswith("Withdrawal amount must be between $0.01 and $50000.00"))
    def test_010_withdraw_over_balance(self):
        print("[Test-010]")
        # Click withdraw button
        # Wait for 2s for the dialog box to appear
        QTimer.singleShot(2000, lambda: self.simulateInputDialog(self.mainWindow.atm.test_dict["d_dialog"], "20"))
        # Wait for 3s for the message box to appear
        QTimer.singleShot(3000, lambda: self.simulateClickMessage(self.mainWindow.atm))
        # Wait for 4s to cancel the dialog
        QTimer.singleShot(4000, lambda: self.simulateCancelDialog(self.mainWindow.atm.test_dict["d_dialog"]))
        QTest.mouseClick(self.mainWindow.atm.test_dict["b_withdraw"], Qt.LeftButton)
        QTest.qWait(1000)
        self.assertTrue(self.msgBoxText.startswith("Insufficient account balance for withdrawal"))
    def test_011_return_card(self):
        print("[Test-011]")
        # Wait for 1s for the message box to appear
        QTimer.singleShot(1000, lambda: self.simulateClickMessage(self.mainWindow.atm))
        QTest.mouseClick(self.mainWindow.atm.test_dict["b_return"], Qt.LeftButton)
        self.assertEqual(self.msgBoxText, "Card returned successfully")
    def test_012_log_in_wrong_id(self):
        print("[Test-012]")
        # Click log in button
        QTest.mouseClick(self.mainWindow.atm.test_dict["b_login"], Qt.LeftButton)
        QTest.qWait(1000)
        QTest.keyClicks(self.mainWindow.atm.test_dict["i_id"], "2024987654")
        QTest.qWait(1000)
        QTest.keyClicks(self.mainWindow.atm.test_dict["i_password"], "123456")
        QTest.qWait(1000)
        # Wait for 2s for the message box to appear
        QTimer.singleShot(2000, lambda: self.simulateClickMessage(self.mainWindow.atm))
        QTest.mouseClick(self.mainWindow.atm.test_dict["b_confirm"], Qt.LeftButton)
        self.assertEqual(self.msgBoxText, "Invalid account ID")
    def test_013_log_in_wrong_id_and_password(self):
        print("[Test-013]")
        # Click log in button
        QTest.mouseClick(self.mainWindow.atm.test_dict["b_login"], Qt.LeftButton)
        QTest.qWait(1000)
        QTest.keyClicks(self.mainWindow.atm.test_dict["i_id"], "123451")
        QTest.qWait(1000)
        QTest.keyClicks(self.mainWindow.atm.test_dict["i_password"], "654321")
        QTest.qWait(1000)
        # Wait for 2s for the message box to appear
        QTimer.singleShot(2000, lambda: self.simulateClickMessage(self.mainWindow.atm))
        QTest.mouseClick(self.mainWindow.atm.test_dict["b_confirm"], Qt.LeftButton)
        self.assertEqual(self.msgBoxText, "Invalid account ID")
    def test_014_log_in_wrong_password(self):
        print("[Test-014]")
        # Click log in button
        QTest.mouseClick(self.mainWindow.atm.test_dict["b_login"], Qt.LeftButton)
        QTest.qWait(1000)
        QTest.keyClicks(self.mainWindow.atm.test_dict["i_id"], "2024123456")
        QTest.qWait(1000)
        QTest.keyClicks(self.mainWindow.atm.test_dict["i_password"], "654321")
        QTest.qWait(1000)
        # Wait for 2s for the message box to appear
        QTimer.singleShot(2000, lambda: self.simulateClickMessage(self.mainWindow.atm))
        QTest.mouseClick(self.mainWindow.atm.test_dict["b_confirm"], Qt.LeftButton)
        self.assertEqual(self.msgBoxText, "Invalid password")
    def test_015_log_in_common(self):
        print("[Test-015]")
        # Click log in button
        QTest.mouseClick(self.mainWindow.atm.test_dict["b_login"], Qt.LeftButton)
        # QTest.qWait(1000)
        # QTest.keyClicks(self.mainWindow.atm.test_dict["i_id"], "1234567890")
        QTest.qWait(1000)
        QTest.keyClicks(self.mainWindow.atm.test_dict["i_password"], "123456")
        QTest.qWait(1000)
        # Wait for 2s for the message box to appear
        QTimer.singleShot(2000, lambda: self.simulateClickMessage(self.mainWindow.atm))
        QTest.mouseClick(self.mainWindow.atm.test_dict["b_confirm"], Qt.LeftButton)
        self.assertEqual(self.msgBoxText, "Insert card successfully")
    @unittest.skip("input line no longer support input non digit")
    def test_016_change_password_notObeyFormat(self):
        print("[Test-016]")
        # Wait for 2s for the dialog box to appear
        QTimer.singleShot(2000, lambda: self.simulateInputDialog(self.mainWindow.atm.test_dict["d_dialog"], "j12re7"))
        # Wait for 3s for the message box to appear
        QTimer.singleShot(3000, lambda: self.simulateClickMessage(self.mainWindow.atm))
        # Wait for 4s to cancel the dialog
        QTimer.singleShot(4000, lambda: self.simulateCancelDialog(self.mainWindow.atm.test_dict["d_dialog"]))
        # Click change password button
        QTest.mouseClick(self.mainWindow.atm.test_dict["b_change_password"], Qt.LeftButton)
        QTest.qWait(1000)
        self.assertEqual(self.msgBoxText, "Password must consist of 6 digits")
    def test_017_change_password_sameAsOldPwd(self):
        print("[Test-017]")
        # Wait for 2s for the dialog box to appear
        QTimer.singleShot(2000, lambda: self.simulateInputDialog(self.mainWindow.atm.test_dict["d_dialog"], "123456"))
        # Wait for 3s for the message box to appear
        QTimer.singleShot(3000, lambda: self.simulateClickMessage(self.mainWindow.atm))
        # Wait for 4s to cancel the dialog
        QTimer.singleShot(4000, lambda: self.simulateCancelDialog(self.mainWindow.atm.test_dict["d_dialog"]))
        # Click change password button
        QTest.mouseClick(self.mainWindow.atm.test_dict["b_change_password"], Qt.LeftButton)
        QTest.qWait(1000)
        self.assertEqual(self.msgBoxText, "New password cannot be the same as the old password")
    def test_018_change_password_common(self):
        print("[Test-018]")
        # Wait for 2s for the dialog box to appear
        QTimer.singleShot(2000, lambda: self.simulateInputDialog(self.mainWindow.atm.test_dict["d_dialog"], "654321"))
        # Wait for 3s for the message box to appear
        QTimer.singleShot(3000, lambda: self.simulateClickMessage(self.mainWindow.atm))
        # Wait for 4s to verify the message Box
        QTimer.singleShot(4000, lambda: self.assertEqual(self.msgBoxText, "Password changed successfully"))
        # Wait for 5s for another message box
        QTimer.singleShot(5000, lambda: self.simulateClickMessage(self.mainWindow.atm))
        # Wait for 6s to verify the other message Box
        QTimer.singleShot(6000, lambda: self.assertEqual(self.msgBoxText, "Card returned successfully"))
        # Click change password button
        QTest.mouseClick(self.mainWindow.atm.test_dict["b_change_password"], Qt.LeftButton)
        QTest.qWait(1000)
    def test_019_create_account_InvalidId(self): 
        print("[Test-019]")
        # Click create account button
        QTest.mouseClick(self.mainWindow.atm.test_dict["b_create"], Qt.LeftButton)
        QTest.qWait(1000)
        QTest.keyClicks(self.mainWindow.atm.test_dict["i_id"], "1234O6789")
        QTest.qWait(1000)
        QTest.keyClicks(self.mainWindow.atm.test_dict["i_password"], "654321")
        QTest.qWait(1000)
        # Wait for 2s for the message box to appear
        QTimer.singleShot(2000, lambda: self.simulateClickMessage(self.mainWindow.atm))
        QTest.mouseClick(self.mainWindow.atm.test_dict["b_confirm"], Qt.LeftButton)
        self.assertEqual(self.msgBoxText, "Account ID must consist of 10 digits")
    def test_020_create_account_InvalidPassword(self):
        print("[Test-020]")
        # Click create account button
        QTest.mouseClick(self.mainWindow.atm.test_dict["b_create"], Qt.LeftButton)
        QTest.qWait(1000)
        QTest.keyClicks(self.mainWindow.atm.test_dict["i_id"], "2024654321")
        QTest.qWait(1000)
        QTest.keyClicks(self.mainWindow.atm.test_dict["i_password"], "jsk1!-=234")
        QTest.qWait(1000)
        # Wait for 2s for the message box to appear
        QTimer.singleShot(2000, lambda: self.simulateClickMessage(self.mainWindow.atm))
        QTest.mouseClick(self.mainWindow.atm.test_dict["b_confirm"], Qt.LeftButton)
        self.assertEqual(self.msgBoxText, "Password must consist of 6 digits")
        QTest.qWait(1000)
        QTest.mouseClick(self.mainWindow.atm.test_dict["b_back"], Qt.LeftButton)
    def test_021_create_account_alreadyExist(self):
        print("[Test-021]")   
        # Click create account button
        QTest.mouseClick(self.mainWindow.atm.test_dict["b_create"], Qt.LeftButton)
        QTest.qWait(1000)
        QTest.keyClicks(self.mainWindow.atm.test_dict["i_id"], "2024123456")
        QTest.qWait(1000)
        QTest.keyClicks(self.mainWindow.atm.test_dict["i_password"], "654321")
        QTest.qWait(1000)
        # Wait for 2s for the message box to appear
        QTimer.singleShot(2000, lambda: self.simulateClickMessage(self.mainWindow.atm))
        QTest.mouseClick(self.mainWindow.atm.test_dict["b_confirm"], Qt.LeftButton)
        self.assertEqual(self.msgBoxText, "Account already exists")
    def test_022_create_account_and_deposit(self):
        print("[Test-022]")
        # 1. CREATE ACCOUNT
        # Click create account button
        QTest.mouseClick(self.mainWindow.atm.test_dict["b_create"], Qt.LeftButton)
        QTest.qWait(1000)
        QTest.keyClicks(self.mainWindow.atm.test_dict["i_id"], "2024654321")
        QTest.qWait(1000)
        QTest.keyClicks(self.mainWindow.atm.test_dict["i_password"], "654321")
        QTest.qWait(1000)
        # Wait for 2s for the message box to appear
        QTimer.singleShot(2000, lambda: self.simulateClickMessage(self.mainWindow.atm))
        QTest.mouseClick(self.mainWindow.atm.test_dict["b_confirm"], Qt.LeftButton)
        self.assertEqual(self.msgBoxText, "Account created successfully")
        # 2. DEPOSIT
        # get start balance:
        start_balance = self.getDispayBalance()
        # Click deposit button
        # Wait for 2s for the message box to appear
        QTimer.singleShot(2000, lambda: self.simulateInputDialog(self.mainWindow.atm.test_dict["d_dialog"], "10"))
        # Wait for 3s for the message box to appear
        QTimer.singleShot(3000, lambda: self.simulateClickMessage(self.mainWindow.atm))
        QTest.mouseClick(self.mainWindow.atm.test_dict["b_deposit"], Qt.LeftButton)
        QTest.qWait(1000)
        self.assertTrue(self.msgBoxText.startswith("$1000.00 deposited successfully"))
        # get end balance:
        end_balance = self.getDispayBalance()
        self.assertEqual(start_balance + 1000.00, end_balance)
    def test_023_transfer_invalid_id(self):
        print("[Test-023]")
        # Wait for 2s for the dialog box to appear (input accountID)
        QTimer.singleShot(2000, lambda: self.simulateInputDialog(self.mainWindow.atm.test_dict["d_dialog"], "123456789"))
        # Wait for 3s for the message box to appear (input money)
        QTimer.singleShot(5000, lambda: self.simulateInputDialog(self.mainWindow.atm.test_dict["d_dialog"], "1"))
        # Wait for 4s for the message box to appear
        QTimer.singleShot(6000, lambda: self.simulateClickMessage(self.mainWindow.atm))
        # Wait for 5s to cancel the dialog
        QTimer.singleShot(7000, lambda: self.simulateCancelDialog(self.mainWindow.atm.test_dict["d_dialog"]))

        QTest.mouseClick(self.mainWindow.atm.test_dict["b_transfer"], Qt.LeftButton)
        self.assertEqual(self.msgBoxText, "Receiver's account ID must consist of 10 digits")
    def test_024_transfer_invalid_money(self):
        print("[Test-024]")
        # Wait for 2s for the dialog box to appear (input accountID)
        QTimer.singleShot(2000, lambda: self.simulateInputDialog(self.mainWindow.atm.test_dict["d_dialog"], "2024123456"))
        # Wait for 3s for the message box to appear (input money)
        QTimer.singleShot(3000, lambda: self.simulateInputDialog(self.mainWindow.atm.test_dict["d_dialog"], "jqk0"))
        # Wait for 4s for the message box to appear
        QTimer.singleShot(4000, lambda: self.simulateClickMessage(self.mainWindow.atm))
        # Wait for 5s to cancel the dialog
        QTimer.singleShot(5000, lambda: self.simulateCancelDialog(self.mainWindow.atm.test_dict["d_dialog"]))
        
        QTest.mouseClick(self.mainWindow.atm.test_dict["b_transfer"], Qt.LeftButton)
        self.assertEqual(self.msgBoxText, "Transfer amount must be between $0.01 and $50000.00")
    def test_025_transfer_over_balance(self):
        print("[Test-025]")
        # Wait for 2s for the dialog box to appear (input accountID)
        QTimer.singleShot(2000, lambda: self.simulateInputDialog(self.mainWindow.atm.test_dict["d_dialog"], "2024123456"))
        # Wait for 3s for the message box to appear (input money)
        QTimer.singleShot(5000, lambda: self.simulateInputDialog(self.mainWindow.atm.test_dict["d_dialog"], "9000.00"))
        # Wait for 4s for the message box to appear
        QTimer.singleShot(6000, lambda: self.simulateClickMessage(self.mainWindow.atm))
        # Wait for 5s to cancel the dialog
        QTimer.singleShot(7000, lambda: self.simulateCancelDialog(self.mainWindow.atm.test_dict["d_dialog"]))

        QTest.mouseClick(self.mainWindow.atm.test_dict["b_transfer"], Qt.LeftButton)
        self.assertEqual(self.msgBoxText, "Insufficient account balance for transfer")
    def test_026_transfer_to_itself(self):
        print("[Test-026]")
        # Wait for 2s for the dialog box to appear (input accountID)
        QTimer.singleShot(2000, lambda: self.simulateInputDialog(self.mainWindow.atm.test_dict["d_dialog"], "2024654321"))
        # Wait for 3s for the message box to appear (input money)
        QTimer.singleShot(5000, lambda: self.simulateInputDialog(self.mainWindow.atm.test_dict["d_dialog"], "10"))
        # Wait for 4s for the message box to appear
        QTimer.singleShot(6000, lambda: self.simulateClickMessage(self.mainWindow.atm))
        # Wait for 5s to cancel the dialog
        QTimer.singleShot(7000, lambda: self.simulateCancelDialog(self.mainWindow.atm.test_dict["d_dialog"]))

        QTest.mouseClick(self.mainWindow.atm.test_dict["b_transfer"], Qt.LeftButton)
        self.assertEqual(self.msgBoxText, "Can't tranfer to your own")
    def test_027_transfer_notExistID(self):
        print("[Test-027]")
        # Wait for 2s for the dialog box to appear (input accountID)
        QTimer.singleShot(2000, lambda: self.simulateInputDialog(self.mainWindow.atm.test_dict["d_dialog"], "2024987654"))
        # Wait for 3s for the message box to appear (input money)
        QTimer.singleShot(5000, lambda: self.simulateInputDialog(self.mainWindow.atm.test_dict["d_dialog"], "10"))
        # Wait for 4s for the message box to appear
        QTimer.singleShot(6000, lambda: self.simulateClickMessage(self.mainWindow.atm))
        # Wait for 5s to cancel the dialog
        QTimer.singleShot(7000, lambda: self.simulateCancelDialog(self.mainWindow.atm.test_dict["d_dialog"]))

        QTest.mouseClick(self.mainWindow.atm.test_dict["b_transfer"], Qt.LeftButton)
        self.assertEqual(self.msgBoxText, "Invalid receiver account ID")
    def test_028_transfer_common(self):
        print("[Test-028]")
        balance = self.getDispayBalance()
       
        # Wait for 2s for the dialog box to appear (input accountID)
        QTimer.singleShot(2000, lambda: self.simulateInputDialog(self.mainWindow.atm.test_dict["d_dialog"], "2024123456"))
        # Wait for 3s for the message box to appear (input money)
        QTimer.singleShot(5000, lambda: self.simulateInputDialog(self.mainWindow.atm.test_dict["d_dialog"], "100"))
        # Wait for 4s for the message box to appear
        QTimer.singleShot(6000, lambda: self.simulateClickMessage(self.mainWindow.atm))

        QTest.mouseClick(self.mainWindow.atm.test_dict["b_transfer"], Qt.LeftButton)
        self.assertTrue(self.msgBoxText.startswith("$100.00 transferred successfully"))
        # get end balance:
        end_balance = self.getDispayBalance()
        self.assertEqual(balance - 100.00, end_balance)
    def test_029_cancel_account_BalanceNotZero(self):
        print("[Test-029]")
        # Wait for 2s for the confirm message box to appear
        QTimer.singleShot(2000, lambda: self.simulateYesMessage(self.mainWindow.atm))
        # Wait for 3s for the error message box to appear
        QTimer.singleShot(3000, lambda: self.simulateClickMessage(self.mainWindow.atm))
        # Click cancel account button
        QTest.mouseClick(self.mainWindow.atm.test_dict["b_cancel"], Qt.LeftButton)
        
        self.assertEqual(self.msgBoxText, "Account balance must be zero to cancel the account")
    def test_030_transfer_allBalance(self):
        print("[Test-030]")
        balance = self.getDispayBalance()
       
        # Wait for 2s for the dialog box to appear (input accountID)
        QTimer.singleShot(2000, lambda: self.simulateInputDialog(self.mainWindow.atm.test_dict["d_dialog"], "2024123456"))
        # Wait for 3s for the message box to appear (input money)
        QTimer.singleShot(5000, lambda: self.simulateInputDialog(self.mainWindow.atm.test_dict["d_dialog"], str(balance)))
        # Wait for 4s for the message box to appear
        QTimer.singleShot(6000, lambda: self.simulateClickMessage(self.mainWindow.atm))

        QTest.mouseClick(self.mainWindow.atm.test_dict["b_transfer"], Qt.LeftButton)
        self.assertTrue(self.msgBoxText.startswith(f"${balance:.2f} transferred successfully"))
        # get end balance:
        end_balance = self.getDispayBalance()
        self.assertEqual(0.00, end_balance)
    def test_031_cancel_account_BalanceZero(self):
        print("[Test-031]")
        # Wait for 2s for the message box to appear
        QTimer.singleShot(2000, lambda: self.simulateYesMessage(self.mainWindow.atm))
        # Wait for 3s for the result message box to appear
        QTimer.singleShot(3000, lambda: self.simulateClickMessage(self.mainWindow.atm))
        # Click cancel account button
        QTest.mouseClick(self.mainWindow.atm.test_dict["b_cancel"], Qt.LeftButton)
        
        self.assertEqual(self.msgBoxText, "Account canceled successfully")

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

    def getDispayBalance(self)->float:
        "Account ID: {self.current_account_id}\nBalance: ${balance:.2f}"
        return float(self.mainWindow.atm.test_dict["l_account"].text().split("$")[1])

    def simulateYesMessage(self,ui_window:QWidget):
        # Find the active message box and click the "Yes" button
        active_message_box = ui_window.findChild(QMessageBox)
        if active_message_box:
            yes_button = active_message_box.button(QMessageBox.Yes)
            if yes_button:
                QTest.mouseClick(yes_button, Qt.LeftButton)
if __name__ == "__main__":
    unittest.main()
