from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QPushButton, QLineEdit, QVBoxLayout, QHBoxLayout, QFrame, QGridLayout, QMessageBox, QInputDialog, QLineEdit
from PyQt5.QtGui import QFont, QIntValidator
from PyQt5.QtCore import pyqtSignal, Qt
import time

class ATM(QWidget):
    password_changed = pyqtSignal(int)
    balance_changed = pyqtSignal(int)
    transfer_changed = pyqtSignal(int)

    def __init__(self, zmqThread, main_window):
        super().__init__()
        self.zmqThread = zmqThread
        self.main_window = main_window
        self.initUI()

    def create_account(self):
        account_id = self.id_input.text()
        password = self.password_input.text()

        # Send create account request to backend
        self.zmqThread.sendMsg(f"create_account@{account_id}@{password}")
        time.sleep(0.1)  # Wait for backend processing
        response = self.zmqThread.receivedMessage

        if response.startswith("error@"):
            QMessageBox.warning(self, "Error", response.split("@")[2])
            if response.split("@")[1] == 'A':  # Account error
                self.id_input.clear()
                self.password_input.clear()
            elif response.split("@")[1] == 'B':  # Password error
                self.password_input.clear()
            return False
        QMessageBox.information(self, "Success", "Account created successfully")
        return True
    
    def insert_card(self):
        account_id = self.id_input.text()
        password = self.password_input.text()

        # Send login request to backend
        self.zmqThread.sendMsg(f"insert_card@{account_id}@{password}")
        time.sleep(0.1)  # Wait for backend processing
        response = self.zmqThread.receivedMessage

        if response.startswith("error@"):
            QMessageBox.warning(self, "Error", response.split("@")[2])
            if response.split("@")[1] == 'A':  # Account error
                self.id_input.clear()
                self.password_input.clear()
            elif response.split("@")[1] == 'B':  # Password error
                self.password_input.clear()
            return False

        QMessageBox.information(self, "Success", "Insert card successfully")
        return True
    
    def insert_card_successful(self):
        self.current_account_id = self.id_input.text()  # Save the current logged-in account ID
        self.clear_and_hide_inputs()
        self.subtitle_label.setText('Main Menu')
        self.show_secondary_page()

    def show_secondary_page(self):
        self.zmqThread.sendMsg(f"get_balance@{self.current_account_id}")
        time.sleep(0.1)  # Wait for backend processing
        response = self.zmqThread.receivedMessage
        print("response",response)
        balance = float(response.split("@")[1])
        if not self.account_info_label:
            self.account_info_label = QLabel(f"Account ID: {self.current_account_id}\nBalance: ${balance:.2f}", self)
            self.layout().addWidget(self.account_info_label)
        else:
            self.account_info_label.setText(f"Account ID: {self.current_account_id}\nBalance: ${balance:.2f}")
        self.account_info_label.show()
        self.cancel_button.show()
        self.return_button.show()
        self.withdraw_button.show()
        self.deposit_button.show()
        self.change_password_button.show()
        self.transfer_money_button.show()
        self.query_button.show()

    def clear_and_hide_inputs(self):
        self.id_input.clear()
        self.password_input.clear()
        self.create_button.hide()
        self.login_button.hide()
        self.id_input.hide()
        self.password_input.hide()
        self.confirm_button.hide()
        self.back_button.hide()

    def change_password(self):
        if self.main_window.whether_processing(self.current_account_id):
            QMessageBox.warning(self, "Error", "Another operation is in progress in APP.")
            return
        while True:
            self.main_window.set_operatoin_status(self.current_account_id, True)
            new_password, ok = QInputDialog.getInt(self, "Change Password", "Enter new password (6 digits):", min=0, max=999999)
            if not ok:
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

            return_id = int(self.current_account_id)
            self.password_changed.emit(return_id)
            self.main_window.set_operatoin_status(self.current_account_id, False)
            self.return_card()
            break


    def transfer_money(self):
        if self.main_window.whether_processing(self.current_account_id):
            QMessageBox.warning(self, "Error", "Another operation is in progress in APP.")
            return
        while True:
            self.main_window.set_operatoin_status(self.current_account_id, True)
            receiver_id, ok = QInputDialog.getText(self, "Transfer Money", "Enter receiver's account ID:")
            if not ok:
                self.main_window.set_operatoin_status(self.current_account_id, False) 
                return

            amount, ok = QInputDialog.getDouble(self, "Transfer Money", "Enter amount to transfer:", decimals=2)
            if not ok:
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
            # Update account info
            return_id = int(self.current_account_id)
            self.balance_changed.emit(return_id)
            self.transfer_changed.emit(int(receiver_id))
            self.update_account_info()
            self.main_window.set_operatoin_status(self.current_account_id, False)
            break

    def return_card(self):
        # Send return card request to backend
        self.zmqThread.sendMsg("return_card")
        time.sleep(0.1)  # Wait for backend processing
        response = self.zmqThread.receivedMessage
        QMessageBox.information(self, "Success", "Card returned successfully")
        self.current_account_id = None
        self.show_initial_page()

    def deposit_cash(self):
        if self.main_window.whether_processing(self.current_account_id):
            QMessageBox.warning(self, "Error", "Another operation is in progress in APP.")
            return
        while True:
            self.main_window.set_operatoin_status(self.current_account_id, True) 
            amount, ok = QInputDialog.getDouble(self, "Deposit Cash", "Enter amount to deposit:", decimals=2)
            if not ok:
                self.main_window.set_operatoin_status(self.current_account_id, False) 
                return

            # Send deposit cash request to backend
            self.zmqThread.sendMsg(f"deposit_cash@{self.current_account_id}@{amount}")

            time.sleep(0.1)  # Wait for backend processing
            response = self.zmqThread.receivedMessage
            # print("response info", response.split("@")[0])
            # print("response info", response.split("@")[1])
            if response.startswith("error@"):
                QMessageBox.warning(self, "Error", response.split("@")[1])
                continue

            QMessageBox.information(self, "Success", response.split("@")[1])
            # Update account info
            return_id = int(self.current_account_id)
            self.balance_changed.emit(return_id)
            self.update_account_info()
            self.main_window.set_operatoin_status(self.current_account_id, False)      
            break
  

    def update_account_info(self):
        # Send get balance request to backend
        self.zmqThread.sendMsg(f"get_balance@{self.current_account_id}")
        time.sleep(0.1)  # Wait for backend processing
        response = self.zmqThread.receivedMessage
        balance = float(response.split("@")[1])
        # Update account info label
        self.account_info_label.setText(f"Account ID: {self.current_account_id}\nBalance: ${balance:.2f}")

    def withdraw_cash(self):
        if self.main_window.whether_processing(self.current_account_id):
            QMessageBox.warning(self, "Error", "Another operation is in progress in APP.")
            return
        while True:
            self.main_window.set_operatoin_status(self.current_account_id, True) 
            amount, ok = QInputDialog.getDouble(self, "Withdraw Cash", "Enter amount to withdraw:", decimals=2)
            if not ok:
                self.main_window.set_operatoin_status(self.current_account_id, False) 
                return

            # Send withdraw cash request to backend
            self.zmqThread.sendMsg(f"withdraw_cash@{self.current_account_id}@{amount}")
            time.sleep(0.1)  # Wait for backend processing
            response = self.zmqThread.receivedMessage

            if response.startswith("error@"):
                QMessageBox.warning(self, "Error", response.split("@")[1])
                continue

            QMessageBox.information(self, "Success", response.split("@")[1])
            # Update account info
            return_id = int(self.current_account_id)
            self.balance_changed.emit(return_id)
            self.update_account_info()
            self.main_window.set_operatoin_status(self.current_account_id, False)    
            break
       
    def cancel_account(self):
        if self.main_window.whether_logging_in(self.current_account_id):
            QMessageBox.warning(self, "Error", f"Account {self.current_account_id} is currently logged in from an APP. Cannot cancel account.")
            return

        reply = QMessageBox.question(self, 'Confirm', 'Are you sure you want to cancel your account?',
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

        if reply == QMessageBox.Yes:
            # Send cancel account request to backend
            self.zmqThread.sendMsg(f"cancel_account@{self.current_account_id}")
            time.sleep(0.1)  # 等待后端处理
            response = self.zmqThread.receivedMessage

            if response.startswith("error@"):
                QMessageBox.warning(self, "Error", response.split("@")[1])
                return

            QMessageBox.information(self, "Success", "Account canceled successfully")
            self.current_account_id = None  # Reset the current account ID
            self.show_initial_page()

    def show_initial_page(self):
        self.subtitle_label.setText('Init Menu') 
        self.id_input.clear()
        self.password_input.clear()
        self.create_button.show()
        self.login_button.show()
        self.id_input.hide()
        self.password_input.hide()
        self.confirm_button.hide()
        self.back_button.hide()
        self.cancel_button.hide()
        self.return_button.hide()
        self.withdraw_button.hide()
        self.deposit_button.hide()
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
            # 发送查询请求到后端
            self.zmqThread.sendMsg(f"query@{self.current_account_id}")
            time.sleep(0.1)  # 等待后端处理
            response = self.zmqThread.receivedMessage
            QMessageBox.information(self, "Transaction History", response.split("@")[1])

    def initUI(self):
        self.maxDepositAmount = 50000.00
        self.current_mode = None
        self.current_account_id = None
        self.account_info_label = None

        # Main label
        self.label = QLabel('Banking System ATM', self)
        self.subtitle_label = QLabel('Init Menu', self)

        self.create_button = QPushButton('Create Account', self)
        self.create_button.clicked.connect(self.show_create_inputs)

        self.login_button = QPushButton('Log In', self)
        self.login_button.clicked.connect(self.show_login_inputs)

        self.id_input = QLineEdit(self)
        self.id_input.setPlaceholderText('Account ID')
        validator = QIntValidator(0, 9999999999, self)  # Allows only 10 digit numbers
        self.id_input.setValidator(validator)
        self.id_input.hide()

        self.password_input = QLineEdit(self)
        self.password_input.setPlaceholderText('Password')
        self.password_input.setEchoMode(QLineEdit.Password)
        validator = QIntValidator(0, 999999, self)  # Allows only 6 digit numbers
        self.password_input.setValidator(validator)
        self.password_input.hide()

        # Confirm and Back buttons
        self.confirm_button = QPushButton('Confirm', self)
        self.confirm_button.clicked.connect(self.confirm_action)
        self.confirm_button.hide()

        self.back_button = QPushButton('Back', self)
        self.back_button.clicked.connect(self.back)
        self.back_button.hide()

        # Secondary action buttons
        self.query_button = QPushButton('Query', self)
        self.query_button.clicked.connect(self.query)
        self.query_button.hide()

        self.cancel_button = QPushButton('Cancel Account', self)
        self.cancel_button.clicked.connect(self.cancel_account)
        self.cancel_button.hide()

        self.return_button = QPushButton('Return Card', self)
        self.return_button.clicked.connect(self.return_card)
        self.return_button.hide()

        self.withdraw_button = QPushButton('Withdraw Cash', self)
        self.withdraw_button.clicked.connect(self.withdraw_cash)
        self.withdraw_button.hide()

        self.deposit_button = QPushButton('Deposit Cash', self)
        self.deposit_button.clicked.connect(self.deposit_cash)
        self.deposit_button.hide()

        self.change_password_button = QPushButton('Change Password', self)
        self.change_password_button.clicked.connect(self.change_password)
        self.change_password_button.hide()

        self.transfer_money_button = QPushButton('Transfer Money', self)
        self.transfer_money_button.clicked.connect(self.transfer_money)
        self.transfer_money_button.hide()

        # Set font
        font = QFont()
        font.setFamily("Times New Roman")
        font.setBold(True)
        font.setItalic(True)
        font.setPointSize(12)
        self.label.setFont(font)
        self.subtitle_label.setFont(font)
        self.create_button.setFont(font)
        self.login_button.setFont(font)
        self.confirm_button.setFont(font)
        self.cancel_button.setFont(font)
        self.return_button.setFont(font)
        self.back_button.setFont(font)
        self.withdraw_button.setFont(font)
        self.deposit_button.setFont(font)
        self.change_password_button.setFont(font)
        self.transfer_money_button.setFont(font)
        self.query_button.setFont(font)

        # Main layout
        main_layout = QVBoxLayout() 
         # Title section
        title_layout = QVBoxLayout()
        title_layout.addWidget(self.label, alignment=Qt.AlignCenter)
        title_layout.addWidget(self.subtitle_label, alignment=Qt.AlignCenter)   
        
        title_frame = QFrame(self)
        title_frame.setLayout(title_layout)
        title_frame.setFrameShape(QFrame.Box)
        title_frame.setFrameShadow(QFrame.Sunken)   

        # Buttons section
        buttons_layout = QVBoxLayout()
        buttons_layout.addWidget(self.create_button, alignment=Qt.AlignCenter)
        buttons_layout.addWidget(self.login_button, alignment=Qt.AlignCenter)
        buttons_layout.addWidget(self.id_input, alignment=Qt.AlignCenter)
        buttons_layout.addWidget(self.password_input, alignment=Qt.AlignCenter)
        buttons_layout.addWidget(self.confirm_button, alignment=Qt.AlignCenter)
        buttons_layout.addWidget(self.back_button, alignment=Qt.AlignCenter)
        buttons_layout.addWidget(self.query_button, alignment=Qt.AlignCenter)
        buttons_layout.addWidget(self.deposit_button, alignment=Qt.AlignCenter)   
        buttons_layout.addWidget(self.withdraw_button, alignment=Qt.AlignCenter) 
        buttons_layout.addWidget(self.transfer_money_button, alignment=Qt.AlignCenter)
        buttons_layout.addWidget(self.change_password_button, alignment=Qt.AlignCenter) 
        buttons_layout.addWidget(self.cancel_button, alignment=Qt.AlignCenter)    
        buttons_layout.addWidget(self.return_button, alignment=Qt.AlignCenter)
        buttons_frame = QFrame(self)
        buttons_frame.setLayout(buttons_layout)
        buttons_frame.setFrameShape(QFrame.Box)
        buttons_frame.setFrameShadow(QFrame.Sunken) 
        main_layout.addWidget(title_frame)
        main_layout.addWidget(buttons_frame)
        self.setLayout(main_layout)
        self.setWindowTitle('ATM Interface')
        self.setGeometry(300, 300, 600, 450)

    def show_create_inputs(self):
        self.subtitle_label.setText('Create Account')
        self.id_input.show()
        self.password_input.show()
        self.confirm_button.show()
        self.back_button.show()
        self.create_button.hide()
        self.login_button.hide()
        self.cancel_button.hide()
        self.return_button.hide()
        self.withdraw_button.hide()
        self.deposit_button.hide()
        self.change_password_button.hide()
        self.transfer_money_button.hide()
        self.query_button.hide()
        self.current_mode = 'create'  # Create mode

    def show_login_inputs(self):
        self.subtitle_label.setText('Log In')
        self.id_input.show()
        self.back_button.show()
        self.password_input.show()
        self.confirm_button.show()
        self.create_button.hide()
        self.login_button.hide()
        self.cancel_button.hide()
        self.return_button.hide()
        self.withdraw_button.hide()
        self.deposit_button.hide()
        self.change_password_button.hide()
        self.transfer_money_button.hide()
        self.query_button.hide()
        self.current_mode = 'login'  # Login mode

    def confirm_action(self):
        if self.current_mode == 'create':
            if self.create_account():
                self.insert_card_successful()
        elif self.current_mode == 'login':
            if self.insert_card():
                self.insert_card_successful()
