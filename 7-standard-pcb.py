#######################################################
##
## IMPORTANT
## correct /boot/config.txt
## to include line below:
##       dpi_timings= 240 0 00 00 00 360 0 00 00 00 0 0 0 60 0 32000000 3
##
## Reason: remove dead time for horizontal/vertical blank
##
#######################################################


import os
#import sys
#import math
import numpy as np
#import subprocess
import time

from config import *


##########     .     ##########

R1 = GPIO11
G1 = GPIO27
B1 = GPIO7
R2 = GPIO8
G2 = GPIO9
B2 = GPIO10

clk = GPIO17
enable = GPIO18
strobe = GPIO4

rows = [GPIO22, GPIO23, GPIO24, GPIO25]
#          A       B       C       D

# push that definitions inside NumPy array, as a LUT thing
out_map = [[R1, G1, B1],
           [R2, G2, B2]]


##########     prepare rows LUT     ##########
row_lut = np.zeros((16), dtype="uint32")
for n in range(16):
    d=0
    if(n&(1<<0)):
        d += rows[0]
    if(n&(1<<1)):
        d += rows[1]
    if(n&(1<<2)):
        d += rows[2]
    if(n&(1<<3)):
        d += rows[3]
    row_lut[n]=d
        

        

##########     settings     ##########
gamma=2 # 1 =enable, 0 =disable
bright=0.90 # 0 to 1 linear brightness
xs=5 # horizontal scale, integer
ys =xs # vertical scale, integer
bl=4 # bit depth per color, max 8
bb=4 # brightness for bitplane zero. Like 1, 2, 4, 8 or so! each next bitplane is half




startx=100 # pixels from top of the input screen (fb0)
starty=200 # pixels from left of the input screen
width=64 # input window will be this times scale
height=32 # same as above


xl=64 # columns of the LED screen
yl=16 # pjysical rows of the LED screen
zl=2  # screens, typically 2 per panel





power_lut = np.zeros((8))
power_lut[0] = bb
for n in range (1, bl):
    power_lut[n] = power_lut[n-1] /2
out_multiply = np.ceil(power_lut).astype("uint8") # roundup




##########     apply brightness to output data     ##########
def set_brightness(value, array):
    out = np.full((8, 16, xf), clk+enable, dtype="uint32") # CLK all high for stability reason
    #                      ^ bit,  y, x
    out[:, :, 1:xl*2+1:2] = 0
    out[:, :, 2:xl*2+2:2] = clk # apply CLK to data section
    out[:, :, xf-3:xf-2] += strobe # add latch pulse
    for n in range(16):
        out[:, n, :] += row_lut[n]
    

    for n in range (8):
        if (int(array[n])):
            out[n,:,0:int(value*xf)] -= enable # add brightness bit for FULL lines (don't multplay)
        else:
            out[n,:,0:int(value*xf*array[n])] -= enable # add brightness bit for HALF lines
    
    # little hack to shift color and brightness one line off
    # MSB (brightest bitplane) at begining of the array
    out = np.concatenate((out[0, 15, :].ravel(), out.ravel())) # flatten the array and add extra column to move brightness bits one row away from data bits (added later) 
    out = np.resize(out, (8, 16, xf)) #, refcheck=False) # resize back to expected size, cut off extra bytes
    
    
    # print some stats
    print("Total lines: ", (out_multiply.sum()+1)*16, ", allowed maximum: ", yf, " (FB height)")
    max_bri = power_lut.sum()*16 / (yf+3) * xf / (xf+30)
    print("Set brightness: ", "%.3f" % (value*100), "%, real brightness: ", "%.3f" % (value*max_bri*100), "%, maximum: ", "%.3f" % (max_bri*100), "%")
    return(out) 



##########     prepare color look-up table, 8 because 2^3 (RGB)     ##########
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
    arr_bitmask[n, :, :, :] = (1<<(7-n)) 


