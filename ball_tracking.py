'''
# Versions
# PA1     First version                                      09/11/18
# PA2     Try to fix multiprocessing crash                   11/11/18
# PA3     change color green Vector and line graph to red    12/11/18
          add "s" to draw square remove import log of 
          Processplotter
# PA4     Add conditions at (if _main_) to configure type of 13/11/18
          process to create based on the OS.
# ============================================================================
# Overview
# This script tracks a ball and over the center of ball draw speed and 
# acceleration color vectors. In addition these data can be seem on real
# time on graphs along the movement of ball.
# Detection of ball based on blog: www.pyimagesearch.com
#
#
# Description
# This script tracks a green ball seem on webcam or video file. The ball once 
# detected, will have an small black circle created on an gray frame output, 
# this position is called centroid.
# The movement of ball then can be seem looking at this black centroid, since
# we are using video input or webcam, the movement of ball will registered in 
# different frames at different positions in the frame. This different of 
# position in different frames is the distance covered by the ball between frames, 
# in this script it is called as delta x (dx) and delta y (dy). dx is the distance 
# covered horizontally and dy covered vertically.
#
# Since the time between frames are fixed, Tf, the average speed can be 
# calculated as:
#     speed horizontal : Vx= dx/Tf      
#     speed vertical   : Vy= dy/Tf
# To make simple we assume Vx is direct proportional to dx and Vy proportional 
# to dy. 
#     Vx ~ dx and Vy ~ dy
#
# Acceleration is variation of speed, and based on the assumption above,  
# we calculate the acceleration using:
#     Acx = Vx[current] - Vx[last] 
#     Acy = Vy[current] - Vy[last] 
#
# With these values V and Ac calculated it is used to put it as vector size 
# on centroid.
# 
# Notes ball moving left to right : Vx positive
#                   right to left : Vx negative
#                   Up to down    : Vy positive
#                   Down to up    : Vy negative
#                   *Acelleration follow the same sign rules
#
# Extra command:
# when selected with mouse the output frame video/webcam type:  
# "q" to quit the execution
# "s" to display an orange square around the tracked ball (green)
# ============================================================================
# USAGE
#
# Command:     python ball_tracking.py
# 
# Parameters:  
#
# fps       = number of frame per seconds to configure the system. 
#             optional. default 30. only applied when using webcam.
#
# factor    = integer, increase the speed of centroid on the screen position. 
#             optional. default 0
#             0 does not change the position of centroid
#             1 add once (dx,dy) 
#             2 add twice (dx,dy) and so on
#             (dx,dy) is the last distance covered in from last frame till 
              current frame
#
# inter     = float, percentage of original frame we are interested. Measured 
#             from left to right 
#             side of frame
#             1   :100% of original frame saved for processing 
#             0.5 :50% of frame (left side) is our interested area         
# video     = name of video file *.avi, *mp4. 
#             optional. default none 
#
# example1:
#
#     python ball_tracking.py
#         this tracking a ball capture the frames from default webcam 
#
# example2:
#     python ball_tracking.py --fps 60
#         this tracking a ball setting the webcam to capture. Confirm at 
        beginning of log if configuration was really accepted.
#
# example3:
#     python ball_tracking.py --factor 2
#        this command start the script to read frames from webcam and and speed 
      up the ball centroid (red circle) by 2x
#
# example4: 
#     python ball_tracking.py --video ball_tracking_example.mp4
#         this tracking a ball using video file  
#
# example5:
#     python ball_tracking.py --inter
#         this tracking a ball using webcam, only 50% of frame is our interested 
#          area (left side of frame)
#
# ============================================================================
'''
from cv2 import imshow
'''#CONFIGURATION'''
#True - it saves a log debug.log in current directory                     
LOG_TO_FILE = True    

#True - Include grid on output, False - disable grid
GRID = True

#True - plot animated graph of Speed and acceleration, False - plot graph is not executed
PLOT_SPEED_ACC = True

#True - Show original frame captured by webcam or video, False the original frame of 
#webcam/video is not displayed
SHOW_ORIG = True


