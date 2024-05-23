import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QLabel, QLineEdit, QMessageBox, QInputDialog
import sqlite3
# from bank import initialize_database
from PyQt5.QtGui import QFont
import time
import NetClient
class ATM(QWidget):
    def __init__(self, zmqThread):
        super().__init__()
        self.zmqThread = zmqThread
        self.initUI()
        # self.initConnection()

    # def initConnection(self):
    #     self.conn = sqlite3.connect('bank.db')
    #     self.cursor = self.conn.cursor()
    #     initialize_database()

    def create_account(self):
        account_id = self.id_input.text()
        password = self.password_input.text()

        # 发送创建账户请求到后端
        self.zmqThread.sendMsg(f"create_account@{account_id}@{password}")
        time.sleep(0.1)  # 等待后端处理
        response = self.zmqThread.receivedMessage

        if response.startswith("error@"):
            QMessageBox.warning(self, "Error", response.split("@")[2])
            if response.split("@")[1] == 'A': ## account error
                self.id_input.clear()
                self.password_input.clear()
            elif response.split("@")[1] == 'B': ## password error
                self.password_input.clear()
            return False
        QMessageBox.information(self, "Success", "Account created successfully")
        return True
    
    def log_in(self):
        account_id = self.id_input.text()
        password = self.password_input.text()

        # 发送登录请求到后端
        self.zmqThread.sendMsg(f"log_in@{account_id}@{password}")
        time.sleep(0.1)  # 等待后端处理
        response = self.zmqThread.receivedMessage

        if response.startswith("error@"):
            QMessageBox.warning(self, "Error", response.split("@")[2])
            if response.split("@")[1] == 'A': ## account error
                self.id_input.clear()
                self.password_input.clear()
            elif response.split("@")[1] == 'B': ## password error
                self.password_input.clear()
            return False

        QMessageBox.information(self, "Success", "Log in successful")
        return True
    
    def log_in_successful(self):
        self.current_account_id = self.id_input.text()  # Save the current logged-in account ID
        self.clear_and_hide_inputs()
        self.subtitle_label.setText('Main Menu')
        self.setup_main_menu_buttons()

    def setup_main_menu_buttons(self):
        self.zmqThread.sendMsg(f"get_balance@{self.current_account_id}")
        time.sleep(0.1)  # 等待后端处理
        response = self.zmqThread.receivedMessage
        balance = float(response.split("@")[1])
        self.account_info_label = QLabel(f"Account ID: {self.current_account_id}\nBalance: ${balance:.2f}", self)
        self.account_info_label.show()
        # Get the current account balance
        # self.cursor.execute("SELECT balance FROM accounts WHERE id = ?", (self.current_account_id,))
        # balance = self.cursor.fetchone()[0]
        # self.account_info_label = QLabel(f"Account ID: {self.current_account_id}\nBalance: ${balance:.2f}", self)
        # self.account_info_label = QLabel(f"Account ID: {self.current_account_id}", self)
        self.account_info_label.show()
        self.layout.addWidget(self.account_info_label)
        self.close_button.show()
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
        while True:
            new_password, ok = QInputDialog.getText(self, "Change Password", "Enter new password:")
            if not ok:
                return
            # 发送修改密码请求到后端
            self.zmqThread.sendMsg(f"change_password@{self.current_account_id}@{new_password}")
            time.sleep(0.1)  # 等待后端处理
            response = self.zmqThread.receivedMessage

            if response.startswith("error@"):
                QMessageBox.warning(self, "Error", response.split("@")[1])
                continue

            QMessageBox.information(self, "Success", "Password changed successfully")
            self.show_initial_page()
            break

    def transfer_money(self):
        while True:
            receiver_id, ok = QInputDialog.getText(self, "Transfer Money", "Enter receiver's account ID:")
            if not ok:
                return

            amount, ok = QInputDialog.getDouble(self, "Transfer Money", "Enter amount to transfer:", decimals=2)
            if not ok:
                return

            # 发送转账请求到后端
            self.zmqThread.sendMsg(f"transfer_money@{self.current_account_id}@{receiver_id}@{amount}")
            time.sleep(0.1)  # 等待后端处理
            response = self.zmqThread.receivedMessage

            if response.startswith("error@"):
                QMessageBox.warning(self, "Error", response.split("@")[1])
                continue

            QMessageBox.information(self, "Success", response.split("@")[1])
            # 更新余额显示
            self.update_account_info()
            break

    def return_card(self):
        # 发送退卡请求到后端
        self.zmqThread.sendMsg("return_card")
        time.sleep(0.1)  # 等待后端处理
        response = self.zmqThread.receivedMessage

        if response.startswith("error@"):
            QMessageBox.warning(self, "Error", response.split("@")[1])
            return

        QMessageBox.information(self, "Success", "Card returned successfully")
        self.current_account_id = None
        self.show_initial_page()

    def deposit_cash(self):
        while True:
            amount, ok = QInputDialog.getDouble(self, "Deposit Cash", "Enter amount to deposit:", decimals=2)
            if not ok:
                return

            # 发送存款请求到后端
            self.zmqThread.sendMsg(f"deposit_cash@{self.current_account_id}@{amount}")

            time.sleep(0.1)  # 等待后端处理
            response = self.zmqThread.receivedMessage
            # print("response info", response.split("@")[0])
            # print("response info", response.split("@")[1])
            if response.startswith("error@"):
                QMessageBox.warning(self, "Error", response.split("@")[1])
                continue

            QMessageBox.information(self, "Success", response.split("@")[1])
            # 更新余额显示
            self.update_account_info()
            break

    def update_account_info(self):
        # 发送关闭账户请求到后端
        self.zmqThread.sendMsg(f"get_balance@{self.current_account_id}")
        time.sleep(0.1)  # 等待后端处理
        response = self.zmqThread.receivedMessage

        balance = float(response.split("@")[1])
        # Update account info label
        self.account_info_label.setText(f"Account ID: {self.current_account_id}\nBalance: ${balance:.2f}")

    def withdraw_cash(self):
        while True:
            amount, ok = QInputDialog.getDouble(self, "Withdraw Cash", "Enter amount to withdraw:", decimals=2)
            if not ok:
                return

            # 发送取款请求到后端
            self.zmqThread.sendMsg(f"withdraw_cash@{self.current_account_id}@{amount}")
            time.sleep(0.1)  # 等待后端处理
            response = self.zmqThread.receivedMessage

            if response.startswith("error@"):
                QMessageBox.warning(self, "Error", response.split("@")[1])
                continue

            QMessageBox.information(self, "Success", response.split("@")[1])
            # 更新余额显示
            self.update_account_info()
            break

    def close_account(self):
        reply = QMessageBox.question(self, 'Confirm', 'Are you sure you want to close your account?',
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

        if reply == QMessageBox.Yes:
            # 发送关闭账户请求到后端
            self.zmqThread.sendMsg(f"close_account@{self.current_account_id}")
            time.sleep(0.1)  # 等待后端处理
            response = self.zmqThread.receivedMessage

            if response.startswith("error@"):
                QMessageBox.warning(self, "Error", response.split("@")[1])
                return

            QMessageBox.information(self, "Success", "Account closed successfully")
            self.current_account_id = None  # Reset the current account ID
            self.show_initial_page()

    def show_initial_page(self):
        self.id_input.clear()
        self.password_input.clear()
        self.create_button.show()
        self.login_button.show()
        self.id_input.hide()
        self.password_input.hide()
        self.confirm_button.hide()
        self.back_button.hide()
        self.close_button.hide()
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
        self.label = QLabel('Banking System', self)
        # Subtitle
        self.subtitle_label = QLabel('', self)
        self.create_button = QPushButton('Create Account', self)
        self.create_button.clicked.connect(self.show_create_inputs)

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

        self.close_button = QPushButton('Close Account', self)
        self.return_button = QPushButton('Return Card', self)
        self.withdraw_button = QPushButton('Withdraw Cash', self)
        self.deposit_button = QPushButton('Deposit Cash', self)
        self.change_password_button = QPushButton('Change Password', self)
        self.transfer_money_button = QPushButton('Transfer Money', self)

        self.close_button.clicked.connect(self.close_account)
        self.return_button.clicked.connect(self.return_card)
        self.withdraw_button.clicked.connect(self.withdraw_cash)
        self.deposit_button.clicked.connect(self.deposit_cash)
        self.change_password_button.clicked.connect(self.change_password)
        self.transfer_money_button.clicked.connect(self.transfer_money)

        self.close_button.hide()
        self.return_button.hide()
        self.withdraw_button.hide()
        self.deposit_button.hide()
        self.change_password_button.hide()
        self.transfer_money_button.hide()

        self.layout = QVBoxLayout()
        self.layout.addWidget(self.label)
        self.layout.addWidget(self.subtitle_label)
        self.layout.addWidget(self.create_button)
        self.layout.addWidget(self.login_button)
        self.layout.addWidget(self.id_input)
        self.layout.addWidget(self.password_input)
        self.layout.addWidget(self.confirm_button)
        self.layout.addWidget(self.back_button)
        self.layout.addWidget(self.query_button)
        self.layout.addWidget(self.deposit_button)
        self.layout.addWidget(self.withdraw_button)
        self.layout.addWidget(self.transfer_money_button)
        self.layout.addWidget(self.return_button)  # Log out
        self.layout.addWidget(self.change_password_button)
        self.layout.addWidget(self.close_button)  # Delete

        self.setLayout(self.layout)

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
        self.close_button.setFont(font)
        self.return_button.setFont(font)
        self.back_button.setFont(font)
        self.withdraw_button.setFont(font)
        self.deposit_button.setFont(font)
        self.change_password_button.setFont(font)
        self.transfer_money_button.setFont(font)
        self.query_button.setFont(font)
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
        self.close_button.hide()
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
        self.close_button.hide()
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
                self.log_in_successful()
        elif self.current_mode == 'login':
            if self.log_in():
                self.log_in_successful()

if __name__ == '__main__':
    identity = "Team15" #write your team name here.
    zmqThread = NetClient.ZmqClientThread(identity=identity)
    app = QApplication(sys.argv)
    ex = ATM(zmqThread)
    ex.show()
    sys.exit(app.exec_())
