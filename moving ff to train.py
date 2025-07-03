# -*- coding: utf-8 -*-
"""
Created on Thu Jul  3 03:52:57 2025

@author: MemoryPC
"""

# -*- coding: utf-8 -*-
"""
Created on Thu Oct 12 15:31:15 2023

@author: marzu
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
import pims
import cv2
from skimage.filters import unsharp_mask


'''
Start here
'''

#This code controls the ff using the motors and records the training and readout experiments
#There is a feedback loop to stop recording once a systme is sufficiently trained

#EVERYTHING IN SECONDS / UM



def createFolder(ds,directory, way, vel, start, run):
    newdir = directory + '/' + str(way) + ' Intruder_in_glass_' + str(ds) + 'from' + str(start) + 'run' + str(run)
    
    if not os.path.exists(newdir):
        os.mkdir(newdir)
    
    return newdir
def createFoldermemtrain(ds,directory,  start, run):
        newdir = directory + '/training at'  + str(ds) + 'from' + str(start) + 'run' + str(run)
        
        if not os.path.exists(newdir):
            os.mkdir(newdir)
        return newdir
    
            
def createFoldermemread(ds,directory, tramp, start):
        newdir = directory + '/read at'  + str(ds) +'system trained at '+str(tramp)+'from' + str(start)
        
        if not os.path.exists(newdir):
            os.mkdir(newdir)        
        return newdir
    
def moveY(start,vel,run):
        Images = pd.DataFrame()
        Images['image'] = []
        Images['metadata'] = []
        Images['time'] = []
        
        stage.setup_velocity(min_velocity= 0, acceleration=acc*scale1,max_velocity =fast*scale1)
       
        stage.move_to(start*scale1+x0)
        time.sleep(int(start/vel))
        newdir= createFolder(directory,0,vel,start,run)
        time_range=(3000/vel + relax)
        cam.setup_acquisition(nframes=25)
        cam.start_acquisition()
        ser.write(('1VA'+str(vel*0.001)+'\r').encode()) #now set up and move the other motor into the aggregate
        ser.write(('1PA'+str(df)+'\r').encode()) #now set up and move the other motor into the aggregate
        i=0
        while True:
            i+=1
            cam.wait_for_frame()
            frame = cam.read_oldest_image(peek = False, return_info=True)
            hour = str(frame[1].timestamp.hour).zfill(2)
            minute = str(frame[1].timestamp.minute).zfill(2)
            second =str(frame[1].timestamp.second).zfill(2)
            millisecond = str(frame[1].timestamp.millisecond).zfill(3)
            imgTime = hour+minute+second+millisecond
            im = Image.fromarray(((frame[0]/frame[0].max())*255).astype(np.uint8))
            im = Image.fromarray(frame[0].astype(np.uint8))
            im.save(newdir+ '/' + imgTime  +'.tif')
            if i > (fps*time_range):
                break
    
        cam.stop_acquisition()
        
        Images = Images.sort_values(by=['time'])
        Images.apply(lambda x: plt.imsave(newdir + '/' + x['time']  + '.tiff', x['image'][0]), axis=1)
        stage.move_to(left)
        stage.wait_move()
        ser.write(('1PA'+str(d0)+'\r').encode())
        time.sleep(int(2200/vel))
        stage.setup_velocity(min_velocity= 0, acceleration=acc*scale1,max_velocity =fast*scale1)
        stage.move_to(x0)

        time.sleep(relax)
        return
    
def moveX(depth,vel,run):
        Images = pd.DataFrame()
        Images['image'] = []
        Images['metadata'] = []
        Images['time'] = []
    
        stage.setup_velocity(min_velocity= 0, acceleration=acc*scale1,max_velocity =fast*scale1)
       
        stage.move_to(left)
        time.sleep(1500/vel)
        ser.write(('1VA'+str(vel*0.001)+'\r').encode()) #now set up and move the other motor into the aggregate
        ser.write(('1PA'+str(d0+depth*0.001)+'\r').encode()) #now set up and move the other motor into the aggregate
        time.sleep(int(depth/vel+relax))
        newdir=createFolder(directory,1,vel,depth,run)
        time_range= (3000/vel + relax)#in seconds!
        cam.setup_acquisition(nframes=25)
        cam.start_acquisition()
        stage.setup_velocity(min_velocity= 0, acceleration=acc*scale1,max_velocity =vel*scale1)
        
        stage.move_to(right)
        i=0
        while True:
            i+=1
            cam.wait_for_frame()
            frame = cam.read_oldest_image(peek = False, return_info=True)
            hour = str(frame[1].timestamp.hour).zfill(2)
            minute = str(frame[1].timestamp.minute).zfill(2)
            second =str(frame[1].timestamp.second).zfill(2)
            millisecond = str(frame[1].timestamp.millisecond).zfill(3)
            imgTime = hour+minute+second+millisecond
            #im = Image.fromarray(((frame[0]/frame[0].max())*255).astype(np.uint8))
            im = Image.fromarray(frame[0].astype(np.uint8))
            im.save(newdir+'/' + imgTime  +'.tif')
            if i > (fps*time_range):
                break
    
        cam.stop_acquisition()
        
        Images = Images.sort_values(by=['time'])
        Images.apply(lambda x: plt.imsave(newdir + '/' + x['time']  + '.tiff', x['image'][0]), axis=1)

        ser.write(('1PA'+str(d0)+'\r').encode())
        time.sleep(int(depth/vel)+relax)
        stage.setup_velocity(min_velocity= 0, acceleration=acc*scale1,max_velocity =fast*scale1)
        stage.move_to(x0)

        time.sleep(relax)
        return
    
            
def movetodepth(depth, distfromcentre,vel):#depth and vel are in microns
        stage.setup_velocity(min_velocity=0, acceleration=acc*scale1,max_velocity =(fast*scale1))
        stage.move_to(x0+distfromcentre*scale1)
        stage.wait_move()
        ser.write(('1VA'+str(vel*0.001)+'\r').encode()) #now set up and move the other motor into the aggregate
        
        ser.write(('1PA'+str(d0+depth*0.001)+'\r').encode())
        time.sleep(int(depth/vel)+relax)
        d=d0+depth*0.001
        return d

def push(ds,vel,depth,width, run):
        Images = pd.DataFrame()
        Images['image'] = []
        Images['metadata'] = []
        Images['time'] = []
        start = str(depth)+ ',' +str(width)
        stage.setup_jog(step_size=ds*scale1, min_velocity=vel*scale1, acceleration=acc*scale1, max_velocity=(vel+1)*scale1,
        stop_mode=None, channel=None)
        
        dd=abs(ds)
        newdir=createFolder(dd,directory,2,vel,start,run)
        time_range= (dd/vel + relax)
        
        cam.setup_acquisition(nframes=25)
        cam.start_acquisition()
        stage.jog("+", kind="builtin")
        i=0
        while True:
            i+=1
            cam.wait_for_frame()
            frame = cam.read_oldest_image(peek = False, return_info=True)
            hour = str(frame[1].timestamp.hour).zfill(2)
            minute = str(frame[1].timestamp.minute).zfill(2)
            second =str(frame[1].timestamp.second).zfill(2)
            millisecond = str(frame[1].timestamp.millisecond).zfill(3)
            imgTime = hour+minute+second+millisecond
            #im = Image.fromarray(((frame[0]/frame[0].max())*255).astype(np.uint8))
            im = Image.fromarray(frame[0].astype(np.uint8))
            im.save(newdir+'/' + imgTime  +'.tif')
            if i > (fps*time_range):
                break
    
        cam.stop_acquisition()
        
        Images = Images.sort_values(by=['time'])
        Images.apply(lambda x: plt.imsave(newdir+'/'+ x['time']  + '.tiff', x['image'][0]), axis=1)
        return
    

def pushtrain(ds,vel,depth,width, run):
        Images = pd.DataFrame()
        Images['image'] = []
        Images['metadata'] = []
        Images['time'] = []
        start = str(depth)+ ',' +str(width)
        stage.setup_jog(step_size=ds*scale1, min_velocity=vel*scale1, acceleration=acc*scale1, max_velocity=(vel+1)*scale1,
        stop_mode=None, channel=None)
        
        dd=abs(ds)
        newdir=createFoldermemtrain(ds,directory,start,run)
        time_range= (dd/vel + relax)
        
        cam.setup_acquisition(nframes=25)
        cam.start_acquisition()
        stage.jog("+", kind="builtin")
        i=0
        while True:
            i+=1
            cam.wait_for_frame()
            frame = cam.read_oldest_image(peek = False, return_info=True)
            hour = str(frame[1].timestamp.hour).zfill(2)
            minute = str(frame[1].timestamp.minute).zfill(2)
            second =str(frame[1].timestamp.second).zfill(2)
            millisecond = str(frame[1].timestamp.millisecond).zfill(3)
            imgTime = hour+minute+second+millisecond
            #im = Image.fromarray(((frame[0]/frame[0].max())*255).astype(np.uint8))
            im = Image.fromarray(frame[0].astype(np.uint8))
            im.save(newdir+'/' + imgTime  +'.tif')
            if i > (fps*time_range):
                break
    
        cam.stop_acquisition()
        
        Images = Images.sort_values(by=['time'])
        Images.apply(lambda x: plt.imsave(newdir+'/'+ x['time']  + '.tiff', x['image'][0]), axis=1)
        return

def pushread(ds,vel,depth,width,tramp):
        Images = pd.DataFrame()
        Images['image'] = []
        Images['metadata'] = []
        Images['time'] = []
        start = str(depth)+ ',' +str(width)
        stage.setup_jog(step_size=ds*scale1, min_velocity=vel*scale1, acceleration=acc*scale1, max_velocity=(vel+1)*scale1,
        stop_mode=None, channel=None)
        
        dd=abs(ds)
        newdir=createFoldermemread(ds,directory,tramp,start)
        time_range= (dd/vel + relax)
        
        cam.setup_acquisition(nframes=25)
        cam.start_acquisition()
        stage.jog("+", kind="builtin")
        i=0
        while True:
            i+=1
            cam.wait_for_frame()
            frame = cam.read_oldest_image(peek = False, return_info=True)
            hour = str(frame[1].timestamp.hour).zfill(2)
            minute = str(frame[1].timestamp.minute).zfill(2)
            second =str(frame[1].timestamp.second).zfill(2)
            millisecond = str(frame[1].timestamp.millisecond).zfill(3)
            imgTime = hour+minute+second+millisecond
            #im = Image.fromarray(((frame[0]/frame[0].max())*255).astype(np.uint8))
            im = Image.fromarray(frame[0].astype(np.uint8))
            im.save(newdir+'/' + imgTime  +'.tif')
            if i > (fps*time_range):
                break
    
        cam.stop_acquisition()
        
        Images = Images.sort_values(by=['time'])
        Images.apply(lambda x: plt.imsave(newdir+'/'+ x['time']  + '.tiff', x['image'][0]), axis=1)
        return
    
def pushnorec(ds,vel,depth,width, run):
        
        dd=abs(ds)
        stage.setup_jog(step_size=ds*scale1, min_velocity=vel*scale1, acceleration=acc*scale1, max_velocity=(vel+1)*scale1,
        stop_mode=None, channel=None)
        
        time_range= (dd/vel + 2)
        stage.jog("+", kind="builtin")
        time.sleep(time_range)
        
        
        return
def pushy(ds,vel,depth,width, run,d):
        Images = pd.DataFrame()
        Images['image'] = []
        Images['metadata'] = []
        Images['time'] = []
        dd=abs(ds)
        #THIS IS WHAT USED TO BE HERE AND WORKS, I've changed it to work better
        #d = d0+depth*0.001
        #d = float(ser.readline().decode().strip())  
        print(d)
        start = str(depth)+ ',' +str(width)
        ser.write(('1VA'+str(vel*0.001)+'\r').encode())
        newdir=createFolder(ds,directory,3,vel,start,run)
        time_range= (dd/vel + relax)
        
        cam.setup_acquisition(nframes=25)
        cam.start_acquisition()
        ser.write(('1PA'+str(d+ds*0.001)+'\r').encode())
        i=0
        while True:
            i+=1
            cam.wait_for_frame()
            frame = cam.read_oldest_image(peek = False, return_info=True)
            hour = str(frame[1].timestamp.hour).zfill(2)
            minute = str(frame[1].timestamp.minute).zfill(2)
            second =str(frame[1].timestamp.second).zfill(2)
            millisecond = str(frame[1].timestamp.millisecond).zfill(3)
            imgTime = hour+minute+second+millisecond
            #im = Image.fromarray(((frame[0]/frame[0].max())*255).astype(np.uint8))
            im = Image.fromarray(frame[0].astype(np.uint8))
            im.save(newdir+'/' + imgTime  +'.tif')
            if i > (fps*time_range):
                break
        d=d+ds*0.001
        return d


def cleanup(vel,imax):
         x=(df-d0)/imax
         stage.setup_velocity(min_velocity= 0, acceleration=acc*scale1,max_velocity =vel*scale1) 
         ser.write(('1VA'+str(vel*0.001)+'\r').encode())
         
         for i in range (1,imax,2):
             print('cleaning '+ str(i))
             stage.move_to(right)
             stage.wait_move()
             ser.write(('1PA'+str(df-i*x)+'\r').encode())
             time.sleep(int(x/vel))
             stage.move_to(left)
             stage.wait_move()
             ser.write(('1PA'+str(df-(i+1)*x)+'\r').encode())
             time.sleep(int(x/vel))
                 
         ser.write(('1PA'+str(d0)+'\r').encode())#move 1/10 up
         time.sleep(int(x/vel))
         stage.setup_velocity(min_velocity= 0, acceleration=acc*scale1,max_velocity =fast*scale1)
         stage.move_to(x0)
         stage.wait_move()

         time.sleep(relax)
         return   
     
def home(vel):
    stage.setup_velocity(min_velocity= 0, acceleration=acc*scale1,max_velocity =vel*scale1)
    ser.write(('1PA'+str(d0)+'\r').encode())
    time.sleep(20)
    stage.setup_velocity(min_velocity= 0, acceleration=acc*scale1,max_velocity =fast*scale1)
    stage.move_to(x0)
    stage.wait_move()
    time.sleep(relax)
    d=d0
    
    
def sub(images,finimages,n):
    
    end= len(finimages)-1
    images2 = cv2.absdiff(images[0],finimages[end]) 
    images2 = images2.astype(np.uint8)
    #images2 = np.clip(wimages2, 0, 255)
    #tiff.imsave(dire + '/Imagesub/subtractedimage' + str(n) + '.tif', images2)

    return images2

def preprocess_img(frame,x0,xf,y0,yf):                                                                    #CHANGE#
    frame = frame[y0:yf,x0:xf]
    #frame = frame[0:1200,0:1200]
    frame = unsharp_mask(frame, radius = 2, amount = 5)
    frame *= 255.0/frame.max()
    return frame





ser = serial.Serial(
                    port = 'COM5',
                    baudrate=19200,
                    bytesize=serial.EIGHTBITS,
                    parity = serial.PARITY_NONE,
                    stopbits = serial.STOPBITS_ONE,
                    timeout = 2)

stage = Thorlabs.KinesisMotor("27261341")

x0= float(stage.get_position())
ser.write("1TP\r".encode())
d0 = float(ser.readline().decode().strip()) 





directory = 'D:/Experiments/jan 15/'

df= d0 + 2000*0.001
acc=2500
ser.write(('1AC'+str(acc*0.001)+'\r').encode())
fast=50
fps = 5
scale1=34.555
relax=100
droplet=70
left=x0+1300*scale1
right =x0-1300*scale1

cam = uc480.UC480Camera()
cam.set_exposure(1.34E-4)
cam.set_gains(0,0,0,0)
cam.set_frame_period(1/fps)
frame = [cam.snap(), 0]


stage.setup_jog(step_size=droplet*scale1, min_velocity=None, acceleration=acc*scale1, max_velocity=None,
stop_mode=None, channel=None)
ser.write(('1AC'+str(acc*0.001)+'\r').encode()) #now set up and move the other motor into the aggregate






#This function will train the system but with a feedback loop such that it stops the exp when 
#The imagesub indicates a trained system for at least 6 consecutive runs
def train(x,width,depths=[1400]):
    cleanup(50,10)
    cleanup(50,10)
    
    total_runs = 1
    total_pushes =500
    
    #has    done 900,1000,1100,1200,1300,1400,1500
    for current_run in range(1,  total_runs + 1):
        for depth in depths:
                 subs=[]
                 d=movetodepth(depth,width,fast)
                 time.sleep(30)
                 #training phase:
                 print('starting training at amp=:)'+ str(x)+'and d='+ str(depth))
                 for i in range(0,total_pushes):
                     pushtrain(x, 5, depth,width, (current_run-1)*total_pushes+i)
                     print('training run:)'+ str(i))
                     pushtrain(-x, 5, depth,width, (current_run-1)*total_pushes+i)
                     
                     
                     #THe following does imagesub and saves the value in subs
                     start = str(depth)+ ',' +str(width)
                     direi= directory + '/training at'  + str(x) + 'from' + str(start) + 'run' + str(i)+'/'
                     dire= directory + '/training at-'  + str(x) + 'from' + str(start) + 'run' + str(i)+'/'
                     prefix = '*.tif'
                     ypos=30+0.3833333*depth
                     #xpos=650-0.3833333*width
                     xpos=600-0.3833333*width
                     
                     xi=int(xpos-300)
                     xf=int(xpos+300)
                     y0=int(ypos-200)
                     yf=int(ypos+200)
                     
                     image_sequence = pims.ImageSequence(os.path.join(direi+ prefix))
                     images1 = [preprocess_img(frame,xi,xf,y0,yf) for frame in image_sequence]
                     plt.imshow(images1[0])
                     plt.show()
                     image_sequence2 = pims.ImageSequence(os.path.join(dire+ prefix))
                     images2 = [preprocess_img(frame,xi,xf,y0,yf) for frame in image_sequence2]
                     subbed= sub(images1, images2,i)
                     b=np.sum(subbed)
                     subs.append(b)
                     #check if any of the last 7 are trained
                     if len(subs) >= 6:
                         if all(x < 2750000 for x in subs[-6:]):
                              print('DONE AT'+ str(i))
                              plt.plot(subs)
                              plt.title('Training at: '+ str(x))
                              plt.show()
                              break   
                     '''    
                     #READOUT
                 for xi in range(15,3*x,15):
                     pushread(xi, 5, depth,width, x)
                     print('read run:)'+ str(xi))
                     pushread(-xi, 5, depth,width, x)
                     '''         
    home(50)
    


train(150,100)


ser.close()
stage.close()
cam.close()