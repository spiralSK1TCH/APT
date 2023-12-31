import matplotlib.pyplot as plt
import numpy as np
import cv2 as cv
import zmq
import os

context = zmq.Context()

# Class for controling camera input 
class Vidstream():

    # Sets up key variables
    def __init__(self):
        # Instantiate classes that are used by vidstream
        self.arduinoControl = Arduino()                     # Give the vidstream the Arduino
        self.tracker = TrackRec()                           # Give the vidstream access to the object tracking and recognition function
        self.vidstream = cv.VideoCapture(-1,cv.CAP_V4L)         # Connect to last connected camera/webcam
        self.window = cv.namedWindow("frame")                   # Create a window named frame to display things on
        cv.setMouseCallback("frame", mouseCallback, self)       # Clicks on the frame window get handled by a function that references the function
        # If the camera is not open, try to open it manually
        if not self.vidstream.isOpened():
            print("Check if turret is attached")
            raise FileNotFoundError("Turret is not attached")
        self.vidstream.open(-1)
                         
    # Loop that constantly updates the frame 
    def stream(self):    
        
        graph = Graph()
        # detectionStage allows the program to understand whether it should detect objects or tract them
        detectionStage = 0
        while True:
            # In perpetuity, read from the camera
            self.webcamOn, self.capture = self.vidstream.read()
            # But if the camera is closed for any reason, stop
            if not self.webcamOn:
                print("Error, frame not captured")
                break
            # If a face is in the capture, plot a box around it
            self.tracker.findFaces(self.capture)
            match detectionStage:
                case 0:
                    # if in first detection stage, search frame for red circles, then increment stage 
                    if self.tracker.find(self.capture):
                        detectionStage += 1
                        
                case 1:
                    if self.tracker.track(self.capture):
                        detectionStage += 1

                        
         
                    else:
                        detectionStage = 0
                case 2:
                    if self.tracker.track(self.capture):
                        graph.plot(self.tracker.lastSeenPositions[-3], self.tracker.lastSeenPositions[-2], self.tracker.lastSeenPositions[-1])
                        graph.points()


                    detectionStage = 0
            # If a graph exists, plot it
            if graph.a:
                graph.displayPlot(self.capture)
            # print information on the screen

            cv.putText(self.capture, 
            f"Face Detected? = {self.tracker.face}", (0,405), 1, 2,(0,255,0), 2)
            cv.putText(self.capture, 
            f"Obj Detected? = {bool(detectionStage)}", (0,430), 1, 2,(0,255,0), 2)
            # If there are last seen positions, show object speed
            if "N/A" in self.tracker.lastSeenPositions[-3:]:
                cv.putText(self.capture, 
                f"Obj Speed = N/A", (0,455), 1, 2,(0,255,0), 2)
            else:
                cv.putText(self.capture, 
                f"Obj Speed = {graph.speed(self.tracker.lastSeenPositions[-3][0],self.tracker.lastSeenPositions[-1][0])}", (0,455), 1, 2,(0,255,0), 2)
            cv.putText(self.capture, 
            f"Target Postion = {self.tracker.lastSeenPositions[-1]}", (0,480), 1, 2,(0,255,0), 2)

 
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
        socket.send_string("X")
        socket.close()
        context.destroy()

