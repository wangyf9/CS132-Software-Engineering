from PyQt5.QtWidgets import QMainWindow, QPushButton, QMessageBox, QInputDialog, QApplication
import sys
import APP_UI
import NetClient
import ATM_UI
class MainWindow(QMainWindow):
    def __init__(self, zmqThread):
        super().__init__()
        self.zmqThread = zmqThread
        self.num_apps_opened = 0
        self.app_instances = {}
        self.initUI()

    def initUI(self):
        openAppButton = QPushButton('Open App', self)
        openAppButton.clicked.connect(self.open_app)
        openAppButton.setGeometry(50, 50, 200, 50)

        closeAppButton = QPushButton('Close App', self)
        closeAppButton.clicked.connect(self.close_app)
        closeAppButton.setGeometry(50, 150, 200, 50)

        self.setWindowTitle('Main Window')
        self.setGeometry(100, 100, 300, 250)

    def open_app(self):
        app_id, ok = QInputDialog.getText(self, 'Open App', 'Enter app ID:')
        if ok and app_id:
            try:
                app_id = int(app_id)
                if app_id <= 0:
                    QMessageBox.warning(self, "Error", "App ID must be a positive integer.")
                    return
                if app_id in self.app_instances:
                    QMessageBox.warning(self, "Error", "App with specified ID is already open.")
                    return
            except ValueError:
                QMessageBox.warning(self, "Error", "App ID must be a positive integer.")
                return

            self.num_apps_opened += 1
            new_app = APP_UI.APP(zmqThread, app_id)
            new_app.show()
            self.app_instances[app_id] = new_app

    def close_app(self):
        app_id, ok = QInputDialog.getText(self, 'Close App', 'Enter app ID:')
        if ok and app_id:
            if not app_id.isdigit() or int(app_id) <= 0:
                QMessageBox.warning(self, "Error", "App ID must be a positive integer.")
                return
            app_id = int(app_id)
            if app_id in self.app_instances:
                self.app_instances[app_id].close()
                del self.app_instances[app_id]
                self.num_apps_opened -= 1
            else:
                QMessageBox.warning(self, "Error", "App with specified ID is not open.")

if __name__ == '__main__':
    identity = "Team15"
    zmqThread = NetClient.ZmqClientThread(identity=identity)
    app = QApplication(sys.argv)
    mainWindow = MainWindow(zmqThread)
    mainWindow.show()
    ex = ATM_UI.ATM(zmqThread)
    ex.show()
    sys.exit(app.exec_())