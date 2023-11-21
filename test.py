import matplotlib.pyplot as plt
import numpy as np
import cv2 as cv

# Class for controling camera input 
class Vidstream():

    # Sets up key variables
    def __init__(self):
        
        self.vidstream = cv.VideoCapture(-1,cv.CAP_V4L)         # Connect to last connected camera/webcam
        self.window = cv.namedWindow("frame")                   # Create a window named frame to display things on
        cv.setMouseCallback("frame", mouseCallback, self)       # Clicks on the frame window get handled by a function that references the function
        # If the camera is not open, try to open it manually
        if not self.vidstream.isOpened():
            print("Check if turret is attached")
            raise FileNotFoundError("Turret is not attached")
        self.vidstream.open(-1)
        # Instantiate classes that are used by vidstream
        self.arduinoControl = Arduino()                     # Give the vidstream the Arduino
        self.tracker = TrackRec()                           # Give the vidstream access to the object tracking and recognition function

    # Loop that constantly updates the frame 
    def stream(self,graph=None):    
        
        while True:
            # In perpetuity, read from the camera
            self.webcamOn, self.capture = self.vidstream.read()
            # But if the camera is closed for any reason, stop
            if not self.webcamOn:
                print("Error, frame not captured")
                break
            # If a graph exists, plot it
            if graph:
                graph.displayPlot(self)
            # If a face is in the capture, plot a box around it
            self.tracker.findFaces(self.capture)
            # Or if the user tells you to stop, stop
            frame = self.displayStream()
            if not frame:
                break
        self.endStream()
    
    # Shows the current frame to the user
    def displayStream(self):
        #Show frame to user in a window named "frame"
        cv.imshow("frame", self.capture) 
        # Wait for one second for user input (this also allows adequate time for the screen to display a frame)
        command = cv.waitKey(1) 
        # If the user enters q, they want to quit, so return False. Otherwise, return True.
        if command == ord("q"):
            return False
        return True

    # End video capture and all windows
    def endStream(self):
        self.vidstream.release()
        cv.destroyAllWindows()

# Class to find equation of projectile movement
class Graph():
    
    def __init__(self):
        
        self.x  = [0]*81                # List of x coordinates we apply the equation y = ax2 + bx + c to
        self.x2 = [0]*81                # Predifined x2 list for faster calculations 
        # Giving the list the values of the 8 times table
        for i in range(81):
            self.x[i] = i*8
        # Giving x2 the value of the square of x
        for i in range(81):
            self.x2[i]= i**2
    
    # Quadratic solver method
    def plot(self,coord1,coord2,coord3):
        # given 3 points, plot parabola
        matrix = np.array([[coord1[0]**2,coord1[0],1]
                          ,[coord2[0]**2,coord2[0],1]
                          ,[coord3[0]**2,coord3[0],1]
                          ])
        solutions = np.array([[coord1[1]]
                             ,[coord2[1]]
                             ,[coord3[1]]
                             ])
        inverseMatrix = np.linalg.inv(matrix)       # Inverse matrix
        # Multiply the inverse matrix and solution matrix to get the matrix of coefficents to 3dp
        coefficients= np.around(np.dot(inverseMatrix,solutions),decimals=3)  
        self.a = np.take(coefficients,0)
        self.b = np.take(coefficients,1)
        self.c = np.take(coefficients,2)
    
    # Finds the y value for each x value
    def points(self):
        
        x2term = np.multiply(self.a,self.x2)    # a multiplied over x2
        xterm  = np.multiply(self.b,self.x)     # b multiplied over x
        cterm  = self.c
        yterm  = (x2term+xterm+cterm)           # add together ax2 + bx +c to get y
        self.y = yterm.astype(int)              # y must be a list of integers, as all pixel coordinates are integers
    
    # Display the prediction plot on screen
    def displayPlot(self,img):
        
        for i in range(len(self.x)): # for every x value
            # Try to draw a line between the current coordinate and the next coordinate
            try:
                cv.line(img.capture,(self.x[i], self.y[i]), (self.x[i+1], self.y[i+1]), (0,0,0), 5)
            # If that throws an error (like the point is out of the image), move on t next point
            except:
                pass
        
        
# Arduino control class
class Arduino():

    def __init__(self):
        pass
    
    def moveTurret(self, coordinates, TargetDepthSpeed=None):
        pass
    
    def shootTurret(self):
        pass


# Track and records target positions
class TrackRec():
    def __init__(self):
        pass

# Plaseholder function
def func():
    pass

# Placeholder function specifically for the setMouseCalback function
def mouseCallback(event, x, y, flags, vidstreamInstance):
    match event:
        # If the event is a leftclick 
        case cv.EVENT_LBUTTONDOWN:   
            # Draw crosshairs
            
            # Move the turret to that location and shoot
            vidstreamInstance.arduinoControl.moveTurret((x,y))
            vidstreamInstance.arduinoControl.shootTurret()
        

        # If the event is a rightclick
        case cv.EVENT_RBUTTONDOWN:
            pass

def drawCrosshairs(x, y, vidstreamInstance = None):
    if not vidstreamInstance:
        pass


# Class that identifies and tracks targets
class TrackRec():
    
    # Setup
    def __init__(self):
        # Hold stack of last seen positions
        self.lastSeenPositions = []
        # Call classifier method for targets and faces
        self.targetCascade = cv.CascadeClassifier()
        self.faceCascade = cv.CascadeClassifier()
        # Load cascade classifiers, if not found exit
        if not self.faceCascade.load(cv.samples.findFile(".venv/lib64/python3.11/site-packages/cv2/data/haarcascade_frontalface_default.xml")):
            print("No face cascade found")
            exit(0)
        #if not self.targetCascade.load(cv.samples.findFile):
        #    print("No target cascade found")
        #    exit(0)

    # Face recognition method
    def findFaces(self,frame):
        # Make frame greysclae
        frameGray = cv.cvtColor(frame, cv.COLOR_BGR2GRAY) 
        # Make grayscale image sharper.
        self.frameGray = cv.equalizeHist(frameGray)    
        # Detect faces
        faces = self.faceCascade.detectMultiScale(frameGray, 1.1 ,4)
        # for each rectangle in faces
        for (x,y,w,h) in faces:
            # Draw box around faces
            cv.rectangle(frame, (x,y), (x+w, y+h),(255,0,0), 2 )

    # Target recognition method
    def findTargets(self, frame):
        # Detect targets
        targets = self.targetCascade.detectMultiScale(self.frameGray, 1.1, 4)
        # for every rectangle in targets
        for (x,y,w,h) in targets:
            # Draw box around faces
            cv.rectangle(frame, (x,y), (x+w, y+h), (0,0,255), 2)
            # Find centre of rectangle
            centre = (x+(w/2),y+(h/2))
        

         

# Code to activate the class
test = Vidstream()
test.stream()
graph= Graph()
graph.plot((50,22), (7,40), (10,25))