# Class to find equation of projectile movement
class Graph():
    
    def __init__(self):
        self.targetSpeed = "N/A"
        self.x  = [0]*81                # List of x coordinates we apply the equation y = ax2 + bx + c to
        self.x2 = [0]*81                # Predifined x2 list for faster calculations 
        # Giving the list the values of the 8 times table
        for i in range(81):
            self.x[i] = i*8 # DELETED PART WHERE I RAN LOOP CODE 2CE
            self.x2[i]= self.x[i]**2
        
        # variable is declared as None so existancecan be checked
        self.a = None
    
    # Quadratic solver method
    def plot(self,coord1,coord2,coord3):
        # If the x coordinates are all the same, defer to linearPlot
        if coord1[0] == coord2[0] or coord1[0] == coord3[0] or coord2[0] == coord3[0]:
            return self.linearPlot(coord1, coord2, coord3)
        # If duplicates in x cooordinates, skip
        dup = coord1[0], coord2[0], coord3[0]
        self.coord1 = coord1
        self.coord2 = coord2
        self.coord3 = coord3
        if len(set(dup)) != len(dup):
            pass
        # given 3 points, plot parabola
        matrix = np.array([[coord1[0]**2,coord1[0],1]
                          ,[coord2[0]**2,coord2[0],1]
                          ,[coord3[0]**2,coord3[0],1]
                          ], copy = True)
        solutions = np.array([[coord1[1]]
                             ,[coord2[1]]
                             ,[coord3[1]]
                             ])
        # Inverse matrix        
        inverseMatrix = np.linalg.inv(matrix) 

        # Multiply the inverse matrix and solution matrix to get the matrix of coefficents to 3dp
        coefficients = np.around(np.dot(inverseMatrix,solutions),decimals=3)
        self.a = np.take(coefficients,0)
        self.b = np.take(coefficients,1)
        self.c = np.take(coefficients,2)
    
    def speed(self,x1,x2):
        self.targetSpeed = (x2-x1)/2
        return self.targetSpeed

    
    # Finds the y value for each x value
    def points(self):
        try:
            x2term = np.multiply(self.a,self.x2)    # a multiplied over x2
            xterm  = np.multiply(self.b,self.x)     # b multiplied over x
            cterm  = self.c
            yterm  = (x2term+xterm+cterm)           # add together ax2 + bx +c to get y
            self.y = yterm.astype(int)              # y must be a list of integers, as all pixel coordinates are integers
        except:
            pass
    
    # Display the prediction plot on screen
    def displayPlot(self,img):
        #print(self.y)
        cv.circle(img, (self.coord1[0], self.coord1[1]), 3, (0,0,255), 1)
        cv.circle(img, (self.coord2[0], self.coord2[1]), 3, (0,0,255), 1)
        cv.circle(img, (self.coord3[0], self.coord3[1]), 3, (0,0,255), 1)
        for i in range(len(self.x)): # for every x value
            # Try to draw a line between the current coordinate and the next coordinate
            try:
                cv.line(img, (self.x[i], self.y[i]), (self.x[i+1], self.y[i+1]), (0,0,0), 5)
            # If that throws an error (like the point is out of the image), move on t next point
            except:
                pass

    # function for resolving vertical lines
    def linearPlot(self, coord1, coord2, coord3):
        #self.x = (coord1[0],coord1[0])
        #self.y = (0,480)
        pass

