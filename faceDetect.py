from picamera.array import PiRGBArray
from picamera import PiCamera
import time
import cv2
import numpy as np
import imutils
import maestro
import sys
import select
import client

#class KeyControl sets motor speed of the tango bot
class KeyControl():
    def __init__(self):
        self.tango = maestro.Controller()
        self.body = 6000
        self.headTurn = 6000
        self.headTilt = 6000
        self.motors = 6000
        self.turn = 6000

    def getHead(self):
        return self.headTurn, self.headTilt

    #increments head turn and tilt based on key inputs (key is translated from char to integer)
    def head(self,key):
        print(key)
        if key == 97:
            time.sleep(.05)
            self.headTurn += 200
            if(self.headTurn > 7900):
                self.headTurn = 7900
            self.tango.setTarget(HEADTURN, self.headTurn)
        elif key == 100:
            time.sleep(.05)
            self.headTurn -= 200
            if(self.headTurn < 1510):
                self.headTurn = 1510
            self.tango.setTarget(HEADTURN, self.headTurn)
        elif key == 101:
            self.headTurn = 6000
            self.headTilt = 6000
            self.tango.setTarget(HEADTURN, self.headTurn)
            self.tango.setTarget(HEADTILT, self.headTilt)
        elif key == 119:
            self.headTilt += 200
            if(self.headTilt > 7900):
                self.headTilt = 7900
            self.tango.setTarget(HEADTILT, self.headTilt)
        elif key == 115:
            self.headTilt -= 200
            if(self.headTilt < 1510):
                self.headTilt = 1510
            self.tango.setTarget(HEADTILT, self.headTilt)


    #increments body value based on key inputs
    def waist(self, key):
        print(key)

        if key == 122:
            self.body += 200
            if(self.body > 7900):
                self.body = 7900
            self.tango.setTarget(BODY, self.body)
            print("waist right")
        elif key == 99:
            self.body -= 200
            if(self.body < 1510):
                self.body = 1510
            self.tango.setTarget(BODY, self.body)
            print ('waist left')

    #increments drive speed on key presses
    #self.motors is how much above or below 0m/s both drive
    #self.turn is the offset(above 6000 mean right motor drives more foward than left)
    def arrow(self, key):
        print(key)
        if key == 84:
            self.motors = 5000
            if(self.motors > 7900):
                self.motors = 7900
            print(self.motors)
            self.tango.setTarget(MOTORS, self.motors)
        elif key == 82:
            self.motors = 6800
            if(self.motors < 1510):
                self.motors = 1510
            print(self.motors)
            self.tango.setTarget(MOTORS, self.motors)
        elif key == 83:
            self.turn = 5100
            if(self.turn > 7400):
                self.turn = 7400
            print(self.turn)
            self.tango.setTarget(TURN, self.turn)
        elif key == 81:
            self.turn = 6900
            if(self.turn <2110):
                self.turn = 2110
            print(self.turn)
            self.tango.setTarget(TURN, self.turn)

        elif key == 32:
            self.motors = 6000
            self.turn = 6000
            self.tango.setTarget(MOTORS, self.motors)
            self.tango.setTarget(TURN, self.turn)

    #passes in a string that changes forward and turn to set values if nothing is passed, motors stop
    def setTurn(self,str):
        if str=="forward":
            self.motors=5350
            self.turn=6000
            self.tango.setTarget(MOTORS, self.motors)
            self.tango.setTarget(TURN, self.turn)
        elif str=="right":
            self.motors=6000
            self.turn=5080
            self.tango.setTarget(MOTORS, self.motors)
            self.tango.setTarget(TURN, self.turn)
        elif str=="left":
            self.motors=6000
            self.turn=6920
            self.tango.setTarget(MOTORS, self.motors)
            self.tango.setTarget(TURN, self.turn)
        else:
            self.motors = 6000
            self.turn = 6000
            self.tango.setTarget(MOTORS, self.motors)
            self.tango.setTarget(TURN, self.turn)

