import sys
from PyQt6.QtWidgets import QMainWindow, QApplication, QLabel, QLineEdit, QWidget, QPushButton, QVBoxLayout 

# Login Screen
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("APT")
        title = QLabel("Automated Projectile Turret")
        layout = QVBoxLayout()

        username = QLineEdit()
        password = QLineEdit()

        layout.addWidget(username)
        layout.addWidget(password)
        
app = QApplication(sys.argv)

login = MainWindow()
login.show()

app.exec()
