'''
Created on 2 de nov de 2018

@author: marcelo
Based on pyimage site
'''
# import the necessary packages
from threading import Thread
import cv2
from cv2 import CAP_PROP_FPS
import logging.handlers
 
class WebcamVideoStream1():
    def __init__(self, src=0):
        # initialize the video camera stream and read the first frame
        # from the stream
        self.log = logging.getLogger("WebcamVideoStream1")
        self.stream = cv2.VideoCapture(src)
        (self.grabbed, self.frame) = self.stream.read()
 
        # initialize the variable used to indicate if the thread should
        # be stopped
        self.stopped = False
    
    def start(self):
        # start the thread to read frames from the video stream
        Thread(target=self.update, args=()).start()
        return self
 
    def setFPS(self,fps):
        #cv2.CAP_PROP_FPS = fps
        #cv2.CAP_PROP_FPS = fps
        self.log.debug("Current fps: %s", self.stream.get(cv2.CAP_PROP_FPS))   
        self.log.debug("Try to set fps: %s", fps)     
        self.stream.set(cv2.CAP_PROP_FPS, fps)
        self.log.debug("Current new fps: %s", self.stream.get(cv2.CAP_PROP_FPS))
 
    def update(self):
        # keep looping infinitely until the thread is stopped
        self.log.info("sampling THREADED frames from webcam...")
        
        while True:
            # if the thread indicator variable is set, stop the thread
            if self.stopped:
                return
 
            # otherwise, read the next frame from the stream
            (self.grabbed, self.frame) = self.stream.read()
 
    def read(self):
        # return the frame most recently read
        return self.frame
 
    def stop(self):
        # indicate that the thread should be stopped
        self.stopped = True        