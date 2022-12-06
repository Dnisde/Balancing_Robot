# import the necessary packages
from picamera2.array import PiRGBArray
from picamera2 import PiCamera2
import time
import cv2

face_cascade= cv2.CascadeClassifier('haarcascade_frontalface_default.xml')

width,height=320,240
camera = PiCamera2()
camera.resolution = (width,height)
camera.framerate = 30
rawCapture = PiRGBArray(camera, size=(width,height))
time.sleep(1)

for frame in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):
    image = frame.array
    frame=cv2.flip(image,1)
    gray=cv2.cvtColor(frame,cv2.COLOR_BGR2GRAY)    

    #detect face coordinates x,y,w,h
    faces=face_cascade.detectMultiScale(gray,1.3,5)
    c=0
    for(x,y,w,h) in faces:
        c+=1
        if(c>1):
            break
        #centre of face
        face_centre_x=x+w/2
        face_centre_y=y+h/2
        #pixels to move 
        error_x=160-face_centre_x
        error_y=120-face_centre_y

        print('pixelerrorx=',error_x,'valx=',valx)
        print('pixelerrory=',error_y,'valy=',valy)
            
        if(c==1):
            frame=cv2.rectangle(frame,(x,y),(x+w,y+h),(255,0,0),6)

    cv2.imshow('frame',frame) #display image
    
    key = cv2.waitKey(1) & 0xFF
    rawCapture.truncate(0)
    if key == ord("q"):
        break

cv2.destroyAllWindows()
