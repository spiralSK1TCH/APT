import matplotlib.pyplot as plt
import numpy as np
import cv2 as cv
class Vidstream():
    
    def __init__(self):
        self.vidstream = cv.VideoCapture(-1)
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
    
    def displayStream(self,object=None):
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
    
    def recognise(self):
        #uses mask to find targets
        pass
    
    def centre(self): 
        # this will find centre of recognised objects
        pass



Test = Vidstream()
x = Graph()
x.plot((200,240),(257,240),(0,0))
x.points()
#x.displayPlot(Test)
Test.stream(x)
