from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QLabel, QLineEdit, QMessageBox, QInputDialog
from PyQt5.QtGui import QCloseEvent, QFont
import time
from PyQt5.QtCore import pyqtSignal

class APP(QWidget):
    # This is a front end communication signal
    closed = pyqtSignal(int)
    operationInProgress = pyqtSignal(int, bool)
    def __init__(self, zmqThread, app_id, main_window):
        super().__init__()
        self.zmqThread = zmqThread
        self.app_id = app_id
        self.main_window = main_window
        self.initUI()

    def log_in(self):
        account_id = self.id_input.text()
        password = self.password_input.text()

        # Send login request to backend
        self.zmqThread.sendMsg(f"log_in@{account_id}@{password}")
        time.sleep(0.1)  # Wait for backend processing
        response = self.zmqThread.receivedMessage

        if response.startswith("error@"):
            QMessageBox.warning(self, "Error", response.split("@")[2])
            if response.split("@")[1] == 'A': ## account error
                self.id_input.clear()
                self.password_input.clear()
            elif response.split("@")[1] == 'B': ## password error
                self.password_input.clear()
            return False
        
        if self.main_window.whether_logging_in(account_id):
            QMessageBox.warning(self, "Error", f"Account {account_id} is already logged in another App.")
            self.id_input.clear()
            self.password_input.clear()
            return False
        
        self.main_window.set_log_status(account_id, self.app_id)
        QMessageBox.information(self, "Success", "Log in successfully")
        return True
    
    def change_password(self):
        if self.main_window.whether_processing(self.current_account_id):
            QMessageBox.warning(self, "Error", "Another operation is in progress in ATM.")
            return
        while True:
            self.operationInProgress.emit(self.current_account_id, True)
            self.main_window.set_operatoin_status(self.current_account_id, True)
            new_password, ok = QInputDialog.getText(self, "Change Password", "Enter new password:")
            if not ok:
                self.operationInProgress.emit(self.current_account_id, False)
                self.main_window.set_operatoin_status(self.current_account_id, False)
                return
            
            # Send change password request to backend
            self.zmqThread.sendMsg(f"change_password@{self.current_account_id}@{new_password}")
            time.sleep(0.1)  # Wait for backend processing
            response = self.zmqThread.receivedMessage

            if response.startswith("error@"):
                QMessageBox.warning(self, "Error", response.split("@")[1])
                continue

            QMessageBox.information(self, "Success", "Password changed successfully")
            self.show_initial_page()
            break
        self.operationInProgress.emit(self.current_account_id, False)
        self.main_window.set_operatoin_status(self.current_account_id, False)

    def transfer_money(self):
        if self.main_window.whether_processing(self.current_account_id):
            QMessageBox.warning(self, "Error", "Another operation is in progress in ATM.")
            return
        while True:
            self.operationInProgress.emit(self.current_account_id, True)
            self.main_window.set_operatoin_status(self.current_account_id, True)
            receiver_id, ok = QInputDialog.getText(self, "Transfer Money", "Enter receiver's account ID:")
            if not ok:
                self.operationInProgress.emit(self.current_account_id, False)
                self.main_window.set_operatoin_status(self.current_account_id, False)
                return
            
            amount, ok = QInputDialog.getDouble(self, "Transfer Money", "Enter amount to transfer:", decimals=2)
            if not ok:
                self.operationInProgress.emit(self.current_account_id, False)
                self.main_window.set_operatoin_status(self.current_account_id, False)
                return

            # Send transfer money request to backend
            self.zmqThread.sendMsg(f"transfer_money@{self.current_account_id}@{receiver_id}@{amount}")
            time.sleep(0.1)  # Wait for backend processing
            response = self.zmqThread.receivedMessage
            if response.startswith("error@"):
                QMessageBox.warning(self, "Error", response.split("@")[1])
                continue

            QMessageBox.information(self, "Success", response.split("@")[1])
            # Update balance display
            self.update_account_info()
            break
        self.operationInProgress.emit(self.current_account_id, False)
        self.main_window.set_operatoin_status(self.current_account_id, False)

    def log_out(self):
        # Send log out request to backend
        self.zmqThread.sendMsg("log_out")
        time.sleep(0.1)  # Wait for backend processing
        response = self.zmqThread.receivedMessage

        if response.startswith("error@"):
            QMessageBox.warning(self, "Error", response.split("@")[1])
            return

        self.main_window.set_log_status(self.current_account_id, None)
        QMessageBox.information(self, "Success", "Logged out successfully")
        self.current_account_id = None
        self.show_initial_page()

    def update_account_info(self):
        # Send get balance request to backend
        self.zmqThread.sendMsg(f"get_balance@{self.current_account_id}")
        time.sleep(0.1)  # Wait for backend processing
        response = self.zmqThread.receivedMessage
        balance = float(response.split("@")[1])
        # Update account info label
        self.account_info_label.setText(f"Account ID: {self.current_account_id}\nBalance: ${balance:.2f}")

    def show_initial_page(self):
        # Implement your initial page UI here
        self.id_input.clear()
        self.password_input.clear()
        self.login_button.show()
        self.id_input.hide()
        self.password_input.hide()
        self.confirm_button.hide()
        self.back_button.hide()
        self.return_button.hide()
        self.query_button.hide()
        self.change_password_button.hide()
        self.transfer_money_button.hide()
        if self.account_info_label != None:
            self.account_info_label.hide()
        self.current_mode = None
        self.current_account_id = None
        self.account_info_label = None

    def back(self):
        self.show_initial_page()

    def query(self):
        if self.current_account_id:
            # Send query request to backend
            self.zmqThread.sendMsg(f"query@{self.current_account_id}")
            time.sleep(0.1)  # Wait for backend processing
            response = self.zmqThread.receivedMessage
            QMessageBox.information(self, "Transaction History", response.split("@")[1])

    def initUI(self):
        # Implement your initial UI here
        self.maxDepositAmount = 50000.00
        self.current_mode = None
        self.current_account_id = None
        self.account_info_label = None
        self.label = QLabel(f'Banking System Application: #{self.app_id}', self)
        # Subtitle(f"App Interface: #{self.app_id}")
        self.subtitle_label = QLabel('', self)
        self.login_button = QPushButton('Log In', self)
        self.login_button.clicked.connect(self.show_login_inputs)
        self.id_input = QLineEdit(self)
        self.id_input.setPlaceholderText('Account ID')
        self.id_input.hide()
        self.password_input = QLineEdit(self)
        self.password_input.setPlaceholderText('Password')
        # Hide password
        # self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.hide()
        self.confirm_button = QPushButton('Confirm', self)
        self.confirm_button.clicked.connect(self.confirm_action)
        self.confirm_button.hide()

        self.back_button = QPushButton('Back', self)
        self.back_button.clicked.connect(self.back)
        self.back_button.hide()

        self.query_button = QPushButton('Query', self)
        self.query_button.clicked.connect(self.query)
        self.query_button.hide()

        self.return_button = QPushButton('Log Out', self)
        self.change_password_button = QPushButton('Change Password', self)
        self.transfer_money_button = QPushButton('Transfer Money', self)
        self.return_button.clicked.connect(self.log_out)
        self.change_password_button.clicked.connect(self.change_password)
        self.transfer_money_button.clicked.connect(self.transfer_money)
        self.return_button.hide()
        self.change_password_button.hide()
        self.transfer_money_button.hide()

        self.layout = QVBoxLayout()
        self.layout.addWidget(self.label)
        self.layout.addWidget(self.subtitle_label)
        self.layout.addWidget(self.login_button)
        self.layout.addWidget(self.id_input)
        self.layout.addWidget(self.password_input)
        self.layout.addWidget(self.confirm_button)
        self.layout.addWidget(self.back_button)
        self.layout.addWidget(self.query_button)
        self.layout.addWidget(self.transfer_money_button)
        self.layout.addWidget(self.return_button)  # Log out
        self.layout.addWidget(self.change_password_button)
        self.setLayout(self.layout)
        # Set font
        font = QFont()
        font.setFamily("Times New Roman")
        font.setBold(True)
        font.setItalic(True)
        font.setPointSize(12)
        self.label.setFont(font)
        self.subtitle_label.setFont(font)
        self.login_button.setFont(font)
        self.confirm_button.setFont(font)
        self.return_button.setFont(font)
        self.back_button.setFont(font)
        self.change_password_button.setFont(font)
        self.transfer_money_button.setFont(font)
        self.query_button.setFont(font)
        self.setWindowTitle(f"App Interface: #{self.app_id}")
        self.setGeometry(300, 300, 600, 450)

    def show_login_inputs(self):
        self.subtitle_label.setText('Log In')
        self.id_input.show()
        self.back_button.show()
        self.password_input.show()
        self.confirm_button.show()
        self.login_button.hide()
        self.return_button.hide()
        self.change_password_button.hide()
        self.transfer_money_button.hide()
        self.query_button.hide()
        self.current_mode = 'login'  # Login mode

    def log_in_successful(self):
        self.current_account_id = self.id_input.text()  # Save the current logged-in account ID
        self.clear_and_hide_inputs()
        self.subtitle_label.setText('Main Menu')
        self.setup_main_menu_buttons()

    def setup_main_menu_buttons(self):
        self.zmqThread.sendMsg(f"get_balance@{self.current_account_id}")
        time.sleep(0.1)  # Wait for backend processing
        response = self.zmqThread.receivedMessage
        balance = float(response.split("@")[1])
        self.account_info_label = QLabel(f"Account ID: {self.current_account_id}\nBalance: ${balance:.2f}", self)
        self.account_info_label.show()
        self.account_info_label.show()
        self.layout.addWidget(self.account_info_label)
        self.return_button.show()
        self.change_password_button.show()
        self.transfer_money_button.show()
        self.query_button.show()

    def clear_and_hide_inputs(self):
        self.id_input.clear()
        self.password_input.clear()
        self.login_button.hide()
        self.id_input.hide()
        self.password_input.hide()
        self.confirm_button.hide()
        self.back_button.hide()

    def confirm_action(self):
        if self.current_mode == 'login':
            if self.log_in():
                self.log_in_successful()
    
    def closeEvent(self, event):
        self.closed.emit(self.app_id)
        if self.current_account_id is not None:
            self.main_window.set_log_status(self.current_account_id, None)
        event.accept()  # Let the window close