arr_out_br_clk = np.full((8, 16, xf), clk, dtype="uint32")
#                      ^ bit,  y, x
arr_out_br_clk[:, :, 1:xl*2+1:2] = 0
arr_out_br_clk[:, :, 2:xl*2+2:2] = clk
arr_out_br_clk[:, :, xl-3:xf-1] += strobe

timer=40
data=([0, 0, 0, 0, 0])



##########     prepare black line + clock     ##########
front_blank = np.full((1, xf), clk+enable, dtype="uint32")
front_blank[:, ::2] = enable
front_blank[:, xf-3:xf-1] += strobe

arr_out_br_clk = set_brightness(bright, power_lut).copy()

##########     apply same brightness to last empty line     ##########
end_bright = np.full((1, xf), clk+enable +row_lut[15], dtype="uint32")
end_bright[:, ::2] -= clk # generate clock, clear every second word
end_bright[:,0:int(bright*xf*power_lut[bl-1])] -= enable # set brightness
end_bright[:, xf-3:xf-1] += strobe


with open('/dev/fb1','wb') as f:
    for n in range(yf):
        front_blank[0].tofile(f)
    f.close()


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
    arr_bitplanes = np.bitwise_and(arr_bitmask, arr_input) # split imported image into 8 bitplanes
    arr_bitplanes[:,:,:,0] = np.where(arr_bitplanes[:,:,:,0], 4, 0) # apply weights to colors
    arr_bitplanes[:,:,:,1] = np.where(arr_bitplanes[:,:,:,1], 2, 0)
    arr_bitplanes[:,:,:,2] = np.where(arr_bitplanes[:,:,:,2], 1, 0)
    
    arr_sum = np.bitwise_or(np.bitwise_or(arr_bitplanes[:,:,:,0], arr_bitplanes[:,:,:,1]), arr_bitplanes[:,:,:,2])
                    # ^ sum colors into bitplanes 
    d3 = np.bitwise_or(out_lut[0, arr_sum[:, 0:16, :]], out_lut[1, arr_sum[:, 16:32, :]])
                    # ^ translate color codes (weights 1-2-4) to correct bits, different codes (bits) for each screen
    arr_out_data = arr_out_br_clk.copy()
                    # ^ borrow copy of pre-generated array, with brightness bits
    #arr_out_data[0:1, 0:2, :] = 0

    arr_out_data[:, :, 1:xl*2+1:2] += d3 # drop image data into buffer
    arr_out_data[:, :, 2:xl*2+2:2] += d3 # clock and brightness already inside
    

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
    
    a = np.concatenate((front_blank, np.repeat(arr_out_data, out_multiply, axis=0).reshape((-1, xf)), end_bright))
    #   ^ easy to adjust by poking wth power_lut
    #a = np.concatenate((front_blank, a0, a0, a0, a0, a0, a0, a0, a0, a1, a1, a1, a1, a2, a2, a3, a4, a5, a6, a7, end_bright))
    #   ^ acually faster, but fixed and need manual tweaks
    #a = np.concatenate((front_blank, a0, a1, a0, a2, a0, a1, a0, a3, a6, a7, a0, a1, a0, a2, a0, a1, a0, a4, a5, end_bright))
    #   ^ ideal data sequence, but brightness line-off data doesn't match
    
    with open('/dev/fb1','wb') as f:
        a.tofile(f)
        f.close()
        
    
    ##########     calculate total fps and possible fps if divided into parallel tasks     ##########
    time4 = time.time()
    
    data[0]+= (1.0/(time2-time1))
    data[1]+= (1.0/(time3-time2))
    data[2]+= (1.0/(time4-time3))
    data[3]+= (1.0/(time4-time1))
    
    #time.sleep(0.05)
    time5 = time.time()
    data[4]+= (1.0/(time5-time1))
    
    if (timer):
        timer-=1
    else:
        timer=39
        print("fps:", "%.3f" % (data[3]/40), "imp", "%.3f" % (data[0]/40), "conv", "%.3f" % (data[1]/40), "send", "%.3f" % (data[2]/40), "real", "%.3f" % (data[4]/40))
        data = ([0, 0, 0, 0, 0])
        


