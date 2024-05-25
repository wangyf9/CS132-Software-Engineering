from PyQt5.QtWidgets import QMainWindow, QPushButton, QMessageBox, QInputDialog, QApplication
from PyQt5.QtCore import pyqtSignal
import sys
import APP_UI
import NetClient
import ATM_UI
import sqlite3

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

    def initUI(self):
        openAppButton = QPushButton('Open App', self)
        openAppButton.clicked.connect(self.open_app)
        openAppButton.setGeometry(50, 50, 200, 50)

        closeAppButton = QPushButton('Close App', self)
        closeAppButton.clicked.connect(self.close_app)
        closeAppButton.setGeometry(50, 150, 200, 50)

        resetButton = QPushButton('Reset System Database', self)
        resetButton.clicked.connect(self.reset)
        resetButton.setGeometry(50, 250, 200, 50)

        self.setWindowTitle('Main Window')
        self.setGeometry(100, 100, 400, 400)


    def open_app(self):
        dialog = QInputDialog(self)
        dialog.setInputMode(QInputDialog.IntInput)
        dialog.setWindowTitle('Open App')
        dialog.setLabelText('Enter app ID:')
        dialog.setIntRange(1, 99)  # Set range for the input
        dialog.setIntValue(1)  # Set default value
        
        ok = dialog.exec_()
        if ok:
            app_id = str(dialog.intValue())
            if app_id in self.app_instances:
                QMessageBox.warning(self, "Error", "App with specified ID is already open.")
                return
            
            self.num_apps_opened += 1
            new_app = APP_UI.APP(self.zmqThread, int(app_id), self)  # Pass as integer to APP
            self.connect_signals(new_app)
            new_app.show()
            self.app_instances[app_id] = new_app

    def close_app(self):
        dialog = QInputDialog(self)
        dialog.setInputMode(QInputDialog.IntInput)
        dialog.setWindowTitle('Close App')
        dialog.setLabelText('Enter app ID:')
        dialog.setIntRange(1, 99)  # Set range for the input
        dialog.setIntValue(1)  # Set default value
        
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

    def handle_app_closed(self, app_id):
        del self.app_instances[str(app_id)]
        self.num_apps_opened -= 1
    
    def whether_logging_in(self, account_id):
        return self.logging_in_accounts.get(account_id) is not None

    def set_log_status(self, account_id, app_id):
        if app_id is not None:
            self.logging_in_accounts[account_id] = app_id
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

    def reset(self):
        confirmation = QMessageBox.question(self, 'Reset Database', 'Are you sure you want to reset the database?', QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if confirmation == QMessageBox.Yes:
            reset_database()
            QMessageBox.information(self, 'Success', 'Database has been reset.')

def initialize_database():
    conn = sqlite3.connect('bank.db')
    cursor = conn.cursor()
    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS accounts (
        id TEXT PRIMARY KEY,
        password TEXT NOT NULL,
        balance REAL NOT NULL
    )
    ''')
    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS transactions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        account_id TEXT NOT NULL,
        type TEXT NOT NULL,
        amount REAL NOT NULL,
        date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        starting_balance REAL NOT NULL,
        ending_balance REAL NOT NULL
    )
    ''')
    
    conn.commit()
    conn.close()

def reset_database():
    conn = sqlite3.connect('bank.db')
    cursor = conn.cursor()
    
    cursor.execute('DROP TABLE IF EXISTS accounts')
    cursor.execute('DROP TABLE IF EXISTS transactions')
    
    conn.commit()
    conn.close()
    initialize_database()  # Recreate tables

if __name__ == '__main__':
    identity = "Team15"
    zmqThread = NetClient.ZmqClientThread(identity=identity)
    app = QApplication(sys.argv)
    mainWindow = Controller(zmqThread)
    mainWindow.show()
    sys.exit(app.exec_())
