import os, sys
from PyQt5.QtWidgets import QHBoxLayout, QMainWindow, QApplication, QLabel, QLineEdit, QWidget, QPushButton, QVBoxLayout 
import passwordDatabase 
# Login Screen
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("APT")
        self.loginMenu()

    def loginMenu(self):
        # Set a simple vertical layout
        layout = QVBoxLayout()
        # Set up a widget to be a central widget (displayed) 
        widget = QWidget()
        # Set up input widgits (the password and username textboxes and submit button)
        self.username = QLineEdit()
        self.password = QLineEdit()
        submit = QPushButton()
        self.username.setPlaceholderText("Username")
        self.password.setPlaceholderText("Password")
        submit.setText("Submit")
        
        # When button is clicked, activate the password checker
        submit.clicked.connect(self.submit)

        # Make test in the texbox not visible 
        self.password.setEchoMode(QLineEdit.Password)
        # Add layouts to the vertical boxes
        layout.addWidget(self.username)
        layout.addWidget(self.password)
        layout.addWidget(submit)
        # Make this layout one widget, then set it as the central widget
        widget.setLayout(layout)
        self.setCentralWidget(widget)

    def submit(self):
        # If the text in the username box is an e
        # ntry in the database
        if passwordDatabase.searchDB(self.username.text()):
            if passwordDatabase.passwordCheckDB(self.username.text(), self.password.text()):
                # Login and move to main menu
                self.mainMenu() 
            else:
                self.username.clear()
                self.password.clear()
        else:
            self.username.clear()
            self.password.clear()
            
        self.username.text()

    def mainMenu(self):
        # Create pushable buttons
        self.autonomousMode = QPushButton()
        self.manualMode = QPushButton()
        self.options = QPushButton()
        self.logout = QPushButton()
        # Add labels to buttons
        self.autonomousMode.setText("Autonomous Mode")
        self.manualMode.setText("Manual Mode")
        self.options.setText("Options")
        self.logout.setText("Log Out")
        # Set layout for these buttons
        layout = QVBoxLayout()
        hlayout = QHBoxLayout()
        # Add functionality to buttons
        self.autonomousMode.clicked.connect(self.openMain)
        self.manualMode.clicked.connect(self.openMain)
        self.logout.clicked.connect(self.loginMenu)
        # Add buttons to layout
        layout.addWidget(self.autonomousMode)
        layout.addWidget(self.manualMode)
        hlayout.addWidget(self.options)
        hlayout.addWidget(self.logout)
        layout.addLayout(hlayout)
        #Create widget to attach these buttons to
        widget = QWidget()
        # Add buttons to the widget
        widget.setLayout(layout)
        self.setCentralWidget(widget)

    # Open the main program
    def openMain(self):
        self.hide()
        os.system("python test.py")
        self.show()

passwordDatabase.setup()
app = QApplication(sys.argv)

login = MainWindow()
login.show()

app.exec()
