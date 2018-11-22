'''
# Versions
# PA1     First version                                                        09/11/18
# PA2     correct the position of calculate_speed and calculate_acceleration
#         it were using the speed and accelearation with frame_since_seem not
#         updated.                                                             19/11/18
#
Created on 27 de out de 2018

@author: marcelo
'''
import logging
import cv2
import numpy as np

class Ball(object):
    #def __init__(self, id_in, position_in, contour_in):
    def __init__(self):
        self.id = 0 
        self.log = logging.getLogger("ball")
        self.positions = []
        self.speed = []         
        self.acceleration = [] 
        
        #recenter 
        self.recenter_position = (0,0)
        
        self.frames_since_seen = 0
        self.last_frame_number =0

# ============================================================================
# Method improve the speed by a factor
# ============================================================================
    def recenter(self,factor):
        cx, cy = self.last_position
        sx , sy = self.get_speed(-1)
        self.recenter_position = (cx+ factor*sx, cy + factor*sy)
        #return (self.rcx,self.rcy)
        return (self.recenter_position)
        
# ============================================================================
# Method draw polyline of elements
# ============================================================================
    def draw_polyline(self, output_image, keep_n_positions):        
        size_pos = len(self.positions) 
        if (size_pos >= keep_n_positions):
            cv2.polylines(output_image, [np.int32(self.positions)], False, Color.BLACK, 1)
        
        
# ============================================================================
# Method delete the first element of list
# ============================================================================
    def delete_first_position(self, keep_n_positions):        
        if (len(self.positions)== keep_n_positions + 1):
            del self.positions[0]
            del self.acceleration[0]
            del self.speed[0]
        
# ============================================================================
# Method return the last position of centroid
# ============================================================================
    @property
    def last_position(self):
        return self.positions[-1]
# ============================================================================
# Method return the next to last position of centroid
# ============================================================================
    @property
    def next_to_last_position(self):
        if (len(self.positions)>1):
            return self.positions[-2]
        else:
            None
            
            

# ============================================================================
# Method get the position of centroid (x,y)
# ============================================================================
    def get_position(self, index):
        return self.positions[index]
    
# ============================================================================
# Method get the speed of centroid (x,y)
# ============================================================================
    def get_speed(self, index):
        return self.speed[index]
    
# ============================================================================
# Method get the speed of centroid (x,y)
# ============================================================================
    def get_accel(self, index):
        return self.acceleration[index]

# ============================================================================
# Method store the centroid identified in the current frame in the Vehicle 
# object. If n_moving_avg is provided it allow reduce the noise on the
# values of centroid, instead of store the value of current centroid, it is
# stored an average value of centroid.
# Parameters:
# new_position: centroid of ball identified
# frame_counter: current frame counter number
# ============================================================================
    def add_position(self, new_position,frame_counter):                            
        self.id += 1
        self.positions.append(new_position)        

        #self.log.debug("Added centroid: %s, speed: %s, acceleration: %s", 
        #               new_position,
        #               self.speed[-1],
        #               self.acceleration[-1])
        
        if (self.last_frame_number==0):              #insert the first time the frame number
            self.last_frame_number = frame_counter
            self.frames_since_seen = -1              #value undefined yet
        else:
            self.frames_since_seen = frame_counter - self.last_frame_number
            

        self.last_frame_number = frame_counter
        
        self.calculate_speed()           #need to be after update frames_since_seen
        self.calculate_acceleration()    #need to be after update frames_since_seen
        
        self.log.debug("added centroid: %s, number frame centroid last seem: %s.", new_position,
                       self.frames_since_seen)        
        self.log.debug("speed: %s  acc: %s.", self.speed[-1], self.acceleration[-1])


# ============================================================================
# Method to calculate the speed and acceleration
# ============================================================================
    def calculate_speed(self):   # need at least 2 points of position

        if (len(self.positions)>=2):
            x1, y1 = self.last_position             #Frame[0]    
            x0, y0 = self.next_to_last_position     #Frame[-1]
            
            #dx and dy average distance between current and last frame centroid was seem
            #10 is just a empiric value to make the vector visible on the ball
            dx = int((x1 - x0)/self.frames_since_seen)  
            dy = int((y1 - y0)/self.frames_since_seen)       

            
            #remove noise of speed
            dx1,dy1 = self.moving_avg_window((dx,dy), self.speed, 3)           
            self.speed.append((dx1,dy1))

        else:
            self.speed.append((0,0))        #(0,0),(vx,vy)....

