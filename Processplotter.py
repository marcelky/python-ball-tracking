'''
# Versions
# PA1     First version (linux)                                     09/11/18
# PA2     This version is compatible with linux and Windows         13/11/18
#         The plotter did not work with spawn so had to instantiate
#         the button object outside of _init_ of ProcessPlotter2.            
#         The button object is not pickable so must stay out of _init_
'''


'''
Created on 31 de out de 2018

@author: marcelo
'''
#10944621

import multiprocessing as mp
import time
import matplotlib.pyplot as plt
import numpy as np
from multiprocessing import freeze_support

#from multiprocessing.managers import BaseManager
from matplotlib.widgets import Button

# Fixing random state for reproducibility
np.random.seed(19680801)


class ColorPlot():
    NAVY  = '#0000FF'
    LBLUE = '#99CCFF'
    GREEN = '#00CC00'
    LGREEN ='#CCFF99'
    
    RED   = '#FF0000'
    YELLOW= '#FFFF00'
    PURPLE= '#990099'
    ORANGE= '#FF9933'
    CYAN  = '#00CCCC'
    BLACK = '#000000'


# ============================================================================
# Class create buttons on graphs
# ============================================================================

class Button_index(object):    
    def __init__(self):
        self.ax_pause    = plt.axes([0.7, 0.02, 0.09, 0.025])   #[left, bottom, width, height]
        self.ax_play     = plt.axes([0.81, 0.02, 0.09, 0.025])       
        
        self.b_pause = Button(self.ax_pause, 'Pause')
        self.b_play = Button(self.ax_play, 'Play')

        self.play_state = True                    #keep animating the graph       
        self.b_pause.color = ColorPlot.GREEN
        self.b_play.color = ColorPlot.RED
        

    def pause(self,event):
        self.play_state = False
        self.b_pause.color = ColorPlot.RED
        self.b_pause.ax.set_facecolor(ColorPlot.RED)
        self.b_play.color = ColorPlot.GREEN
        self.b_play.ax.set_facecolor(ColorPlot.GREEN)        
    
    def play(self,event):
        self.play_state = True
        self.b_pause.color = ColorPlot.GREEN
        self.b_play.color = ColorPlot.RED

# ============================================================================
# Class which read the input data and update the plot data every second
# ============================================================================
class ProcessPlotter2(object):
    def __init__(self):
       
        self.fig = plt.figure('Plotting Area',figsize=(6,8))
        self.ax1, self.ax2  = self.fig.subplots(2,1,sharex=True)
        
        self.ax1.set_title('Speed',color=ColorPlot.RED)
        self.ax1.set_ylabel('[pixel/T]', color=ColorPlot.RED)
        
        self.ax2.set_title('Acceleration',color=ColorPlot.RED)
        self.ax2.set_ylabel('[pixel/T^2]', color=ColorPlot.RED)
        self.ax2.set_xlabel('Frame',color=ColorPlot.RED)
        
        self.lines11, = self.ax1.plot([],[],label='Vx',color=ColorPlot.NAVY)
        self.lines12, = self.ax1.plot([],[],label='Vy',color=ColorPlot.RED)
        self.ax1.legend()
        
        self.lines21, = self.ax2.plot([],[],label='ϒx',color=ColorPlot.PURPLE)
        self.lines22, = self.ax2.plot([],[],label='ϒy',color=ColorPlot.CYAN)
        self.ax2.legend()
        
        self.ax1.grid()
        self.ax2.grid()
        
        self.plotter_buttons = None
        self.draw_frame = True
        
        self.x = []
        self.yh = []
        self.yv = []
        
        self.ach = []
        self.acv = []
        self.xindex = 0

# ============================================================================
    def terminate(self):
        plt.close('all')
        
# ============================================================================
    def call_back(self):

        print("call_back")
        if (self.plotter_buttons is None):
            self.plotter_buttons = Button_index()
        #check state of buttons
        else:
            self.plotter_buttons.b_play.on_clicked(self.plotter_buttons.play)
            self.plotter_buttons.b_pause.on_clicked(self.plotter_buttons.pause)        
            self.draw_frame = self.plotter_buttons.play_state               
            print("self.draw_frame", self.draw_frame)           

        if(len(self.x)==100):
            del self.x[:]
            del self.yh[:]
            del self.yv[:]
            
            del self.ach[:]
            del self.acv[:]
        
        while self.pipe.poll():
            command = self.pipe.recv()
            if command is None:
                self.terminate()
                return False
            else:
                #save data received from pipe
                self.x.append(self.xindex)
                self.yh.append(command[0])
                self.yv.append(command[1])
                self.ach.append(command[2])
                self.acv.append(command[3])
                
                #update the speed data
                self.lines11.set_xdata(self.x)
                self.lines11.set_ydata(self.yh)
                self.lines12.set_xdata(self.x)
                self.lines12.set_ydata(self.yv)                
                self.ax1.relim()
                self.ax1.set_xlim(max(0,self.xindex-100),max(100,self.xindex))
                self.ax1.autoscale_view()
                
                #updata acceleration data
                self.lines21.set_xdata(self.x)
                self.lines21.set_ydata(self.ach)
                self.lines22.set_xdata(self.x)
                self.lines22.set_ydata(self.acv)
                self.ax2.relim()
                self.ax2.set_xlim(max(0,self.xindex-100),max(100,self.xindex))
                self.ax2.autoscale_view()
                
                #counter to indicate position of current element
                self.xindex += 1
        
        if(self.draw_frame):  #condition to pause the print for awhile
            self.fig.canvas.draw()
            self.fig.canvas.flush_events()

        
        return True
# ============================================================================
    def __call__(self, pipe):
        print('starting plotter...')
                
        self.pipe = pipe
        #self.play_pause = pl_buttons
        
        timer = self.fig.canvas.new_timer(interval=1000)
        timer.add_callback(self.call_back)
        timer.start()
 
        print('...done')
        plt.show()


# ============================================================================
# Class that create a process and generate the data to be printed
# ============================================================================
class NBPlot1(object):
    def __init__(self):
        
        #Process of Plotter
        self.plot_pipe, self.plotter_pipe = mp.Pipe()                #plot_pipe (parent), plotter_pipe(child)
        self.plotter = ProcessPlotter2()                         

        self.plot_process = mp.Process(target=self.plotter,          #pointer of object ProcessPlotter
                                        args=(self.plotter_pipe,),   #object buttons, OS windows does not allow to forking, need share resource explicitly
                                        daemon=True)         
        self.plot_process.start()
        
# ============================================================================
# Parameters:
# data: data0 = speedx
#       data1 = speedy
#       data2 = accelerationx
#       data3 = accelerationy

    def plot(self, data, finished=False):

        send = self.plot_pipe.send                
        if finished:
            send(None)
        else:            
            send(data)
# ============================================================================

def main():
    #example how to use it     
    pl = NBPlot1()
    a=np.arange(200,300)
    b=np.arange(100)
    
    for i in b:
        pl.plot([a[i],b[i],a[i],b[i]])
        time.sleep(1)
    pl.plot(finished=True)


if __name__ == '__main__':
    from sys import platform as _platform
    freeze_support()
    
    if _platform == "linux" or _platform == "linux2":
        mp.set_start_method("fork")
    elif _platform == "darwin":  #darwin MAC OS X
        mp.set_start_method("forkserver")
    elif _platform == "win32" or _platform == "win64":
        mp.set_start_method("spawn")        
    
    main()
