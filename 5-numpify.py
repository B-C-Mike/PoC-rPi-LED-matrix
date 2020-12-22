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
bright=0.263 # 0 to 1 linear brightness
xs=6 # horizontal scale, integer
ys =xs # vertical scale, integer
bl=8 # bit depth per color, max 8
bright *= xf

startx=100
width=64
starty=100
height=32


#$%&@! 7 MSB - 0 LSB


xl=64 # columns
yl=16 # pjysical rows
zl=2  # screens


##########     prepare color look-up table     ##########
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
arr_out_black = np.full((1, xf), clk, dtype="uint32")
front_blank = np.full((13, xf), clk, dtype="uint32")
count=0
timer=9
for x in range(0, xl):
    count+=1
    d2=0

    arr_out_black[0, count] = d2
    count+=1
    arr_out_black[0, count] = d2+clk




##########     spawn arrays     ##########
arr_input= np.zeros((1,32, 64, 3), dtype="uint8")
#           ^ bitplane, y,  x, color
arr_gamma= np.zeros((32, 64, 3), dtype="uint16")
#                   ^ y,  x, color
arr_bitplanes= np.zeros((8, 32, 64, 3), dtype="uint8")
#                    ^ bit,  y,  x, color
arr_sum= np.zeros((8, 32, 64), dtype="uint8")
#              ^ bit,  y,  x
arr_out_data = np.zeros((8, 16, xf), dtype="uint32")
#                   ^ bit,  y, x
d3 = np.zeros((8, 16, xl), dtype="uint32")

#arr_bitmask = np.zeros((8, 32, 64, 3), dtype="uint8") # full size array
#arr_bitmask = np.zeros((8, 1, 64, 3), dtype="uint8") # doesn't hurt, doesn't help
arr_bitmask = np.zeros((8, 1, 1, 1), dtype="uint8") # 2% speed improve
for n in range(0,8):
    arr_bitmask[n, :, :, :] = (1<<n)   #$%&@! 7 MSB - 0 LSB


arr_out_br_clk = np.full((8, 16, xf), clk, dtype="uint32")
#                      ^ bit,  y, x
arr_out_br_clk[:, :, 1:xl*2+1:2] = 0
arr_out_br_clk[:, :, 2:xl*2+2:2] = clk



##########     apply brightness to output data     ##########
def set_brightness(value, array):
    #value *= xf 
    
    out = np.full((8, 16, xf), clk, dtype="uint32") # CLK all high for stability reason
    #                      ^ bit,  y, x
    out[:, :, 1:xl*2+1:2] = 0
    out[:, :, 2:xl*2+2:2] = clk # apply CLK to data section

    for n in range (8):
        if (int(array[n])):
            out[n,:,0:int(bright)] += enable # add brightness bit for FULL lines (don't multplay)
        else:
            out[n,:,0:int(bright*array[n])] += enable # add brightness bit for HALF lines
    
    # little hack to shift color and brightness one line off
    #out = np.flip(out,0) # flip to put MSB (brightest bitplane) at begining of the array
    out = np.concatenate((out[0, 0, :].ravel(), out.ravel())) # flatten the array and add extra column to move brightness bits one row away from data bits (added later) 
    out = np.resize(out, (8, 16, xf)) #, refcheck=False) # resize back to expected size, cut off extra bytes
    out = np.flip(out,0) # and flip back to expected order
    return(out) #$%&@! 7 MSB - 0 LSB


bt_lut = np.array([8, 4, 2, 1, 1/2, 1/4, 1/8, 1/16]) #$%&@! 7 MSB - 0 LSB
#      ^ bitplanes 0, 1, 2, 3,   4,   5,   6,   7

out_multiply = np.array([8, 4, 2, 1, 1, 1, 1, 1]) #$%&@! 7 MSB - 0 LSB

arr_out_br_clk = set_brightness(bright, bt_lut).copy()

##########     apply same brightness to empty line     ##########
arr_out_bright = arr_out_black.copy()
arr_out_bright[0,0:int(bright*bt_lut[7])] += enable
        


