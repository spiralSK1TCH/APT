import matplotlib.pyplot as plt
import numpy as np
import cv2 as cv
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
#from PyQt5.GUI import *

class Vidstream():
        
    def __init__(self):

        self.window = cv.namedWindow("frame")
        self.UI = UserInput()
        cv.setMouseCallback("frame",self.UI.handle,0)
        self.vidstream = cv.VideoCapture(-1)
        cv.VideoCapture.set(cv.CAP_PROP_MODE,cv.CAP_MODE_GRAY)
        if not self.vidstream.isOpened():
            print("Check if turret is attached")
            self.vidstream.open(-1)
        self.tracker = TrackRec()
    
    def stream(self,graph=None):   
        
        while True:
            self.webcamOn, self.capture = self.vidstream.read()
            if not self.webcamOn:
                print("Error, frame not captured")
                break
            self.frame()
            if graph:
                graph.displayPlot(self)
            feed = self.displayStream()
            #feed = self.internalStream()
            if feed == False:
                self.endStream()
    
    def displayStream(self):
        cv.imshow("frame", self.capture)
        command = cv.waitKey(1)
        if command == ord("q"):
            return False
        

    def internalStream(self):
        cv.imshow("frame", self.hidden)
        command = cv.waitKey(1)
        if command == ord("q"):
            return False        

    def frame(self):
        self.hidden = self.tracker.find(self.capture)

    def endStream(self):
        self.vidstream.release()
        cv.destroyAllWindows()

class Graph():
    
    def __init__(self):
        self.x  = [0]*81
        self.x2 = [0]*81
    
        for i in range(81):
            self.x[i] = i*8 # DELETED PART WHERE I RAN LOOP CODE 2CE
            self.x2[i]= self.x[i]**2
        
        self.x = np.array(self.x, dtype=int)
        self.x2= np.array(self.x2,dtype=int)

        self.atweak, self.btweak, self.ctweak = 1,1,1

    def plot(self,coord1,coord2,coord3): #changed from x1,y1,x2.. to coords 
        # given 3 points, plot parabola
        matrix = np.array([[coord1[0]**2,coord1[0],1]
                          ,[coord2[0]**2,coord2[0],1]
                          ,[coord3[0]**2,coord3[0],1]
                          ]
                          ,copy=True)
        solutions = np.array([[coord1[1]]
                             ,[coord2[1]]
                             ,[coord3[1]]
                             ])
        coefficients= np.around(np.dot(np.linalg.inv(matrix),solutions),decimals=3)
        print(coefficients)
        self.a = np.take(coefficients,0)
        self.b = np.take(coefficients,1)
        self.c = np.take(coefficients,2)

    
    def tweak(self,x,y):
        predictedy = self.a*(x**2)+self.b*(x)+self.c
        #machine learning function

    def points(self):
        x2term = np.multiply((self.atweak*self.a),self.x2)
        xterm  = np.multiply((self.btweak*self.b),self.x)
        cterm  = (self.ctweak*self.c)
        yterm  = (x2term+xterm+cterm)
        self.y = yterm.astype(int)
    
    def displayPlot(self,img):
        for x in range(81):
            try:
                cv.line(img.capture,(self.x[x], self.y[x]), (self.x[x+1], self.y[x+1]), (0,0,0), 5)
            except:
                pass


class TrackRec():
    
    def __init__(self):
        pass
    
    def find(self,frame):
        hsv = cv.cvtColor(frame, cv.COLOR_BGR2HSV)# OBJECT TRACKING IN RGB
        colourRange = (np.array([110,50 ,50 ])  #default low blue
                      ,np.array([130,255,255])) #default high blue
        mask = cv.inRange(hsv,colourRange[0],colourRange[1])
        self.isolated= cv.bitwise_and(hsv,hsv,mask=mask)
        return self.isolated
    
    def speed(self, coord1, coord2):
        self.hdistance=coord1[0]-coord2[0]
        
        # find hspeed dividing the centres by the time between the two frames, return velocity 
        


    def recognise(self):
        #uses mask to find targets
        pass
    
    def centre(self): 
        # this will find centre of recognised objects
    
    
    
    
        pass
    
class UserInput():
    def __init__(self):
        pass
    def handle(self,event, x, y, flags, para):
        match event:
            case cv.EVENT_LBUTTONDOWN:
                pass
            case cv.EVENT_LBUTTONDBLCLK:
                pass
            case cv.EVENT_RBUTTONDOWN:
                pass
            case cv.EVENT_RBUTTONDBLCLK:
                pass
            case _:
                pass
    def shoot():
        pass
    def track():
        pass
    def close():
        pass

class Menu():
    def __init__(self):
        pass
        
        
    

Test = Vidstream()
x = Graph()
x.plot((200,240),(257,240),(0,300))
x.points()
#x.displayPlot(Test)
Test.stream(x)
