import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QLabel, QLineEdit, QMessageBox, QInputDialog
import sqlite3
from bank import initialize_database
from PyQt5.QtGui import QFont

class ATM(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.initConnection()

    def initConnection(self):
        self.conn = sqlite3.connect('bank.db')
        self.cursor = self.conn.cursor()
        initialize_database()

    def create_account(self):
        account_id = self.id_input.text()
        password = self.password_input.text()

        if not account_id.isdigit() or len(account_id) != 10:
            QMessageBox.warning(self, "Error", "Account ID must consist of 10 digits")
            self.id_input.clear()
            self.password_input.clear()
            return False

        self.cursor.execute("SELECT * FROM accounts WHERE id = ?", (account_id,))
        existing_account = self.cursor.fetchone()
        if existing_account:
            QMessageBox.warning(self, "Error", "Account already exists")
            self.id_input.clear()
            self.password_input.clear()
            return False

        if not (len(password) >= 8 and any(c.isupper() for c in password) and any(c.islower() for c in password) and any(c.isdigit() for c in password)):
            QMessageBox.warning(self, "Error", "Password must be at least 8 characters long and include uppercase letters, lowercase letters, and numbers")
            self.password_input.clear()
            return False

        self.cursor.execute("INSERT INTO accounts (id, password, balance) VALUES (?, ?, 0)", (account_id, password))
        self.conn.commit()

        QMessageBox.information(self, "Success", "Account created successfully")
        return True

    def login(self):
        account_id = self.id_input.text()
        password = self.password_input.text()

        if not account_id or not password:
            QMessageBox.warning(self, "Error", "Please enter account ID and password")
            return False

        self.cursor.execute("SELECT * FROM accounts WHERE id = ?", (account_id,))
        account = self.cursor.fetchone()
        if not account:
            QMessageBox.warning(self, "Error", "Invalid account ID")
            self.id_input.clear()
            self.password_input.clear()
            return False

        if account[1] != password:
            QMessageBox.warning(self, "Error", "Invalid password")
            self.password_input.clear()
            return False

        QMessageBox.information(self, "Success", "Login successful")
        return True

    def login_successful(self):
        self.current_account_id = self.id_input.text()  # Save the current logged-in account ID
        self.clear_and_hide_inputs()
        self.subtitle_label.setText('Main Menu')
        self.setup_main_menu_buttons()

    def setup_main_menu_buttons(self):
        # Get the current account balance
        self.cursor.execute("SELECT balance FROM accounts WHERE id = ?", (self.current_account_id,))
        balance = self.cursor.fetchone()[0]
        self.account_info_label = QLabel(f"Account ID: {self.current_account_id}\nBalance: ${balance:.2f}", self)
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
            if not (len(new_password) >= 8 and any(c.isupper() for c in new_password) and any(c.islower() for c in new_password) and any(c.isdigit() for c in new_password)):
                QMessageBox.warning(self, "Error", "Password must be at least 8 characters long and include uppercase letters, lowercase letters, and numbers")
                continue

            self.cursor.execute("SELECT password FROM accounts WHERE id = ?", (self.current_account_id,))
            old_password = self.cursor.fetchone()[0]

            if new_password == old_password:
                QMessageBox.warning(self, "Error", "New password cannot be the same as the old password")
                continue

            self.cursor.execute("UPDATE accounts SET password = ? WHERE id = ?", (new_password, self.current_account_id))
            self.conn.commit()
            QMessageBox.information(self, "Success", "Password changed successfully")
            self.show_initial_page()
            break

    def transfer_money(self):
        while True:
            receiver_id, ok = QInputDialog.getText(self, "Transfer Money", "Enter receiver's account ID:")
            if not ok:
                return
            if not receiver_id.isdigit() or len(receiver_id) != 10:
                QMessageBox.warning(self, "Error", "Receiver's account ID must consist of 10 digits")
                continue

            # Check if the receiver's account exists
            self.cursor.execute("SELECT * FROM accounts WHERE id = ?", (receiver_id,))
            receiver_account = self.cursor.fetchone()
            if not receiver_account:
                QMessageBox.warning(self, "Error", "Receiver's account does not exist")
                continue

            amount, ok = QInputDialog.getDouble(self, "Transfer Money", "Enter amount to transfer:", decimals=2)
            if not ok:
                return
            if not (0.01 <= amount <= self.maxDepositAmount):
                QMessageBox.warning(self, "Error", "Transfer amount must be between $0.01 and $50000.00")
                continue

            # Get the current account balance
            self.cursor.execute("SELECT balance FROM accounts WHERE id = ?", (self.current_account_id,))
            balance = self.cursor.fetchone()[0]

            if amount > balance:
                QMessageBox.warning(self, "Error", "Insufficient account balance for transfer")
                continue

            # Get the receiver's account balance
            receiver_balance = receiver_account[2]  # Assume balance is in the 3rd column (index 2)

            sender_starting_balance = balance
            sender_ending_balance = balance - amount
            receiver_starting_balance = receiver_balance
            receiver_ending_balance = receiver_balance + amount

            # Update the database
            self.cursor.execute("UPDATE accounts SET balance = ? WHERE id = ?", (sender_ending_balance, self.current_account_id))
            self.cursor.execute("UPDATE accounts SET balance = ? WHERE id = ?", (receiver_ending_balance, receiver_id))

            # Insert transaction records
            self.cursor.execute("INSERT INTO transactions (account_id, type, amount, starting_balance, ending_balance) VALUES (?, 'transfer_out', ?, ?, ?)",
                                (self.current_account_id, amount, sender_starting_balance, sender_ending_balance))
            self.cursor.execute("INSERT INTO transactions (account_id, type, amount, starting_balance, ending_balance) VALUES (?, 'transfer_in', ?, ?, ?)",
                                (receiver_id, amount, receiver_starting_balance, receiver_ending_balance))
            self.conn.commit()

            QMessageBox.information(self, "Success", f"${amount:.2f} transferred successfully")
            # Update balance display
            self.update_account_info()
            break

    def return_card(self):
        # Exit account
        QMessageBox.information(self, "Success", "Card returned successfully")
        self.current_account_id = None
        self.show_initial_page()

    def deposit_cash(self):
        while True:
            amount, ok = QInputDialog.getDouble(self, "Deposit Cash", "Enter amount to deposit:", decimals=2)
            if not ok:
                return

            if 0.01 <= amount <= self.maxDepositAmount:
                self.cursor.execute("SELECT balance FROM accounts WHERE id = ?", (self.current_account_id,))
                starting_balance = self.cursor.fetchone()[0]
                ending_balance = starting_balance + amount

                self.cursor.execute("UPDATE accounts SET balance = ? WHERE id = ?", (ending_balance, self.current_account_id))
                self.cursor.execute("INSERT INTO transactions (account_id, type, amount, starting_balance, ending_balance) VALUES (?, 'deposit', ?, ?, ?)",
                                    (self.current_account_id, amount, starting_balance, ending_balance))
                self.conn.commit()
                QMessageBox.information(self, "Success", f"${amount:.2f} deposited successfully")
                # Update balance display
                self.update_account_info()
                break
            else:
                QMessageBox.warning(self, "Error", "Deposit amount must be between $0.01 and $50000.00")

    def update_account_info(self):
        # Get the current account balance
        self.cursor.execute("SELECT balance FROM accounts WHERE id = ?", (self.current_account_id,))
        balance = self.cursor.fetchone()[0]
        # Update account info label
        self.account_info_label.setText(f"Account ID: {self.current_account_id}\nBalance: ${balance:.2f}")

    def withdraw_cash(self):
        while True:
            amount, ok = QInputDialog.getDouble(self, "Withdraw Cash", "Enter amount to withdraw:", decimals=2)
            if not ok:
                return
            # Get the current account balance
            self.cursor.execute("SELECT balance FROM accounts WHERE id = ?", (self.current_account_id,))
            balance = self.cursor.fetchone()[0]

            if amount > balance:
                QMessageBox.warning(self, "Error", "Insufficient account balance for withdrawal")
                continue

            if 0.01 <= amount <= self.maxDepositAmount:
                starting_balance = balance
                ending_balance = balance - amount
                self.cursor.execute("UPDATE accounts SET balance = ? WHERE id = ?", (ending_balance, self.current_account_id))
                self.cursor.execute("INSERT INTO transactions (account_id, type, amount, starting_balance, ending_balance) VALUES (?, 'withdraw', ?, ?, ?)",
                                    (self.current_account_id, amount, starting_balance, ending_balance))
                self.conn.commit()
                QMessageBox.information(self, "Success", f"${amount:.2f} withdrawn successfully")
                # Update balance display
                self.update_account_info()
                break
            else:
                QMessageBox.warning(self, "Error", "Withdrawal amount must be between $0.01 and $50000.00")

    def close_account(self):
        # Get the current account balance
        self.cursor.execute("SELECT balance FROM accounts WHERE id = ?", (self.current_account_id,))
        balance = self.cursor.fetchone()[0]

        if balance != 0:
            QMessageBox.warning(self, "Error", "Account balance must be zero to close the account")
            return

        reply = QMessageBox.question(self, 'Confirm', 'Are you sure you want to close your account?',
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

        if reply == QMessageBox.Yes:
            self.cursor.execute("DELETE FROM accounts WHERE id = ?", (self.current_account_id,))
            self.conn.commit()
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
            self.cursor.execute("SELECT password, balance FROM accounts WHERE id = ?", (self.current_account_id,))
            account_info = self.cursor.fetchone()
            password = account_info[0]
            balance = account_info[1]

            transactions_text = f"Password: {password}\nBalance: ${balance:.2f}\n\nTransactions:\n"
            self.cursor.execute("SELECT type, amount, date, starting_balance, ending_balance FROM transactions WHERE account_id = ?", (self.current_account_id,))
            transactions = self.cursor.fetchall()
            for transaction in transactions:
                transactions_text += (f"{transaction[2]} - {transaction[0]}: ${transaction[1]:.2f} "
                                    f"(Starting Balance: ${transaction[3]:.2f}, Ending Balance: ${transaction[4]:.2f})\n")
                    
            QMessageBox.information(self, "Transaction History", transactions_text)
        else:
            QMessageBox.warning(self, "Error", "No account logged in!")

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
                self.login_successful()
        elif self.current_mode == 'login':
            if self.login():
                self.login_successful()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = ATM()
    ex.show()
    sys.exit(app.exec_())
