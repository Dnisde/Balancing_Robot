#!/usr/bin/env python3
from picamera2 import Picamera2
from imutils.video import FPS
from threading import Thread
import argparse
import asyncio
import serial # Module needed for serial communication
import time # Module needed to add delays in the code
import cv2


class Object_Recognition:

    def __init__(self):

        cv2.startWindowThread()

        # construct the argument parser and parse the arguments
        self.ap = argparse.ArgumentParser()

        # Run the and Loop the face_recognition application
        self.face_cascade = cv2.CascadeClassifier('./haarcascade_frontalface_default.xml')

        # Initialize global parameters.
        self.width, self.height = 1000, 500
        self.x, self.y, self.w, self.h = 0, 0, 0, 0

        self.error_x, self.valx, self.error_y, self.valy = 0.0, 0.0, 0.0, 0.0

        self.Px, self.Ix, self.Dx = -1/160, 0, 0
        self.Py, self.Iy, self.Dy = -0.2/120, 0, 0

        self.threshold = 0.5
        self.instruction = 6
         
        #initialize some other required vaqriables for PID controller Calculation:
        self.integral_x, self.integral_y = 0, 0
        self.differential_x, self.differential_y = 0, 0
        self.prev_x, self.prev_y = 0, 0

        # Initialize Camera:
        self.camera = Picamera2()

        # Initialize Time Counter:
        self.fps = FPS()
        self.detected = False
        self.finished = False

        # Initialize Serial
        self.ser = serial.Serial('/dev/ttyACM0', 9600, timeout=1)


    def intialize(self):
        # Camera Settings: 
        self.camera.resolution = (self.width, self.height)
        self.camera.framerate = 30
        self.camera.configure(self.camera.create_preview_configuration(main={"size": (self.width, self.height)}))

        # Warm up Raspi Camera: 
        self.camera.start()
        time.sleep(1)

        # Get rid of garbage/incomplete data
        self.ser.reset_input_buffer()
        self.ser.flush()
        self.fps.start()


    async def start_recognize(self):

        while True:

            # Read frame by each stream in nano seconds.
            frame = self.camera.capture_array()

            # Flip the frame by opposite way to 
            frame = cv2.flip(frame,1)

            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB) 
            faces = self.face_cascade.detectMultiScale(rgb,1.3,5)

            self.detected = False
            self.finished = False

            # Extract the face rectangle from each frame of video (.per ts), 
            # Get the face position of the detected face(If detected), and record that coordinate: x,y,w,h
            for(x,y,w,h) in faces:
                self.x = x
                self.y = y
                self.w = w
                self.h = h
                self.detected = True
                self.instruction = 0
                break

            if (self.detected):
                # Central of the face:
                #   Coordiante in X: position of Most.Left + 1/2 * Width of the frame
                #   Coordiante in Y: position of Most.Top  + 1/2 * Height of the frame

                face_centre_x = self.x + self.w / 2
                face_centre_y = self.y + self.h / 2

                # Amount of pixels to move 
                self.error_x = (self.width / 2) - face_centre_x

                self.error_y = (self.height / 2) - face_centre_y
                
                self.integral_x = self.integral_x + self.error_x
                self.integral_y = self.integral_y + self.error_y
                 
                self.differential_x = self.prev_x - self.error_x
                self.differential_y = self.prev_y - self.error_y
                 
                self.prev_x = self.error_x
                self.prev_y = self.error_y

                self.valx = self.Px * self.error_x + self.Dx * self.differential_x + self.Ix * self.integral_x
                self.valy = self.Py * self.error_y + self.Dy * self.differential_y + self.Iy * self.integral_y
                
                # Round off to 2 decimel points.
                self.valx = round(self.valx,2) 
                self.valy = round(self.valy,2)

                # if abs(self.error_x) < 20:
                #     self.instruction = 0;

                # else:
                #     # Left is negative, Right is positive.
                #     if abs(self.valx) > 0.5:
                #         sign = self.valx / abs(self.valx)
                #         self.valx = 0.5 * sign
                #         if self.valx < 0:
                #             self.instruction = 5
                #         else if(self.valx > 0):
                #             self.instruction = 4

                #     self.instruction = self.valx
                 
                # if abs(error_y) < 20:
                #     self.instruction = 0

                # else:
                #     if abs(valy) > 0.5:
                #         sign = valy / abs(valy)
                #         valy = 0.5 * sign

                #     self.instruction = valy

                # Left: Value is too negative.
                if (self.valx <= -self.threshold):
                    # Turn slightly left:
                    self.instruction = 5

                # Right: Value is too positive.
                elif (self.valx >= self.threshold):
                    # Turn slightly right:
                    self.instruction = 4

                # Middle: Go straight following by default or do nothing.
                else:
                    self.instruction = 6

                self.finished = True
            

                frame = cv2.rectangle(frame,(x,y),(self.x + self.w, self.y + self.h),(255, 0, 0), 6)
                # cv2.putText(frame, "Default_Object", (left, y), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (0, 255, 0), 2)


            if(self.finished == True):
                await self.sendTO_Arduino(0.5)
                # print(f"PixelErrorx={self.error_x}, {self.valx}\n")

                
            cv2.imshow('frame',frame) #display image

            key = cv2.waitKey(1) & 0xFF
            if key == ord("q"):
                return
        
        cv2.destroyAllWindows()

    
    async def sendTO_Arduino(self, delay):

        self.ser.flush();

        send_Xerror = (f"{self.instruction}\n")
        # send_Xerror = (f"PixelErrorx={self.error_x}, {self.valx}\n")
        # send_Yerror = (f"PixelErrory={self.error_y}, {self.valy}\n")

        # Send the string. Make sure you encode it before you send it to the Arduino.
        self.ser.write(send_Xerror.encode('utf-8'))
        # self.ser.write(send_Yerror)

        # DEBUG only: 
        # Receive data from the Arduino
        receive_string = self.ser.readline().decode('utf-8').rstrip()

        # Print the data received from Arduino to the terminal
        print(receive_string)

        # Do nothing for 10 milliseconds (0.01 seconds)
        time.sleep(delay)


    def main(self):
        self.intialize()
        asyncio.run(self.start_recognize())


new_object = Object_Recognition()
new_object.main()