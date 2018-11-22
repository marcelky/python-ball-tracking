# python-ball-tracking
Track green ball and add speed/accel vector on its center and real time graphs

# Configuration
Implemented and tested with:

Ubuntu 16.04

Opencv 4.0 Alpha

Python 3.5

(some tests done on windows's python without need any change on script)

# Overview
This script tracks a ball and over the center of ball draw speed and 
acceleration color vectors. In addition these data can be seem on real
time on graphs along the movement of ball.
Detection of ball based on blog: www.pyimagesearch.com

# Description
  This script tracks a green ball seem on webcam or video file. The ball once 
detected, will have an small black circle created on an gray frame output, 
this position is called centroid.
  The movement of ball then can be seem looking at this black centroid, since
we are using video input or webcam, the movement of ball will registered in 
different frames at different positions in the frame. This different of 
position in different frames is the distance covered by the ball between frames, 
in this script it is called as delta x (dx) and delta y (dy). dx is the distance 
covered horizontally and dy covered vertically.

  Since the time between frames are fixed, Tf, the average speed can be 
calculated as:
    speed horizontal : Vx= dx/Tf      
    speed vertical   : Vy= dy/Tf
  To make simple we assume Vx is direct proportional to dx and Vy proportional to dy. 
    Vx ~ dx and Vy ~ dy

  Acceleration is variation of speed, and based on the assumption above,  
we calculate the acceleration using:
    Acx = Vx[current] - Vx[last] 
    Acy = Vy[current] - Vy[last] 

  With these values V and Ac calculated it is used to put it as vector size 
on centroid.
 
Notes ball moving: 

left to right : Vx positive

right to left : Vx negative

Up to down    : Vy positive

Down to up    : Vy negative

*Acelleration follow the same sign rules

# Extra command:
when selected with mouse the output frame video/webcam type:  

"q" to quit the execution

"s" toggle a orange square around the tracked ball

# USAGE

Command:     python ball_tracking.py

Parameters:  

fps       = number of frame per seconds to configure the system. 
            optional. default 30. only applied when using webcam.
            
factor    = integer, increase the speed of centroid on the screen position. 
            optional. default 0
            0 does not change the position of centroid
            1 add once (dx,dy) 
            2 add twice (dx,dy) and so on
            (dx,dy) is the last distance covered in from last frame till 
            current frame
            
inter     = float, percentage of original frame we are interested. Measured 
            from left to right 
            side of frame
            1   :100% of original frame saved for processing 
            0.5 :50% of frame (left side) is our interested area         
            
video     = name of video file *.avi, *mp4. 
            optional. default none 

# Examples
ex1: this tracking a ball capture the frames from default webcam 

    python ball_tracking.py
        

ex2: this tracking a ball setting the webcam to capture. Confirm at beginning of log if configuration was really accepted.

    python ball_tracking.py --fps 60

ex3: this command start the script to read frames from webcam and and speed up the ball centroid (red circle) by 2x

    python ball_tracking.py --factor 2

ex4: this tracking a ball using video file  

    python ball_tracking.py --video ball_tracking_example.mp4
        

ex5: this tracking a ball using webcam, only 50% of frame is our interested area (left side of frame)

    python ball_tracking.py --inter 0.5

# CONFIGURATION SETTINGS IN ball_tracking.py file
True - it saves a log debug.log in current directory, False - disable logging to file. 
  LOG_TO_FILE = True    

True - Include grid on output, False - disable grid
  GRID = True

True - plot animated graph of Speed and acceleration, False - plot graph is not executed
  PLOT_SPEED_ACC = True
 
True - Show original frame captured by webcam or video, False the original frame of 
webcam/video is not displayed
  SHOW_ORIG = True