'''# ============================================================================'''
import numpy as np
import argparse
import cv2
import imutils
import time
import logging.handlers
import sys
from multiprocessing import freeze_support
import multiprocessing as mp

#private classes
from WebcamVideoStream import WebcamVideoStream1
from Ball import Ball
from Processplotter import NBPlot1
from Ball import Color
'''# ============================================================================'''


# define the lower and upper boundaries of the "green"
# ball in the HSV color space, then initialize the (RGB)
colorLower = Color.GREEN_DARK      #darker color  
colorUpper = Color.GREEN_LIGHT     #lighter color




def init_logging():
    main_logger = logging.getLogger()
    
    formatter = logging.Formatter(
        fmt='%(asctime)s.%(msecs)03d %(levelname)-8s [%(name)s] %(message)s'
        , datefmt='%Y-%m-%d %H:%M:%S')

    handler_stream = logging.StreamHandler(sys.stdout)
    handler_stream.setFormatter(formatter)
    main_logger.addHandler(handler_stream)

    if LOG_TO_FILE:
        handler_file = logging.handlers.RotatingFileHandler("debug.log"
            , maxBytes = 2**24
            , backupCount = 10)
        handler_file.setFormatter(formatter)
        main_logger.addHandler(handler_file)

    main_logger.setLevel(logging.DEBUG)    
    #main_logger.setLevel(logging.WARNING)
    #main_logger.setLevel(logging.INFO)
    #main_logger.setLevel(logging.CRITICAL)
    #main_logger.setLevel(logging.FATAL)

        

    return main_logger


# ============================================================================
def filter_image(frame, colorLight, colorDeep, useGPU = False):
    
    if (useGPU): #webcam
        blurred = cv2.GaussianBlur(cv2.UMat(frame), (11, 11), 0)
        imshow("gaussian",blurred)        
        hsv = cv2.cvtColor(cv2.UMat(blurred), cv2.COLOR_BGR2HSV)  
        imshow("cvt", hsv)      
        mask = cv2.inRange(cv2.UMat(hsv), colorLight, colorDeep) 
        imshow("range", mask);       
        mask = cv2.erode(cv2.UMat(mask), None, iterations=2)        
        mask = cv2.dilate(cv2.UMat(mask), None, iterations=2)        
        cnts = cv2.findContours(cv2.UMat(mask), cv2.RETR_EXTERNAL,
                                         cv2.CHAIN_APPROX_SIMPLE)    
    else:  #video
        blurred = cv2.GaussianBlur(frame, (11, 11), 0)
        hsv = cv2.cvtColor(blurred, cv2.COLOR_BGR2HSV)
        mask = cv2.inRange(hsv, colorLight, colorDeep)
        mask = cv2.erode(mask, None, iterations=2)
        mask = cv2.dilate(mask, None, iterations=2)
        cnts = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL,
                                 cv2.CHAIN_APPROX_SIMPLE)
    return cnts 


# ============================================================================
#This method is used to mask right side of frame
'''
All this green rectangle is capture by webcam camera
But only the A is part to be tracked. This B area will be ignored
during the tracking process.

          **********************************
          *      A         *        B      *       
          * interested     *     masked    *
          * area to track. *     black     *
          * e.g.           *               *
          * pendulum       *               *
          *                *               *
          **********************************
          <---fr_w_inter--->
'''
# Parameters:
# fr = frame to output image
# fr_h_inter = height of frame we are interested
# fr_w_inter = width of frame we are interested

def crop_interest_area(fr, fr_h_inter, fr_w_inter):
    interest_area = np.zeros((fr_h_inter,fr_w_inter,3), np.uint8)
    interest_area[0:fr_h_inter, 0: fr_w_inter] = fr[0:fr_h_inter, 0: fr_w_inter]
    return interest_area

# ============================================================================
# Method to create grid in the output blanked frame
# default grid size is 80pixels
def make_grid(fr,hg,wd):
    step=80
    
    #write line
    for r in np.arange(step,hg,step,np.uint16):
        cv2.line(fr,(0, r), (wd,r),  (0,0,0), 1)

    #write column
    for c in np.arange(step, wd, step, np.uint16):
        cv2.line(fr,(c, 0), (c,hg),  (0,0,0), 1)



