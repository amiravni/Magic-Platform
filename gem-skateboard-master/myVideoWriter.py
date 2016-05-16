# -*- coding: utf-8 -*-
"""
Created on Mon May 16 19:07:30 2016

@author: root
"""

import cv2
import time
from thread import start_new_thread

class myVideoWriter:
    
    height = -1
    width = -1
    video = None
    camera = None
    capture_flag = False
    
    def init(self,cam_dev,filename):
        if len(filename) < 2:
            print "Error filename is not valid"
            return
            
        self.camera = cv2.VideoCapture(cam_dev)
        if not self.camera.isOpened():
            print "Error opening camera, Try again later or with another camera?"
            self.camera = None
            return
        
        timeout = 5
        tic = time.time()        
        while (time.time() - tic < timeout):
            ret,img = self.camera.read()            
            if ret:
                self.height,self.width = img.shape[:2]
        if self.height == -1 or self.width == -1:
            print "We got camera timeout no image could be grabbed!,Try later or with another camera?"
            return
            
        self.video = cv2.VideoWriter(filename,cv2.cv.CV_FOURCC(*"DIVX"),25,(self.width,self.height),True)

    def start_capture_thread(self):
        while self.capture_flag:
            ret,img = self.camera.read()
            if ret:
                self.video.write(img)
            time.sleep(0.01)

    def startCapture(self):
        self.capture_flag = True
        start_new_thread(self.start_capture_thread,())

    def stopCapture(self):
        self.capture_flag = False
        self.camera.release()
        self.video.release()

