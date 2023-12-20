import json
from cv2.samples import findFile
import numpy as np
import cv2 as cv 
import zmq

# Class that identifies and tracks targets

# Is facein frame
faces = False
# Hold stack of last seen positions
lastSeenPositions = ["N/A"]
# Call classifier method for targets and faces
faceCascade = cv.CascadeClassifier()
# Get context to set up the TCP port
context = zmq.Context()
# Create a reply socket on this port to the chosen Tracker in options
trackerChoiceSocket = context.socket(zmq.REP)
# Bind the reply socket to the TCP port
trackerChoiceSocket.bind("tcp://*:5556")
tracker = trackerChoiceSocket.recv()
# Create another reply socket to communicate with main program
socket = context.socket(zmq.REP)
socket.bind("tcp://*:5557")
# Image socket (passes in current frame)
image = context.socket(zmq.REP)
image.bind("tcp://*:5558")


# Setup
def start():
    global tracker
    global socket
    # Load cascade classifiers, if not found exit
    if not faceCascade.load(cv.samples.findFile(".venv/lib64/python3.11/site-packages/cv2/data/haarcascade_frontalface_default.xml")):
        print("No face cascade found")
        exit(0)
    match tracker:
        # Initialise BOOSTING algorithm
        case b"0":
            tracker = cv.legacy.TrackerBoosting_create()
        # Initialise MIL algorithm
        case b"1":
            tracker = cv.legacy.TrackerMIL_create()
        # Initialise KCF algorithm
        case b"2":
            tracker = cv.legacy.TrackerKCF_create()
        # Initialise TLD algorithm
        case b"3":
            tracker = cv.legacy.TrackerTLD_create()
        # Initialise MedianFlow algorithm
        case b"4":
            tracker = cv.legacy.TrackerMedianFlow_create()
        # Initialise Mosse algorithm
        case b"5":
            tracker = cv.legacy.TrackerMOSSE_create()
        # Initialise CSRT algorithm
        case b"6":
            tracker = cv.legacy.TrackerCSRT_create()


# Face recognition method
def findFaces(frame):
    # Make frame greysclae
    frameGray = cv.cvtColor(frame, cv.COLOR_BGR2GRAY) 
    # Make grayscale image sharper.
    frameGray = cv.equalizeHist(frameGray)    
    # Detect faces
    faces = faceCascade.detectMultiScale(frameGray, 1.1 ,4)
    # for each rectangle in faces
    for (x,y,w,h) in faces:
        # Draw box around faces
        cv.rectangle(frame, (x,y), (x+w, y+h),(255,0,0), 2 ) 
    socket.send(json.dumps(faces))

# Create mask of only the red colours
def find(frame):
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
            tracker.init(frame, bbox)
            largestArea = w*h
            centre = cv.moments(i)
            # find xcoordinate of centre.
            xcoord = int(centre["m10"]/centre["m00"])
            # find ycoord of centre.
            ycoord = int(centre["m01"]/centre["m00"])
            centre = (xcoord,ycoord)
    #cv.imshow(contouredFrame)
    if circleContours:
        socket.send((json.dumps(centre)))


def track(frame):
    returned, bbox = tracker.update(frame)
    if returned:
        # get the box coordinates
        (x, y, w, h) = [int(v) for v in bbox]
        print(x,y,w,h)
        # find xcoordinate of centre 
        xcoord = int(x + (w/2))
        # find ycoord of centre
        ycoord = int(y + (h/2))
        centre = (xcoord,ycoord)
        # send back a centre to use in main file
        socket.send(json.dumps((centre)))

# Startup code
start()
# Feedback loop to check socket
while True:
    # Wait for next request from client
    message = socket.recv()
    print(message)
    print(f"Received request: {message}")
    image = json.loads(image.recv())
    match message:
        case b"A":
            find(image)
        case b"B":
            track(image)
        case b"C":
            findFaces(image)
        case b"X":
            break
socket.close()
exit(0)