# ============================================================================
def main():
    # construct the argument parse and parse the arguments
    ap = argparse.ArgumentParser()
    ap.add_argument("-v", "--video",
        help="path to the (optional) video file")

    ap.add_argument("-t", "--factor", type=int, default=0,
        help="factor (optional) increase speed")

    ap.add_argument("-i", "--inter", type=float, default=1,
        help="percentage of width (optional)")
    
    ap.add_argument("-f", "--fps", type=int, default=30,
        help="fps frame per second (optional)")
    
#     ap.add_argument("-b", "--buffer", type=int, default=64,
#         help="max buffer size")
    args = vars(ap.parse_args())
    
    #Setup the size of interest area. This is the area where ball will be tracked
    INTER_WIDTH = int((args["inter"])*640)
    INTER_HEIGHT = 480    
    log.debug("INTER_WIDTH: %s, INTER_HEIGHT: %s", INTER_WIDTH, INTER_HEIGHT)
    
    
    #pts = deque(maxlen=args["buffer"])
    
    # if a video path was not supplied, grab the reference
    # to the webcam    
    if not args.get("video", False):
        #thread to read the camera
        camera = WebcamVideoStream1(src=0).start()        
        camera.setFPS(args["fps"])
        time.sleep(2.0)
        for i in range(0, 50):
            frame = cv2.UMat(camera.read())
        #changing the sampling size
        frame = cv2.resize(frame,(640,480))
    else:
        camera = cv2.VideoCapture(args["video"])
    
        for i in range(0, 20):
            frame = camera.read()

        #changing the sampling size
        camera.set(cv2.CAP_PROP_FRAME_HEIGHT,480)
        camera.set(cv2.CAP_PROP_FRAME_WIDTH,640)
        
    # allow the camera or video file to warm up
    time.sleep(2.0)
    
    # Define the codec and create VideoWriter object
    fourcc = cv2.VideoWriter_fourcc(*'XVID')
    # save frame with smaller frame size
    out = cv2.VideoWriter('output.avi',fourcc, 30.0, (320,240))#640,480))

    
    green_ball = Ball()
    
