from picamera.array import PiRGBArray
from picamera import PiCamera
import time
import numpy as np
import cv2 as cv
import imutils
import maestro
import sys
import select

face_cascade = cv.CascadeClassifier('haarcascade_frontalface_default.xml')


camera = PiCamera()
camera.resolution = (640, 480)
camera.framerate = 32
rawCapture = PiRGBArray(camera, size=(640, 480))

# allow the camera to warmup
time.sleep(0.1)

for frame in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):
    img = frame.array

    gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, 1.3, 5)
    #print(faces)
    for (x,y,w,h) in faces:
        cv.rectangle(img,(x,y),(x+w,y+h),(255,0,0))
        print(w)
        roi_gray = gray[y:y+h, x:x+w]
        roi_color = img[y:y+h, x:x+w]

    cv.imshow('Image',img)
    if cv.waitKey(1) & 0xFF == ord('q'):
        break

    # clear the stream in preparation for the next frame
    rawCapture.truncate(0)

cv.destroyAllWindows()