# ============================================================================
# Method to calculate the speed and acceleration
# ============================================================================
    def calculate_acceleration(self):   # need at least 2 points of position

        if (len(self.positions)>=3):
            vx_curr, vy_curr = self.speed[-1]             #Frame[0]    
            vx_prev, vy_prev = self.speed[-2]             #Frame[-1]
            
            #dx and dy average distance between current and last frame centroid was seem
            #10 is just a empiric value to make the vector visible on the ball
            acx = int((vx_curr - vx_prev)/self.frames_since_seen)  
            acy = int((vy_curr - vy_prev)/self.frames_since_seen)       

            #acx1,acy1 = self.moving_avg_window((acx,acy), self.acceleration, 3)
            self.acceleration.append((acx,acy))
        else:
            self.acceleration.append((0,0))        #(0,0),(0,0),(ax,ay)....
            

# ============================================================================
# Method plot vectors 
# Parameter:
# output_image 
# color_vector
# source_data: either the last element of speed of accelleration
# factor: if vector too small, integer factor to increase the size of vector
# ============================================================================
    def draw_vectorxy(self,output_image,source_data, factor,colorH, colorV):
        #xcenter, ycenter = self.last_position
        xcenter, ycenter = self.recenter_position
        Pcenter = (xcenter,ycenter)
        
        dx, dy  = source_data
        dx = dx * factor
        dy = dy * factor
        
        #Horizontal component x-axis
        Px = (xcenter + dx, ycenter)
        
        #Vertical component y-axis
        Py = (xcenter, ycenter + dy)
        
        
        #horizontal
        cv2.arrowedLine(output_image, Pcenter, Px, colorH, 4)                
        
        #vertical
        cv2.arrowedLine(output_image, Pcenter, Py, colorV, 4)  
        
        #diagonal
        #End point of Vector 
        #Pxy= (xcenter + dx, ycenter + dy)
        #cv2.arrowedLine(output_image, Pcenter, Pxy , (0, 0, 255), 4)
        
        #rectangle
        #cv2.rectangle(output_image, Pcenter, Pxy,(255,0,0), 2) 


# ============================================================================
# Method calculate the average value among the given lastCentroid and centroid
# stored in the Vehicle object
# n_points = 0 not valid
#            1 result is the own lastCentroid
#            2 result is the average of lastCentroid and position[-1]
#            3 result is the average of lastCentroid, position[-1], position[-2]
#            and so on. 
# ============================================================================
    def moving_avg_window(self, new_point, vector2D, n_points):    
        avg_vector2D = new_point
      
        if ((len(vector2D) >= n_points-1) and n_points!= 0):        
            for i in range(1,n_points):    
                avg_vector2D= np.add(vector2D[-i], avg_vector2D)            
            avg_vector2D = np.divide(avg_vector2D,n_points)
            avg_vector2D = (int(avg_vector2D[0]), int(avg_vector2D[1]))                
        
        return avg_vector2D


# ============================================================================
    def draw_rectangle_centroid(self, fr, radius): 
        xc,yc = self.recenter_position
        cv2.rectangle(fr, (xc-radius,yc-radius), (xc+radius, yc+radius) ,Color.ORANGE, 2) 

# ============================================================================

class Color():
    NAVY  = (255,0,0)
    LBLUE = (255,204,153)
    GREEN = (0,204,0)
    LGREEN = (153,255,204)
    
    RED   = (0,0,255)
    YELLOW= (0,255,255)
    PURPLE= (153,0,153)
    ORANGE= (51,153,255)
    CYAN  = (204,204,0)
    BLACK = (0,0,0)
    
    
    GREEN_DARK = (29, 86, 6)      
    GREEN_LIGHT= (64, 255, 255) 
    
    RED_DARK  = (153,76,0)    
    RED_LIGHT = (255,153,153)

