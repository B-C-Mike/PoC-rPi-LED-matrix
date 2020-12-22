import os
#import sys
#import math
import numpy as np
#import subprocess
import time

from config import *


##########     .     ##########


##########     settings     ##########
gamma=2 # 1 =enable, 0 =disable
bright=0.363 # 0 to 1 linear brightness
xs=3 # horizontal scale, integer
ys =xs # vertical scale, integer
bl=8 # bit depth per color, max 8
bright *= xf





xl=64 # columns
yl=16 # pjysical rows
zl=2  # screens


##########     prepare look-up table     ##########
out_lut = np.zeros((zl, 8), dtype="uint32")
for i in range(zl):
    for n in range(8):
        d=0
        if(n&(1<<0)):
            d += out_map[i][0]
        if(n&(1<<1)):
            d += out_map[i][1]
        if(n&(1<<2)):
            d += out_map[i][2]
        out_lut[i, n]=d
        
#print(out_lut)
print("refresh rate: ", 40*1000*1000/(xf+30)/(yf+3), "hz")

        
##########     prepare black line + clock     ##########
arr_out_black = np.full((1, 1, xf), clk, dtype="uint32")
count=0
timer=9
for x in range(0, xl):
    count+=1
    d2=0

    arr_out_black[0, 0, count] = d2
    count+=1
    arr_out_black[0, 0, count] = d2+clk


while 1:
    time1 = time.time()


    ##########     spawn arrays     ##########
    arr_input= np.zeros((32, 64, 3), dtype="uint8")
    #                   ^ y,  x, color
    arr_gamma= np.zeros((32, 64, 3), dtype="uint16")
    #                   ^ y,  x, color
    arr_bitplanes= np.zeros((8, 32, 64, 3), dtype="uint8")
    #                    ^ bit,  y,  x, color
    arr_sum= np.zeros((8, 32, 64), dtype="uint8")
    #              ^ bit,  y,  x
    arr_out_data = np.full((8, 16, xf), clk, dtype="uint32")
    #                   ^ bit,  y, x
    


    ##########     import image     ##########
    with open('/dev/fb0','rb') as s:
        startx=100
        width=64
        starty=100
        height=32
        for y in range(height):
            s.seek((xhost*(starty+y*ys)+startx)*4, 0)
            raw = s.read(width*xs*4)
            buffer = np.frombuffer(raw, dtype="uint8").reshape((64,4*xs))
            arr_input[y, :, :] = buffer[:, 0:3]
        s.close()
        
    ##########     super simple gamma correction     ##########
    if(gamma):
        arr_gamma = arr_input.astype("uint16")
        arr_gamma = arr_gamma**2
        arr_input = np.right_shift(arr_gamma, 8)

    time2 = time.time()

    ##########     convert image to bitplanes     ##########
    for n in range(0,8):
        arr_bitplanes[n, :, :, :] = arr_input[:, :, :] &(1<<n)
    arr_bitplanes[:,:,:,0] = np.where(arr_bitplanes[:,:,:,0], 4, 0)
    arr_bitplanes[:,:,:,1] = np.where(arr_bitplanes[:,:,:,1], 2, 0)
    arr_bitplanes[:,:,:,2] = np.where(arr_bitplanes[:,:,:,2], 1, 0)
    arr_sum[:,:,:] = np.add(arr_bitplanes[:,:,:,0], arr_bitplanes[:,:,:,1])
    arr_sum[:,:,:] = np.add(arr_sum[:,:,:], arr_bitplanes[:,:,:,2])
    
    d3 = np.zeros((8, 16, xl), dtype="uint32")
    d3 = np.add(out_lut[0, arr_sum[:, 0:16, :]], out_lut[1, arr_sum[:, 16:32, :]])
    arr_out_data[:, :, 1:xl*2+1:2] = d3
    arr_out_data[:, :, 2:xl*2+2:2] = d3+clk



    ##########     apply brightness to output data     ##########
    
    #arr_out_data xf 16 8 to bit7
    arr_out_data[4:8,:,0:int(bright)] += enable # "full" brightness for bitplanes 4 to 7
    arr_out_data[3,0,0:int(bright)] += enable # and first row of 3 bitplane
    
    arr_out_data[3,1:16,0:int(bright/2)] += enable # half brightness for bitplane 3
    arr_out_data[2,0,0:int(bright/2)] += enable
    
    arr_out_data[2,1:16,0:int(bright/4)] += enable # quater brightness for bitplane 2
    arr_out_data[1,0,0:int(bright/4)] += enable
    
    arr_out_data[1,1:16,0:int(bright/8)] += enable # bitplane 1
    arr_out_data[0,0,0:int(bright/8)] += enable
    
    arr_out_data[0,1:16,0:int(bright/16)] += enable # bitplane 0

    
    time3 = time.time()    
    
    
    ##########     write bitplanes to output framebuffer     ##########
    # total 318 lines to print out, 360 limit set in bootup config.txt
    with open('/dev/fb1','wb') as f:
        for n in range(13):
            arr_out_black[0,0,:].tofile(f)
        count=13
        div=1
        
        if(bl>0):        
            for n in range(8):
                arr_out_data[7,:,:].tofile(f) # bitplane 7 show with 8x main brightness (copy 8 times)
                count +=16
            
        if(bl>1):        
            for n in range(4):
                arr_out_data[6,:,:].tofile(f) # bitplane 6
                count +=16
            
        if(bl>2):        
            for n in range(2):
                arr_out_data[5,:,:].tofile(f) # bitplane 5
                count +=16
            
        if(bl>3):        
            for n in range(1):
                arr_out_data[4,:,:].tofile(f) # bitplane 4 with main brightness (copy only once)
                count +=16

        if(bl>4):        
            arr_out_data[3,:,:].tofile(f) # bitplane 3 have already applied brightness of 1/2
            count +=16
            div=2
        if(bl>5):        
            arr_out_data[2,:,:].tofile(f) # bitplane 2
            count +=16
            div=4
        if(bl>6):        
            arr_out_data[1,:,:].tofile(f) # bitplane 1
            count +=16
            div=8
        if(bl>7):        
            arr_out_data[0,:,:].tofile(f) # bitplane 0 have already applied brightness of 1/16
            count +=16
            div=16

        ##########     apply same brightness to empty line     ##########
        arr_out_bright = arr_out_black.copy()
        arr_out_bright[0,0,0:int(bright/div)] += enable
        arr_out_bright[0,0,:].tofile(f)
        count +=1

        for n in range(count, yf):
            arr_out_black[0,0,:].tofile(f) # fill rest of the framebuffer with just clock
        #print(count)
        f.close()
        
    
    ##########     calculate total fps and possible fps if divided into parallel tasks     ##########
    time4 = time.time()
    
    t1 = "%.3f" % (1.0/(time2-time1))
    t2 = "%.3f" % (1.0/(time3-time2))
    t3 = "%.3f" % (1.0/(time4-time3))
    t4 = "%.3f" % (1.0/(time4-time1))
    
    #time.sleep(0.05)
    time5 = time.time()
    t5 = "%.3f" % (1.0/(time5-time1))
    
    if (timer):
        timer-=1
    else:
        timer=20
        print("fps:", t4, "imp", t1, "conv", t2, "send", t3, "real", t5)
    #print("input ", 1.0/(draw_time-start_time), " draw", 1.0/(time.time()-draw_time))
        






