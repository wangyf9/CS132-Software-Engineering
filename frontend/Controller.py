from PyQt5.QtWidgets import QWidget, QMainWindow, QLabel, QPushButton, QMessageBox, QInputDialog, QApplication, QVBoxLayout, QHBoxLayout, QFrame, QGridLayout
from PyQt5.QtCore import pyqtSignal, Qt
from PyQt5.QtGui import QFont
import sys
import os
import APP_UI
import NetClient
import ATM_UI
import sqlite3
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from backend.bank import reset_database

class Controller(QMainWindow):
    operationInProgress = pyqtSignal(int, bool)  # Signal with account ID and operation status
    def __init__(self, zmqThread):
        super().__init__()
        self.zmqThread = zmqThread
        self.num_apps_opened = 0
        self.app_instances = {}
        self.logging_in_accounts = {}
        self.account_operations = {}  # Account ID to operation status mapping
        self.initUI()
        self.atm = ATM_UI.ATM(zmqThread, self)
        self.atm.show()
        self.atm.password_changed.connect(self.handle_password_changed_atm)
        self.atm.balance_changed.connect(self.handle_balance_changed_atm)
        self.atm.transfer_changed.connect(self.handle_transfer_changed_atm)
        self.create_test_dict()
        
    def initUI(self):
        self.label = QLabel('Banking System Controller', self)

        self.openAppButton = QPushButton('Open App', self)
        self.openAppButton.clicked.connect(self.open_app)

        self.closeAppButton = QPushButton('Close App', self)
        self.closeAppButton.clicked.connect(self.close_app)

        self.resetButton = QPushButton('Reset System Database', self)
        self.resetButton.clicked.connect(self.reset)

        # Set font
        font = QFont()
        font.setFamily("Times New Roman")
        font.setBold(True)
        font.setItalic(True)
        font.setPointSize(12)
        self.label.setFont(font)
        self.openAppButton.setFont(font)
        self.closeAppButton.setFont(font)
        self.resetButton.setFont(font)

        # Main layout
        main_layout = QVBoxLayout()

        # Title section
        title_layout = QVBoxLayout()
        title_layout.addWidget(self.label, alignment=Qt.AlignCenter)

        title_frame = QFrame(self)
        title_frame.setLayout(title_layout)
        title_frame.setFrameShape(QFrame.Box)
        title_frame.setFrameShadow(QFrame.Sunken)

        # Buttons section
        buttons_layout = QVBoxLayout()
        buttons_layout.addWidget(self.openAppButton, alignment=Qt.AlignCenter)
        buttons_layout.addWidget(self.closeAppButton, alignment=Qt.AlignCenter)
        buttons_layout.addWidget(self.resetButton, alignment=Qt.AlignCenter)

        buttons_frame = QFrame(self)
        buttons_frame.setLayout(buttons_layout)
        buttons_frame.setFrameShape(QFrame.Box)
        buttons_frame.setFrameShadow(QFrame.Sunken)

        main_layout.addWidget(title_frame)
        main_layout.addWidget(buttons_frame)

        # Create a central widget and set the layout on it
        central_widget = QWidget()
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)

        self.setWindowTitle('Main Window')
        self.setGeometry(300, 300, 400, 400)

    def open_app(self):
        self.num_apps_opened += 1
        appid = self.num_apps_opened
        new_app = APP_UI.APP(self.zmqThread, int(appid), self)  # Pass as integer to APP
        self.connect_signals(new_app)
        new_app.show()
        self.app_instances[str(appid)] = new_app

    def close_app(self):
        dialog = QInputDialog(self)
        dialog.setInputMode(QInputDialog.IntInput)
        dialog.setWindowTitle('Close App')
        dialog.setLabelText('Enter app ID:')
        # dialog.setIntRange(1, 99)  # Set range for the input
        dialog.setIntValue(1)  # Set default value
        self.test_dict["d_dialog"]=dialog 
        
        ok = dialog.exec_()
        if ok:
            app_id = str(dialog.intValue())
            if app_id in self.app_instances:
                self.app_instances[app_id].close()
            else:
                QMessageBox.warning(self, "Error", "App with specified ID is not open.")

    def connect_signals(self, app_instance):
        app_instance.closed.connect(self.handle_app_closed)
        app_instance.operationInProgress.connect(self.set_operatoin_status)
        app_instance.password_changed.connect(self.handle_password_changed_app)
        app_instance.balance_changed.connect(self.handle_balance_changed_app)
        app_instance.transfer_changed.connect(self.handle_transfer_changed_app)

    def handle_app_closed(self, app_id):
        del self.app_instances[str(app_id)]
        # self.num_apps_opened -= 1
    
    def whether_logging_in(self, account_id):
        if self.logging_in_accounts.get(account_id) is not None:
            self.logging_in_accounts[account_id].log_out()

    def set_log_status(self, app_instance, account_id, app_id):
        if app_id is not None:
            self.logging_in_accounts[account_id] = app_instance
        else:
            if account_id in self.logging_in_accounts:
                del self.logging_in_accounts[account_id]

    def set_operatoin_status(self, account_id, in_progress):
        if in_progress:
            self.account_operations[account_id] = True
        else:
            if account_id in self.account_operations:
                del self.account_operations[account_id]

    def whether_processing(self, account_id):
        return self.account_operations.get(account_id, False)
    
    def handle_password_changed_atm(self, account_id):
        for app_id, app_instance in self.app_instances.items():
            if app_instance.logged_in and (int(app_instance.current_account_id) == account_id):
                app_instance.log_out()

    def handle_password_changed_app(self, account_id):
        if self.atm.current_account_id is not None and int(self.atm.current_account_id) == account_id:
            self.atm.return_card()

    def handle_balance_changed_atm(self, account_id):
        for app_id, app_instance in self.app_instances.items():
            if app_instance.logged_in and (int(app_instance.current_account_id) == account_id):
                app_instance.update_account_info()

    def handle_balance_changed_app(self, account_id):
        if self.atm.current_account_id is not None and int(self.atm.current_account_id) == account_id:
            self.atm.update_account_info()

    def handle_transfer_changed_atm(self, account_id):
        for app_id, app_instance in self.app_instances.items():
            if app_instance.logged_in and (int(app_instance.current_account_id) == account_id):
                app_instance.update_account_info()

    def handle_transfer_changed_app(self, account_id):
        if self.atm.current_account_id is not None and int(self.atm.current_account_id) == account_id:
            self.atm.update_account_info()

    def reset(self):
        confirmation = QMessageBox.question(self, 'Reset Database', 'Are you sure you want to reset the database?', QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if confirmation == QMessageBox.Yes:
            reset_database()
            QMessageBox.information(self, 'Success', 'Database has been reset.')
    
    def create_test_dict(self):
        self.test_dict={
        # "b_open":self.openAppButton,
        "b_close":self.closeAppButton,
        "b_reset":self.resetButton,
        "d_dialog":None,
        }
    
if __name__ == '__main__':
    identity = "Team15"
    zmqThread = NetClient.ZmqClientThread(identity=identity)
    app = QApplication(sys.argv)
    mainWindow = Controller(zmqThread)
    mainWindow.show()
    sys.exit(app.exec_())
