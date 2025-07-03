# -*- coding: utf-8 -*-
"""
Created on Mon Nov 20 15:14:01 2023

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


#Run this code with the pipettes attached to the kinesis motor to sweep across the channel

#Loads the thorlabs motor
stage = Thorlabs.KinesisMotor("27261341")

#Finds the current position, assuming that the pipettes are on the left of the channel
left= float(stage.get_position())

acc=2500
scale1=34.555 
#This function will sweep scross a distance given by the distance, at a certain speed for a certain number of runs)
def make(dist,vel,runs):
    x=3000+dist
    stage.setup_velocity(min_velocity= 0, acceleration=acc*scale1,max_velocity =vel*scale1)
    for i in range (0,runs):
        print('start')
        stage.move_to(left+(x)*scale1)
        time.sleep(int(x/vel))
        stage.move_to(left)
        time.sleep(int(x/vel))
        print('Done pass:' + str(i) + 'of ' + str(runs))
make(1100,30,200)
stage.move_to(left-(800)*scale1)   
              
stage.close()

