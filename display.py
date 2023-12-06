import os, sys
from PyQt5.QtWidgets import QHBoxLayout, QMainWindow, QApplication, QLabel, QLineEdit, QWidget, QPushButton, QVBoxLayout 
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
import passwordDatabase 
import zmq
# Login Screen
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("APT")
        self.loginMenu()
        # Set default tracker 
        self.currentTracker = 6

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
        # Make the submit button get pressed when you press the enter key
        submit.setAutoDefault(True)
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
                # Update last login date 
                passwordDatabase.updateDate(self.username.text())
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
        self.options.clicked.connect(self.optionMenu)
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

    def optionMenu(self):
        # Set the tracker to be global
        global trackers
        
        # Create buttons corresponding to each object tracking algorithm
        buttonLayout= QGridLayout()        # Grid layout for the buttons
        self.trackerButtons = {}
        trackers = ['BOOSTING', 'MIL', 'KCF', 'TLD', 'MEDIANFLOW', 'MOSSE', 'CSRT']
        for i in range(len(trackers)):
            self.trackerButtons[trackers[i]] = QPushButton()
            self.trackerButtons[trackers[i]].setText(trackers[i])
            self.trackerButtons[trackers[i]].setCheckable(True)
            self.trackerButtons[trackers[i]].clicked.connect(lambda state, currentButton = i: self.chooseTracker(currentButton))
            buttonLayout.addWidget(self.trackerButtons[trackers[i]], int(i//3), int(i%3))
        # Set CSRT as clicked down
        self.trackerButtons["CSRT"].setChecked(True)
        # Create back button, bound to mainMenu
        back = QPushButton()
        back.setText("Back")
        back.clicked.connect(self.mainMenu)
        # Create overarching vertical layout
        optionLayout = QVBoxLayout()
        # Add all sub layouts to this overarching layout
        optionLayout.addLayout(buttonLayout)
        optionLayout.addWidget(back)
        # Create widget to attach these layouts to 
        self.widget = QWidget()
        self.widget.setLayout(optionLayout)
        self.setCentralWidget(self.widget)

    def chooseTracker(self, button):
        for i in range(len(trackers)):
            if i == button:
                self.currentTracker = i
                continue
            self.trackerButtons[trackers[i]].setChecked(False)
        #self.centralWidget.update()
    def openMain(self):
        self.hide()
        # Get context to set up the TCP port
        context = zmq.Context()
        # Create a request socket on this port (Global so it can be shutdown)
        socket = context.socket(zmq.REQ)
        # Bind the request socket to the TCP port
        socket.connect("tcp://localhost:5556")
        socket.send_string(str(self.currentTracker))
        socket.close()
        os.system("python test.py")
        self.show()

    # Define new username
    def newUserMenu(self):

        pass

    # 

passwordDatabase.setup()
app = QApplication(sys.argv)

login = MainWindow()
login.show()

app.exec()
passwordDatabase.closeDB()
