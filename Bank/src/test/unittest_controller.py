import unittest
from unittest.mock import MagicMock, patch
from PyQt5.QtWidgets import QApplication, QMainWindow, QMessageBox, QInputDialog,QDialog,QLineEdit,QWidget
from PyQt5.QtTest import QTest
from PyQt5.QtCore import Qt,QTimer

import sys
import os
import time

from src.frontend.Controller import Controller  # Replace 'your_module' with the actual module name

class TestController(unittest.TestCase):

    def setUp(self):
        self.app = QApplication(sys.argv)
        self.zmqThread = MagicMock()
        self.controller = Controller(self.zmqThread)

    def tearDown(self):
        self.controller.close()
        for appid,appinstance in self.controller.app_instances.items():
            appinstance.close()
        self.controller.atm.close()
        self.app.quit()
        time.sleep(0.5)

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


    def test_001_initUI(self):
        self.assertIsInstance(self.controller, QMainWindow)
        self.assertEqual(self.controller.windowTitle(), 'Main Window')
        self.assertEqual(self.controller.label.text(), 'Banking System Controller')

    def test_002_open_app(self):
        initial_num_apps = self.controller.num_apps_opened
        self.controller.open_app()
        self.assertEqual(self.controller.num_apps_opened, initial_num_apps + 1)
        self.assertIn(str(self.controller.num_apps_opened), self.controller.app_instances)
    @patch('PyQt5.QtWidgets.QMessageBox.warning')
    def test_004_close_app_logged_in(self,mock_warning):
        # Simulate opening an app
        self.controller.open_app()
        app_id = str(self.controller.num_apps_opened)
        app_instance = self.controller.app_instances[app_id]
        app_instance.logged_in = True
        QTimer.singleShot(500, lambda: self.simulateInputDialog(self.controller.test_dict["d_dialog"], app_id))
        QTimer.singleShot(700, lambda:mock_warning.assert_called_with(self.controller, "Warning", "Please log out before closing the app."))
        self.controller.close_app()
    def test_003_close_app(self):
        # Simulate opening an app
        self.controller.open_app()
        app_id = str(self.controller.num_apps_opened)
        app_instance = self.controller.app_instances[app_id]
        QTimer.singleShot(500, lambda: self.simulateInputDialog(self.controller.test_dict["d_dialog"], app_id))
        self.controller.close_app()
    @patch('PyQt5.QtWidgets.QMessageBox.warning')
    def test_005_close_app_notopen(self,mock_warning):
        QTimer.singleShot(500, lambda: self.simulateInputDialog(self.controller.test_dict["d_dialog"], "9"))
        QTimer.singleShot(700, lambda:mock_warning.assert_called_with(self.controller,  "Error", "App with specified ID is not open."))
        self.controller.close_app()
    

if __name__ == '__main__':
    unittest.main()