def motion(control, state, x, y, size, LR):
    angle, tilt = control.getHead()
    if state==0:
        print(angle)
        if angle > 7800 and LR=='L':
            LR='R'
        elif angle < 4300 and LR=='R':
            LR='L'
        if(LR=='L'):
            control.head(ord('a'))
        if(LR=='R'):
            control.head(ord('d'))
    elif state==1:
        pass
    elif state==2:
        if x < 260:
            keys.head(97)
        elif x > 380:
            keys.head(100)
        if y < 150:
            keys.head(119)
        elif y > 300:
            keys.head(115)
    return LR

def turn2center(x):
    #while x != 6000:
    if x >= 5900 and x <= 6100:
        x = 6000
    if x > 6100:
        print(x)
        keys.arrow(81)
        time.sleep(.5)
        #keys.head(100)
    elif x < 5900:
        print(x)
        keys.arrow(83)
        time.sleep(.5)
        #keys.head(97)
    keys.arrow(32)


def move2you(x):
    #while x != 90:
    if x >= 89 and x <= 120:
        x = 90
    if x > 120:
        print(x)
        keys.arrow(82)
        time.sleep(1)
    elif x < 89:
        print(x)
        keys.arrow(84)
        time.sleep(.5)
    keys.arrow(32)



face_cascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')

# initialize the camera and grab a reference to the raw camera capture


# capture frames from the camera


camera = PiCamera()
camera.resolution = (640, 480)
camera.framerate = 32
rawCapture = PiRGBArray(camera, size=(640, 480))

# allow the camera to warmup
time.sleep(0.1)

IP = '10.200.42.220'
PORT = 5010
client = client.ClientSocket(IP, PORT)

MOTORS = 1
TURN = 2
BODY = 0
HEADTILT = 4
HEADTURN = 3

#sets up keyboard object for input
keys = KeyControl()
keys.head(ord('w'))

state=0    #0=no face found 1=face found but not right distance 2=face tracking with only neck
faceLR='R'   #where the face was last seen
size=0
centerX=0
centerY=0
tf = True
follow = False
count = 0

for frame in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):

    img = frame.array
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, 1.3, 5)


    for (x,y,w,h) in faces:
        count = 0
        cv2.rectangle(img,(x,y),(x+w,y+h),(255,0,0))
        state=2
        centerX=x+(w/2)
        centerY=y+(h/2)
        size=w*h
        if follow is False:
            if centerX > 280 and centerX < 360:
                while tf == True:
                    time.sleep(1)
                    client.sendData("Howdy")
                    #client.killSocket()
                    tf = False
                xx, yy = keys.getHead()
                if xx > 5700 and xx < 6300:
                    print("moves")
                    move2you(w)
                    if w >= 89 and w <= 120:
                        follow = True
                        break
                else:
                    print("turns")
                    turn2center(xx)
    faceLR=motion(keys,state,centerX,centerY,size,faceLR)
    if len(faces) == 0:
        count += 1

    if count == 75:
        keys.head(101)
        state=0    #0=no face found 1=face found but not right distance 2=face tracking with only neck
        faceLR='R'
        size=0
        centerX=0
        centerY=0
        tf = True
        follow = False
        count = 0


    cv2.imshow('Image',img)

    # clear the stream in preparation for the next frame
    rawCapture.truncate(0)

    #---------quits if q is entered in terminal
    while sys.stdin in select.select([sys.stdin], [], [], 0)[0]:
        line = sys.stdin.readline()
        if line[0]=="q":
            keys.arrow(32)
            exit()
#-----------


cv2.destroyAllWindows()

#Flow
#
#while face not found for 15 secs:
#search left right up down until face is detected
#
#
#hello human
#center neck, keep face on screen

#if face is centered:
#drive until sized correctly
#else: center face
#
#move neck to center on face without driving
