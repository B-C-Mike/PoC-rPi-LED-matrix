import os
#import sys
import math
import numpy as np
import time

from config import *


xl=64 # columns
yl=16 # physical rows
bl=8  # bit depth per color, max 8
gamma=2 # gamma correction, 2 =enable, 0 =disable




while 1:
    start_time = time.time()

    
    arr1 = np.zeros((64, 32, 8, 3)) # input array: [X] [Y] [bitplanes] [RGB]
    with open('/dev/fb0','rb') as s: # open rPi main screen
        startx=20
        starty=100 # grab at offset from top-left corner
        width=64
        height=32
        for y in range(height):
            s.seek((xhost*(starty+y)+startx)*4, 0)
            for x in range (width):
                if (gamma): # grab 3 bits and apply gamma=2.0 curve
                    b=(ord(s.read(1))**2)>>8
                    g=(ord(s.read(1))**2)>>8
                    r=(ord(s.read(1))**2)>>8
                else: # grab 3 bits without correction, gamma = 1.0
                    b=ord(s.read(1))
                    g=ord(s.read(1))
                    r=ord(s.read(1))
                a=s.read(1) # read and waste 4'th bit because 32b color
                for bit in range(8-bl,8): # encode bits into bitplanes
                    arr1[x][y][bit][0]= ((r)&(1<<bit))
                    arr1[x][y][bit][1]= ((g)&(1<<bit))
                    arr1[x][y][bit][2]= ((b)&(1<<bit))
        s.close()
 

    draw_time = time.time()



    arr2 = np.full((8, 16, xf), clk, dtype="uint32") # output rows for matrix [bitplane] [row] [framebuffer pixels]
    arr3 = np.full((1, 1, xf), clk, dtype="uint32") # output row (black and clock)



    xs=int(xf/2) # dump 2 DPI pixels at a time
    
    ys=yf
    
    for bit in range(8-bl,8):
        dat=bytearray(0)
        for y in range (yl):
            for x in range(0, xl):
                d2=0
                if (arr1[x][y][bit][2]): #b
                    d2+=B1
                if (arr1[x][y][bit][1]): #g
                    d2+=G1
                if (arr1[x][y][bit][0]): #r
                    d2+=R1
                    
                if (arr1[x][y+16][bit][0]): #r
                    d2+=R2
                if (arr1[x][y+16][bit][2]): #b
                    d2+=B2
                if (arr1[x][y+16][bit][1]): #g
                    d2+=G2
                arr2[bit, y, 2*x] = d2 # just image data, no brightness
                arr2[bit, y, 2*x+1] = d2+clk
                


    
    for x in range(0, xl):
        arr3[0, 0, 2*x] = 0 # just clock, no brightness
        arr3[0, 0, 2*x+1] = 0+clk
                


    

            
    arr2[8-bl:8,:,0:90] += enable # add brightness bit for first 90 bits. 
    arr3[:,:,0:90] += enable
    
    with open('/dev/fb1','wb') as f:
        for n in range(13):
            arr3[0,0,:].tofile(f) # send 13 lines of "black & clock" to make next write as first (top) line 
        
        
        ### magic below, don't touch
        ### this function should write bitfields with appropiete weight
        ### like 77777777 6666 55 4
        max_1 = 3
        max_2 = bl
        bit=8
        count=13
        while(bit):
            for m in range(1<<max_1):
                arr2[bit-1,:,:].tofile(f)
                count +=16
            bit -=1
            max_2 -=1
            if(max_1==0 or max_2==0):
                #print (bit, max_1, max_2)
                bit=0
            max_1 -=1
        for n in range(count, yf):
            arr3[0,0,:].tofile(f)
        #print(count)
            
            
        ### if function above doesn't work
        ### just write data to framebuffer
        ### manually, like code below

        #arr2[7,:,:].tofile(f)
        #arr2[6,:,:].tofile(f)
        #arr2[7,:,:].tofile(f)
        #arr2[5,:,:].tofile(f)
        #arr2[7,:,:].tofile(f)
        #arr2[6,:,:].tofile(f)
        #arr2[7,:,:].tofile(f)
        #arr2[4,:,:].tofile(f)
        #arr2[7,:,:].tofile(f)
        #arr2[6,:,:].tofile(f)
        #arr2[7,:,:].tofile(f)
        #arr2[5,:,:].tofile(f)
        #arr2[7,:,:].tofile(f)
        #arr2[6,:,:].tofile(f)
        #arr2[7,:,:].tofile(f)
        #arr2[4,:,:].tofile(f)
        #arr3[0,0,:].tofile(f)


        f.close()
    print("fps: ", 1.0/(time.time()-start_time))
    print("input ", 1.0/(draw_time-start_time), " draw", 1.0/(time.time()-draw_time)) # just a but of stats

