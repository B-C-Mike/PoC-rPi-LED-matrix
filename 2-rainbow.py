import os
#import sys
import math
import numpy as np
import time
from config import *



lo0p=1
while lo0p:
    lo0p=0
    start_time = time.time()
    
    # fill rainbow pattern
    rgb = np.zeros((32, 3))
    rgb[0]=[3, 3, 3]
    rgb[1]=[0, 0, 0]
    rgb[2]=[0, 0, 1]
    rgb[3]=[0, 0, 2]
    rgb[4]=[0, 0, 3]
    rgb[5]=[0, 1, 3]
    rgb[6]=[0, 2, 3]
    rgb[7]=[0, 3, 3]
    rgb[8]=[0, 3, 2]
    rgb[9]=[0, 3, 1]
    rgb[10]=[0, 3, 0]
    rgb[11]=[1, 3, 0]
    rgb[12]=[2, 3, 0]
    rgb[13]=[3, 3, 0]
    rgb[14]=[3, 2, 0]
    rgb[15]=[3, 1, 0]
    rgb[16]=[3, 0, 0]
    rgb[17]=[3, 0, 1]
    rgb[18]=[3, 0, 2]
    rgb[19]=[3, 0, 3]
    rgb[20]=[2, 0, 3]
    rgb[21]=[1, 0, 3]
    rgb[22]=[0, 0, 3]
    rgb[23]=[3, 2, 1]
    rgb[24]=[0, 0, 0]
    rgb[25]=[1, 1, 1]
    rgb[26]=[2, 2, 2]
    rgb[27]=[3, 3, 3]
    rgb[28]=[0, 0, 0]
    rgb[29]=[3, 0, 0]
    rgb[30]=[0, 3, 0]
    rgb[31]=[0, 0, 3]

    
    # generate image (LED matrix), based on given pattern
    arr1 = np.zeros((64, 32, 8, 3))
    
    width=64
    height=32
    for y in range(height):
        for x in range (width):
            if (y==0 or y>28): # generate gradient for given color, alter orientation for some lines
                b=int(rgb[y][2]*(63-x))
                g=int(rgb[y][1]*(63-x))
                r=int(rgb[y][0]*(63-x))
            else: 
                b=int(rgb[y][2]*x)
                g=int(rgb[y][1]*x)
                r=int(rgb[y][0]*x)


            for bit in range(0,8): # split pixel into 8 bitfields
                arr1[x][y][bit][0]= ((r)&(1<<bit))
                arr1[x][y][bit][1]= ((g)&(1<<bit))
                arr1[x][y][bit][2]= ((b)&(1<<bit))


    xs=int(xf/2)
    # create black line, empty line. 
    black_line =bytearray(0) 
    for x in range(0,xs):
        black_line.extend((0).to_bytes(4, byteorder='little')) #
        black_line.extend((0).to_bytes(4, byteorder='little')) #
    
    bit0=bytearray(0)
    bit1=bytearray(0)
    bit2=bytearray(0)
    bit3=bytearray(0)
    bit4=bytearray(0)
    bit5=bytearray(0)
    bit6=bytearray(0)
    bit7=bytearray(0)
    
    # translate bitplanes into strings of data
    for bit in range(0,8):
        dat=bytearray(0)
        for y in range (16):
            count=0
            for x in range(0,xs):
                count+=1
                d2=0
                if (count <=64):
                    d2=enable
                    if (count>90):
                        d2=0
                    if (arr1[x][y][bit][2]): #b
                        d2+=B1
                    if (arr1[x][y][bit][1]): #g
                        d2+=G1
                    if (arr1[x][y][bit][0]): #r
                        d2+=R1
                        
                    if (arr1[x][y+16][bit][2]): #b
                        d2+=B2
                    if (arr1[x][y+16][bit][1]): #g
                        d2+=G2
                    if (arr1[x][y+16][bit][0]): #r
                        d2+=R2
                    low=(d2).to_bytes(4, byteorder='little') #
                    hig=(d2+clk).to_bytes(4, byteorder='little') #
                    
                    dat.extend(low)
                    dat.extend(hig)
                else:
                    dat.extend((0).to_bytes(4, byteorder='little')) #
                    dat.extend((0).to_bytes(4, byteorder='little')) #
            #f.write(dat) #
        if(bit==0):
            bit0=dat
        if(bit==1):
            bit1=dat
        if(bit==2):
            bit2=dat
        if(bit==3):
            bit3=dat
        if(bit==4):
            bit4=dat
        if(bit==5):
            bit5=dat
        if(bit==6):
            bit6=dat
        if(bit==7):
            bit7=dat

            
        

    with open('/dev/fb1','wb') as f:
        for n in range(13):
            f.write(black_line) # padding at the beginning
        
        # display data in order, 
        #f.write(bit7)    
        #f.write(bit7)    
        #f.write(bit7)    
        #f.write(bit7)    
        #f.write(bit7)    
        #f.write(bit7)    
        #f.write(bit7)    
        #f.write(bit7)    
        #f.write(bit6)    
        #f.write(bit6)    
        #f.write(bit6)    
        #f.write(bit6)    
        #f.write(bit5)    
        #f.write(bit5)    
        #f.write(bit4)    
    

        # shuffle data around to get less flicker
        f.write(bit7)    
        f.write(bit6)    
        f.write(bit7)    
        f.write(bit5)    
        f.write(bit7)    
        f.write(bit6)    
        f.write(bit7)    
        f.write(bit4)    
        f.write(bit7)    
        f.write(bit6)    
        f.write(bit7)    
        f.write(bit5)    
        f.write(bit7)    
        f.write(bit6)    
        f.write(bit7)    
        #f.write(bit3)    
        for n in range(30):
            f.write(black_line) # paddung at the end
        f.close()
    print("fps: ", 1.0/(time.time()-start_time))

