from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QPushButton, QLineEdit, QVBoxLayout, QHBoxLayout, QFrame, QGridLayout, QMessageBox, QInputDialog
from PyQt5.QtGui import QCloseEvent, QFont, QIntValidator,QRegularExpressionValidator
import time
from PyQt5.QtCore import pyqtSignal, Qt,QRegularExpression

class APP(QWidget):
    # This is a front end communication signal
    closed = pyqtSignal(int)
    operationInProgress = pyqtSignal(int, bool)
    password_changed = pyqtSignal(int)
    balance_changed = pyqtSignal(int)
    transfer_changed = pyqtSignal(int)
    def __init__(self, zmqThread, app_id, main_window):
        super().__init__()
        self.zmqThread = zmqThread
        self.app_id = app_id
        self.main_window = main_window
        self.logged_in = False
        self.initUI()
        self.create_test_dict()

    def log_in(self):
        account_id = self.id_input.text()
        password = self.password_input.text()

        # Send login request to backend
        self.zmqThread.sendMsg(f"log_in@{account_id}@{password}#{self.app_id}")
        time.sleep(0.1)  # Wait for backend processing
        response = self.zmqThread.receivedMessage

        if response.startswith("failed@"):
            QMessageBox.warning(self, "failed", response.split("@")[2])
            if response.split("@")[1] == 'A': ## account failed
                self.id_input.clear()
                self.password_input.clear()
            elif response.split("@")[1] == 'B': ## password failed
                self.password_input.clear()
            return False
        
        self.main_window.whether_logging_in(account_id)
        self.main_window.set_log_status(self, account_id, self.app_id)
        self.logged_in = True
        QMessageBox.information(self, "Success", "Log in successfully")
        return True
    
    def change_password(self):
        if self.main_window.whether_processing(self.current_account_id):
            QMessageBox.warning(self, "failed", "Another operation is in progress in ATM.")
            return
        while True:
            self.operationInProgress.emit(self.current_account_id, True)
            self.main_window.set_operatoin_status(self.current_account_id, True)
            self.test_dict["d_dialog"] = QInputDialog(self)
            new_password, ok = self.test_dict["d_dialog"].getText(self, "Change Password", "Enter new password (6 digits):")
            if not ok:
                self.operationInProgress.emit(self.current_account_id, False)
                self.main_window.set_operatoin_status(self.current_account_id, False)
                return
            
            # Send change password request to backend
            self.zmqThread.sendMsg(f"change_password@{self.current_account_id}@{new_password}(#{self.app_id})")
            time.sleep(0.1)  # Wait for backend processing
            response = self.zmqThread.receivedMessage

            if response.startswith("failed@"):
                QMessageBox.warning(self, "failed", response.split("@")[1])
                continue

            QMessageBox.information(self, "Success", "Password changed successfully")
            return_id = int(self.current_account_id)
            self.password_changed.emit(return_id)
            self.operationInProgress.emit(self.current_account_id, False)
            self.main_window.set_operatoin_status(self.current_account_id, False)
            self.log_out()
            break

    def transfer_money(self):
        if self.main_window.whether_processing(self.current_account_id):
            QMessageBox.warning(self, "failed", "Another operation is in progress in ATM.")
            return
        while True:
            self.operationInProgress.emit(self.current_account_id, True)
            self.main_window.set_operatoin_status(self.current_account_id, True)
            self.test_dict["d_dialog"] = QInputDialog(self)
            receiver_id, ok = self.test_dict["d_dialog"].getText(self, "Transfer Money", "Enter receiver's account ID:")
            if not ok:
                self.operationInProgress.emit(self.current_account_id, False)
                self.main_window.set_operatoin_status(self.current_account_id, False)
                return
            self.test_dict["d_dialog"] = QInputDialog(self)
            amount, ok = self.test_dict["d_dialog"].getDouble(self, "Transfer Money", "Enter amount to transfer:", decimals=2)
            if not ok:
                self.operationInProgress.emit(self.current_account_id, False)
                self.main_window.set_operatoin_status(self.current_account_id, False)
                return

            # Send transfer money request to backend
            self.zmqThread.sendMsg(f"transfer_money@{self.current_account_id}@{receiver_id}@{amount}(#{self.app_id})")
            time.sleep(0.1)  # Wait for backend processing
            response = self.zmqThread.receivedMessage
            if response.startswith("failed@"):
                QMessageBox.warning(self, "failed", response.split("@")[1])
                continue

            QMessageBox.information(self, "Success", response.split("@")[1])
            # Update balance display
            return_id = int(self.current_account_id)
            self.balance_changed.emit(return_id)
            self.operationInProgress.emit(self.current_account_id, False)
            self.transfer_changed.emit(int(receiver_id))
            self.update_account_info()
            self.main_window.set_operatoin_status(self.current_account_id, False)
            break

    def log_out(self):
        # Send log out request to backend
        self.zmqThread.sendMsg(f"log_out#{self.app_id}")
        time.sleep(0.1)  # Wait for backend processing
        response = self.zmqThread.receivedMessage
        self.main_window.set_log_status(self, self.current_account_id, None)
        QMessageBox.information(self, "Success", "Logged out successfully")
        self.current_account_id = None
        self.logged_in = False
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
        self.subtitle_label.setText('Init Menu') 
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
            self.zmqThread.sendMsg(f"query@{self.current_account_id}(#{self.app_id})")
            time.sleep(0.1)  # Wait for backend processing
            response = self.zmqThread.receivedMessage
            QMessageBox.information(self, "Transaction History", response.split("@")[1])

    def initUI(self):
        self.maxDepositAmount = 50000.00
        self.current_mode = None
        self.current_account_id = None
        self.account_info_label = None

        self.label = QLabel(f'Banking System Application: #{self.app_id}', self)
        self.subtitle_label = QLabel('Init Menu', self)

        self.login_button = QPushButton('Log In', self)
        self.login_button.clicked.connect(self.show_login_inputs)

        self.id_input = QLineEdit(self)
        self.id_input.setPlaceholderText('Account ID')
        # validator = QIntValidator(0, 9999999999, self)  # Allows only 10 digit numbers
        reg_exp = QRegularExpression(r'^\d{1,10}$')  # Allows only up to 10 digit numbers
        validator = QRegularExpressionValidator(reg_exp, self.id_input)
        self.id_input.setValidator(validator)
        self.id_input.hide()

        self.password_input = QLineEdit(self)
        self.password_input.setPlaceholderText('Password')
        self.password_input.setEchoMode(QLineEdit.Password)
        reg_exp = QRegularExpression(r'^\d{1,6}$')  # Allows only up to 6 digit numbers
        validator = QRegularExpressionValidator(reg_exp, self.password_input)
        self.password_input.setValidator(validator)
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

        self.close_button = QPushButton('Close', self)
        self.close_button.clicked.connect(self.close_action)

        self.return_button = QPushButton('Log Out', self)
        self.change_password_button = QPushButton('Change Password', self)
        self.transfer_money_button = QPushButton('Transfer Money', self)
        self.return_button.clicked.connect(self.log_out)
        self.change_password_button.clicked.connect(self.change_password)
        self.transfer_money_button.clicked.connect(self.transfer_money)
        self.return_button.hide()
        self.change_password_button.hide()
        self.transfer_money_button.hide()

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
        self.close_button.setFont(font)
        # Main layout
        main_layout = QVBoxLayout()
        
        # Title section
        title_layout = QVBoxLayout()
        title_layout.addWidget(self.label, alignment=Qt.AlignCenter)
        title_layout.addWidget(self.subtitle_label, alignment=Qt.AlignCenter)
        title_layout.addWidget(self.close_button, alignment=Qt.AlignCenter)
        title_frame = QFrame(self)
        title_frame.setLayout(title_layout)
        title_frame.setFrameShape(QFrame.Box)
        title_frame.setFrameShadow(QFrame.Sunken)

        # Buttons section
        buttons_layout = QVBoxLayout()
        buttons_layout.addWidget(self.login_button, alignment=Qt.AlignCenter)
        buttons_layout.addWidget(self.id_input, alignment=Qt.AlignCenter)
        buttons_layout.addWidget(self.password_input, alignment=Qt.AlignCenter)
        buttons_layout.addWidget(self.confirm_button, alignment=Qt.AlignCenter)
        buttons_layout.addWidget(self.back_button, alignment=Qt.AlignCenter)
        buttons_layout.addWidget(self.query_button, alignment=Qt.AlignCenter)
        buttons_layout.addWidget(self.transfer_money_button, alignment=Qt.AlignCenter)
        buttons_layout.addWidget(self.change_password_button, alignment=Qt.AlignCenter)
        buttons_layout.addWidget(self.return_button, alignment=Qt.AlignCenter)
        buttons_frame = QFrame(self)
        buttons_frame.setLayout(buttons_layout)
        buttons_frame.setFrameShape(QFrame.Box)
        buttons_frame.setFrameShadow(QFrame.Sunken)

        main_layout.addWidget(title_frame)
        main_layout.addWidget(buttons_frame)

        self.setLayout(main_layout)
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
        self.show_secondary_page()

    def show_secondary_page(self):
        self.zmqThread.sendMsg(f"get_balance@{self.current_account_id}")
        time.sleep(0.1)  # Wait for backend processing
        response = self.zmqThread.receivedMessage
        balance = float(response.split("@")[1])
        if not self.account_info_label:
            self.account_info_label = QLabel(f"Account ID: {self.current_account_id}\nBalance: ${balance:.2f}", self)
            self.layout().addWidget(self.account_info_label)
        else:
            self.account_info_label.setText(f"Account ID: {self.current_account_id}\nBalance: ${balance:.2f}")
        self.account_info_label.show()
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
    
    # def closeEvent(self, event):
    #     self.closed.emit(self.app_id)
    #     if self.current_account_id is not None:
    #         self.main_window.set_log_status(self, self.current_account_id, None)
    #     event.accept()  # Let the window close

    def close_action(self):
        if self.logged_in:
            QMessageBox.warning(self, "Warning", "Please log out before closing the app.")
            return
        self.main_window.set_log_status(self, self.current_account_id, None)
        self.closed.emit(self.app_id)
        self.close()

    def create_test_dict(self):

        self.test_dict={
            "l_label":self.label,
            "l_subtitle":self.subtitle_label,
            "l_account":self.account_info_label,
            "b_login":self.login_button,
            "i_id":self.id_input,
            "i_password":self.password_input,
            "b_confirm":self.confirm_button,
            "b_back":self.back_button,
            "b_query":self.query_button,
            "b_return":self.return_button,
            "b_change_password":self.change_password_button,
            "b_transfer":self.transfer_money_button,
            "b_close":self.close_button,
            "d_dialog": None
        }