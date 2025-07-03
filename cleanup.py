# -*- coding: utf-8 -*-
"""
Created on Tue Nov  5 12:33:08 2024

@author: KDVLabFerro
"""
from pylablib.devices import Thorlabs # import the device libraries
from pylablib.devices import uc480
import pandas as pd
#import numpy as np # import numpy for saving
import matplotlib.pyplot as plt
#from pylablib.devices import uc480
import numpy as np
from PIL import Image
import time
import os
import serial



def cleanup(vel,imax):
         x=(df-d0)/imax
         stage.setup_velocity(min_velocity= 0, acceleration=acc*scale1,max_velocity =vel*scale1) 
         ser.write(('1VA'+str(vel*0.001)+'\r').encode())
         
         for i in range (1,imax,2):
             print(i)
             stage.move_to(right)
             stage.wait_move()
             ser.write(('1PA'+str(df-i*x)+'\r').encode())
             if i==1:
                 time.sleep(int(((df-d0)*1000)/vel))
             time.sleep(int(x*1000/vel))
             stage.move_to(left)
             stage.wait_move()
             ser.write(('1PA'+str(df-(i+1)*x)+'\r').encode())
             time.sleep(int(x/vel))
             print('done '+ str (i) + 'of ' + str(imax) )
                 
         ser.write(('1PA'+str(d0)+'\r').encode())#move 1/10 up
         time.sleep(int((x*1000)/vel))
         stage.setup_velocity(min_velocity= 0, acceleration=acc*scale1,max_velocity =fast*scale1)
         stage.move_to(x0)
         stage.wait_move()

         time.sleep(relax)
         return   
     
        
     


ser = serial.Serial(
                    port = 'COM3',
                    baudrate=19200,
                    bytesize=serial.EIGHTBITS,
                    parity = serial.PARITY_NONE,
                    stopbits = serial.STOPBITS_ONE,
                    timeout = 2)

stage = Thorlabs.KinesisMotor("27261341")
#%%
###IN ORDER TO MOVE CAMERA AND RUN AGAIN> CHANGE D0 ans X0 TO BE CONSTANTS
x0= float(stage.get_position())
ser.write("1TP\r".encode())
d0 = float(ser.readline().decode().strip()) 
#d0=2.97469
d=d0



#directory = 'C:/Users/KDVLabFerro/Desktop/Data/oct 6/'
directory = 'G:/Experiments/nov 4/'
df= d0 + 2000*0.001
acc=2500
ser.write(('1AC'+str(acc*0.001)+'\r').encode())
fast=50
fps = 5
scale1=34.555
relax=20
drp=75
left=x0+1300*scale1
right =x0-1300*scale1
'''
cam = uc480.UC480Camera()
cam.set_exposure(3E-4)
cam.set_gains(0,0,0,0)
cam.set_frame_period(1/fps)
frame = [cam.snap(), 0]

'''
stage.setup_jog(step_size=drp*scale1, min_velocity=None, acceleration=acc*scale1, max_velocity=None,
stop_mode=None, channel=None)
ser.write(('1AC'+str(acc*0.001)+'\r').encode()) #now set up and move the other motor into the aggregate



cleanup(100,10)



ser.close()
stage.close()