#     if(PLOT_SPEED_ACC):
#         speed_plot_process = NBPlot1()

    syncON = False
    
    frame_counter = -1
    
    '''
    ****************************************************************************
    # keep looping
    ****************************************************************************
    '''
    while True:

        
        
        #start measure the processing time of frame
        e1 = cv2.getTickCount()                
        frame_counter += 1
        
        
        ''' *************Frame capture part****************************'''    
        frame = camera.read()       
        # handle the frame from VideoCapture or VideoStream
        # webcam frame = frame[1]
        # video  frame = frame
        frame = frame[1] if args.get("video", False) else frame

        #store full frame image
        orig_full_frame =frame        #store full frame                      
        cv2.line(orig_full_frame,(INTER_WIDTH, 0), (INTER_WIDTH,INTER_HEIGHT),  Color.BLACK, 2)
        
        #store interested area, only half left
        frame= crop_interest_area(frame, INTER_HEIGHT, INTER_WIDTH) 
        
        #store the interested area but only as gray frame
        blank_frame = np.full((INTER_HEIGHT,INTER_WIDTH,3), 125 ,np.uint8)
        if(GRID):
            make_grid(blank_frame, INTER_HEIGHT, INTER_WIDTH)        
        
        # if we are viewing a video and we did not grab a frame,
        # then we have reached the end of the video
        if frame is None:
            log.debug("Frame processing None.")
            break

        
        ''' *************End of capture part****************************'''
 
        if args.get("video", True):                        
            cnts = filter_image(frame, colorLower, colorUpper)
        else:
            cnts = filter_image(cv2.UMat(frame), colorLower, colorUpper,True)
    
        cnts = cnts[0] if imutils.is_cv2() else cnts[1]
        center = None
    
        # only proceed if at least one contour was found
        if len(cnts) > 0:
            # find the largest contour in the mask, then use
            # it to compute the minimum enclosing circle and
            # centroid
            c = max(cnts, key=cv2.contourArea)
            ((x, y), radius) = cv2.minEnclosingCircle(c)
            M = cv2.moments(c)
            center = (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))
    
            # only proceed if the radius meets a minimum size
            if radius > 10:
                #save the original position in a list (it will be used to calculate speed/acceleration
                green_ball.add_position(center, frame_counter)
                
                
                #get the latest speed to plot
                speedH,speedV = green_ball.get_speed(-1)
                accH,accV = green_ball.get_accel(-1)
                                
                #draw graphic
                if(PLOT_SPEED_ACC):
                    speed_plot_process.plot((speedH,speedV,accH,accV))
                
                
                #This method try to reduce the lagging adding dx/dy (speed) to current ball location
                #it saves in green_ball.recenter_position
                green_ball.recenter(args["factor"])
                
                
                #draw original center for debugging
                #cv2.circle(blank_frame, center, int(radius),(255, 255, 255), 2)                
                #cv2.circle(blank_frame, center, 5, (255, 255, 255), 5)                
                
                
                # draw the circle and centroid on the frame,
                cv2.circle(blank_frame, green_ball.recenter_position, int(radius),Color.BLACK, 1)                
                cv2.circle(blank_frame, green_ball.recenter_position, 5, Color.BLACK, 1)


                #draw rectangle on ball
                key = cv2.waitKey(1) & 0xFF
                if (key == ord("s")):
                    if(syncON):
                        syncON=False
                    else:
                        syncON=True
                
                if (syncON):
                    green_ball.draw_rectangle_centroid(blank_frame, int(radius))
                    
                
                
                #frame original
                if (SHOW_ORIG):
                    cv2.circle(orig_full_frame, green_ball.recenter_position, int(radius),Color.BLACK, 1)
                    cv2.circle(orig_full_frame, green_ball.recenter_position, 5, Color.BLACK, 1)
                
                

        green_ball.draw_polyline(blank_frame, 10)
            
        if(len(green_ball.positions)>= 3):                        
            green_ball.draw_vectorxy(blank_frame, green_ball.speed[-1], 15, Color.NAVY, Color.RED)
            green_ball.draw_vectorxy(blank_frame, green_ball.acceleration[-1], 15, Color.PURPLE, Color.CYAN)
            green_ball.delete_first_position(50)
    
        #save frame to file
        out.write(blank_frame)
        
        # show the frame to our screen
        cv2.imshow("Tracking Area", blank_frame)
        if(SHOW_ORIG):
            cv2.imshow("Original full frame", orig_full_frame)
            #cv2.imshow("Interest area", frame)

        time_exec = (cv2.getTickCount() - e1)/cv2.getTickFrequency()
        log.debug("Frame processing time %f [s] and frequency %d [Hz].", time_exec, 1/time_exec)

        key = cv2.waitKey(1) & 0xFF
    
        # if the 'q' key is pressed, stop the loop
        if key == ord("q"):
            break
    
        
    #save frame to file at same reading speed
    #out.write(frame)
    
    if(PLOT_SPEED_ACC):
        speed_plot_process.plot(1,finished=True)
        
    
    # if we are not using a video file, stop the camera video stream
    if not args.get("video", False):
        camera.stop()
        out.release()
    
    # otherwise, release the camera
    else:
        camera.release()
        out.release()
    
    # close all windows
    cv2.destroyAllWindows()
    
# ============================================================================

if __name__ == "__main__":
    #start the logging configuration
    log = init_logging()  
    if(PLOT_SPEED_ACC):

        freeze_support()

        from sys import platform as _platform
        if _platform == "linux" or _platform == "linux2":
            mp.set_start_method("fork")
        elif _platform == "darwin":  #darwin MAC OS X
            mp.set_start_method("forkserver")
        elif _platform == "win32" or _platform == "win64":
            mp.set_start_method("spawn")        

        speed_plot_process = NBPlot1() 

    main()    