if (0): # old code, that works but looks terrible
    #arr_out_data xf 16 8 to bit7
    arr_out_br_clk[4:8,:,0:int(bright)] += enable # "full" brightness for bitplanes 4 to 7
    arr_out_br_clk[3,0,0:int(bright)] += enable # and first row of 3 bitplane

    arr_out_br_clk[3,1:16,0:int(bright/2)] += enable # half brightness for bitplane 3
    arr_out_br_clk[2,0,0:int(bright/2)] += enable

    arr_out_br_clk[2,1:16,0:int(bright/4)] += enable # quater brightness for bitplane 2
    arr_out_br_clk[1,0,0:int(bright/4)] += enable

    arr_out_br_clk[1,1:16,0:int(bright/8)] += enable # bitplane 1
    arr_out_br_clk[0,0,0:int(bright/8)] += enable

    arr_out_br_clk[0,1:16,0:int(bright/16)] += enable # bitplane 0


    

while 1:
    time1 = time.time()




    ##########     import image     ##########
    with open('/dev/fb0','rb') as s:
        s.seek(xhost*starty*4, 0)
        raw=s.read(height*ys*xhost*4)
        buffer = np.frombuffer(raw, dtype="uint8").reshape((1, height*ys,xhost,4))
        
        arr_input = buffer[0, ::ys, startx:startx+xs*width:xs, 0:3]
        s.close()
        
    ##########     super simple gamma correction     ##########
    if(gamma):
        arr_gamma = arr_input.astype("uint16")
        arr_gamma = arr_gamma**2
        arr_input = np.right_shift(arr_gamma, 8).astype("uint8")

    time2 = time.time()

    
    
    ##########     convert image to bitplanes     ##########
    arr_bitplanes = np.bitwise_and(arr_bitmask, arr_input)
    arr_bitplanes[:,:,:,0] = np.where(arr_bitplanes[:,:,:,0], 4, 0)
    arr_bitplanes[:,:,:,1] = np.where(arr_bitplanes[:,:,:,1], 2, 0)
    arr_bitplanes[:,:,:,2] = np.where(arr_bitplanes[:,:,:,2], 1, 0)
    
    arr_sum = np.bitwise_or(np.bitwise_or(arr_bitplanes[:,:,:,0], arr_bitplanes[:,:,:,1]), arr_bitplanes[:,:,:,2])

    d3 = np.bitwise_or(out_lut[0, arr_sum[:, 0:16, :]], out_lut[1, arr_sum[:, 16:32, :]])
    
    arr_out_data = arr_out_br_clk.copy()

    arr_out_data[:, :, 1:xl*2+1:2] += d3
    arr_out_data[:, :, 2:xl*2+2:2] += d3
    

    time3 = time.time()
    
    ##########     write bitplanes to output framebuffer     ##########
    a7 = arr_out_data[7,:,:]
    a6 = arr_out_data[6,:,:]
    a5 = arr_out_data[5,:,:]
    a4 = arr_out_data[4,:,:]
    a3 = arr_out_data[3,:,:]
    a2 = arr_out_data[2,:,:]
    a1 = arr_out_data[1,:,:]
    a0 = arr_out_data[0,:,:]
    #a = np.concatenate((front_blank, a7, a7, a7, a7, a7, a7, a7, a7, a6, a6, a6, a6, a5, a5, a4, a3, a2, a1, a0, arr_out_bright, arr_out_black))
    # total 318 lines to print out, 360 limit set in bootup config.txt
    #a = np.repeat(np.flip(arr_out_data,0), out_multiply, axis=0).reshape((-1, 240))
    
    #print(a.shape)
    #print(front_blank.shape)
    #print(arr_out_bright.shape)
    #print(arr_out_black.shape)
    #exit()
    
    #a = np.concatenate((front_blank, np.repeat(np.flip(arr_out_data,0), out_multiply, axis=0).reshape((-1, 240)), arr_out_bright, arr_out_black))
    a = np.concatenate((front_blank, np.repeat(np.flip(arr_out_data,0), out_multiply, axis=0).reshape((-1, 240)), arr_out_bright, arr_out_black))
    
    with open('/dev/fb1','wb') as f:
        #a.tofile(f)
        
        
        
        #front_blank.tofile(f)
        a.tofile(f)   #$%&@! 7 MSB - 0 LSB
        #arr_out_bright.tofile(f)
        #arr_out_black.tofile(f)
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
        timer=40
        print("fps:", t4, "imp", t1, "conv", t2, "send", t3, "real", t5)
    #print("input ", 1.0/(draw_time-start_time), " draw", 1.0/(time.time()-draw_time))
        