# Class that identifies and tracks targets
class TrackRec():
    
    # Setup
    def __init__(self):
        # Hold stack of last seen positions
        self.lastSeenPositions = ["N/A","N/A","N/A"]
        # Call classifier method for targets and faces
        self.faceCascade = cv.CascadeClassifier()
        # is face in frame?
        self.face = False
        # Load cascade classifiers, if not found exit
        if not self.faceCascade.load(cv.samples.findFile(".venv/lib64/python3.11/site-packages/cv2/data/haarcascade_frontalface_default.xml")):
            print("No face cascade found")
            exit(0)
         # Get context to set up the TCP port
        # Create a reply socket on this port
        socket = context.socket(zmq.REP)
        # Bind the reply socket to the TCP port
        socket.bind("tcp://*:5556")
        tracker = socket.recv()
        match tracker:
            # Initialise BOOSTING algorithm
            case b"0":
                self.tracker = cv.legacy.TrackerBoosting_create()
                print("yo")
            # Initialise MIL algorithm
            case b"1":
                self.tracker = cv.legacy.TrackerMIL_create()
            # Initialise KCF algorithm
            case b"2":
                self.tracker = cv.legacy.TrackerKCF_create()
            # Initialise TLD algorithm
            case b"3":
                self.tracker = cv.legacy.TrackerTLD_create()
            # Initialise MedianFlow algorithm
            case b"4":
                self.tracker = cv.legacy.TrackerMedianFlow_create()
            # Initialise Mosse algorithm
            case b"5":
                self.tracker = cv.legacy.TrackerMOSSE_create()
            # Initialise CSRT algorithm
            case b"6":
                self.tracker = cv.legacy.TrackerCSRT_create()


    # Face recognition method
    def findFaces(self,frame):
        # Make frame greysclae
        frameGray = cv.cvtColor(frame, cv.COLOR_BGR2GRAY) 
        # Make grayscale image sharper.
        self.frameGray = cv.equalizeHist(frameGray)    
        # Detect faces
        faces = self.faceCascade.detectMultiScale(frameGray, 1.1 ,4)
        # for each rectangle in faces
        face = False
        for (x,y,w,h) in faces:
            # Draw box around faces
            cv.rectangle(frame, (x,y), (x+w, y+h),(255,0,0), 2 )
            face = True
        self.face = face

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
            self.lastSeenPositions.append(centre)

    # Create mask of only the red colours
    def find(self,frame):
        # blur the frame
        median = cv.medianBlur(frame, 5)
        Guassian = cv.GaussianBlur(median, (5,5), 0)
        # Convert pixels to hsv values
        hsv = cv.cvtColor(Guassian, cv.COLOR_BGR2HSV)# OBJECT TRACKING IN RGB

        # lower mask (0-10)
        lowerRed = np.array([0,100,100])
        upperRed = np.array([10,255,255])
        mask0 = cv.inRange(hsv, lowerRed, upperRed)

        # upper mask (170-180)
        lowerRed = np.array([165,50,50])
        upperRed = np.array([179,255,255])
        mask1 = cv.inRange(hsv, lowerRed, upperRed)
        # join my masks
        mask = mask0+mask1
        # Only return red values
        redIsolated = cv.bitwise_and(hsv,hsv,mask=mask)
        # Turn this greyscale to prepare for thresholding
        greyImage = cv.cvtColor(redIsolated, cv.COLOR_BGR2GRAY)
        # threshold the image
        _, thresh = cv.threshold(greyImage, 127, 255, 0)
        # Get the list of contoured from this image
        contours, _  = cv.findContours(thresh, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_NONE)
        circleContours = []
        # For each contour in the list, check ciruclarity
        count = 0
        for i in contours:
            # create a polygon thar models each contour
            count += 1
            polygon = cv.approxPolyDP(i, .03 * cv.arcLength(i, True), True)
            # check only shapes which have more than 8 lines 
            
            if len(polygon) >= 7:
                # Check if shape is circular
                isCircle = cv.isContourConvex(polygon)
                # If it is a circle, append it to a new list
                if isCircle:
                    circleContours.append(i)
                    
            # If the contour has less than 8 lines, probably not a circle 
            
        contouredFrame = cv.drawContours(frame, circleContours, -1, (0, 255, 0), 4)
        # Find centre of the contours and draw bounding box
        # Keep track of largest area so we can decide which bound box to track
        largestArea = 0
        for i in circleContours:
           # Find bounding box
            x, y, w, h = cv.boundingRect(i)
            bbox = (x, y, w, h)
            # Drew all the bounding boxes
            cv.rectangle(contouredFrame, (x,y), (x+w, y+h), (0,255,0), 3)
            # Initialise the tracer on the largest area box
            if w*h > largestArea:
                # Initialise tracker on this bounding boxes
                self.tracker.init(frame, bbox)
                largestArea = w*h
                centre = cv.moments(i)
                # find xcoordinate of centre.
                xcoord = int(centre["m10"]/centre["m00"])
                # find ycoord of centre.
                ycoord = int(centre["m01"]/centre["m00"])
                centre = (xcoord,ycoord)
        #cv.imshow(contouredFrame)
        if circleContours:
            self.lastSeenPositions.append(centre)    
            return True

 
    def track(self, frame):
        returned, bbox = self.tracker.update(frame)
        if returned:
            # get the box coordinates
            (x, y, w, h) = [int(v) for v in bbox]
            print(x,y,w,h)
            # find xcoordinate of centre 
            xcoord = int(x + (w/2))
            # find ycoord of centre
            ycoord = int(y + (h/2))
            centre = (xcoord,ycoord)
            self.lastSeenPositions.append(centre)
           

            # use predicted bounding box coordinates to draw a rectangle
        return returned

# Arduino control class
class Arduino():

    # Initialise connection with the arduino.py file
    def __init__(self):
        os.system("./Hardware/arduinoRun.sh")
        print("Connecting to Arduino...")
        try:
            # Get context to set up the TCP port
            # Create a request socket on this port (Global so it can be shutdown)
            global socket
            socket = context.socket(zmq.REQ)
            # Bind the request socket to the TCP port
            socket.connect("tcp://localhost:5555")
        except:
            print("Could not connect")
            exit(0)
    
    def moveTurret(self, coordinates, TargetDepthSpeed=None):
        socket.send_string(f"A {(coordinates[0]-180)*0.25}")
        _ = socket.recv()
        socket.send_string(f"B {(coordinates[1]-180)*0.25}")
        _ = socket.recv()

    
    def shootTurret(self):
        socket.send_string(f"C done")


# Track and records target positions

# Placeholder function specifically for the setMouseCalback function
def mouseCallback(event, x, y, flags, vidstreamInstance):
    match event:
        # If the event is a leftclick 
        case cv.EVENT_LBUTTONDOWN:   
            # Draw crosshairs
            
            print("case")
            # Move the turret to that location and shoot
            vidstreamInstance.arduinoControl.moveTurret((x,y))
            vidstreamInstance.arduinoControl.shootTurret()
        

        # If the event is a rightclick
        case cv.EVENT_RBUTTONDOWN:
            pass

def drawCrosshairs(x, y, vidstreamInstance = None):
    if not vidstreamInstance:
        pass

# Give the vidstream access to the object tracking and recognition function

         

# Code to activate the class
test = Vidstream()
test.stream()

