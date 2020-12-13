import os
#import sys
import math
import numpy as np
import time
from config import *


start_time = time.time() # capture total time execution

# create variables for output pattern
black_line=bytearray(0) # just clock
bright_line=bytearray(0) # clock and ENable bit for previous line
R_UP_line=bytearray(0) # red for top screen
B_DN_line=bytearray(0) # blue for bottom screen
RG_line=bytearray(0) # red for top screen and green for bottom
WW_line=bytearray(0) # white for both screens
BR_dots=bytearray(0) # just dots, pixel by pixel
Y_dashes=bytearray(0) # wdashes, 3px long
rainbow_line=bytearray(0) # rainbow-like pattern

rainbow = [R1+R2, R1+G1+R2+G2, G1+G2, G1+B1+G2+B2, B1+B2, B1+R1+B2+R2] # LUT for renerating rainbow

# fill the variables with colors/patterns
for x in range(int(xf/2)):  # hal of framebuffer width because generate 2 pixels each time
    if (x<64): # put selected bits
        black_line.extend((0).to_bytes(4, byteorder='little'))
        black_line.extend((clk).to_bytes(4, byteorder='little'))
        
        bright_line.extend((enable).to_bytes(4, byteorder='little'))
        bright_line.extend((enable+clk).to_bytes(4, byteorder='little'))
        
        R_UP_line.extend((R1+enable).to_bytes(4, byteorder='little'))
        R_UP_line.extend((R1+enable+clk).to_bytes(4, byteorder='little'))

        B_DN_line.extend((B2+enable).to_bytes(4, byteorder='little'))
        B_DN_line.extend((B2+enable+clk).to_bytes(4, byteorder='little'))

        RG_line.extend((R1+G2+enable).to_bytes(4, byteorder='little'))
        RG_line.extend((R1+G2+enable+clk).to_bytes(4, byteorder='little'))

        WW_line.extend((R1+G1+B1+R2+G2+B2+enable).to_bytes(4, byteorder='little'))
        WW_line.extend((R1+G1+B1+R2+G2+B2+enable+clk).to_bytes(4, byteorder='little'))


        if (x%2): # paint each other line
            BR_dots.extend((B1+enable).to_bytes(4, byteorder='little'))
            BR_dots.extend((B1+enable+clk).to_bytes(4, byteorder='little'))
        else: 
            BR_dots.extend((R2+enable).to_bytes(4, byteorder='little'))
            BR_dots.extend((R2+enable+clk).to_bytes(4, byteorder='little'))

        if ((x%6)<3): # paint 3 pixels, then leave 3 black
            Y_dashes.extend((R1+G1+enable).to_bytes(4, byteorder='little'))
            Y_dashes.extend((R1+G1+enable+clk).to_bytes(4, byteorder='little'))
        else: 
            Y_dashes.extend((R2+G2+enable).to_bytes(4, byteorder='little'))
            Y_dashes.extend((R2+G2+enable+clk).to_bytes(4, byteorder='little'))
        
        # use LUT to put colors in line
        rainbow_line.extend((rainbow[x%6]+enable).to_bytes(4, byteorder='little'))
        rainbow_line.extend((rainbow[x%6]+enable+clk).to_bytes(4, byteorder='little'))
            

    else: # just fill rest of the line with zeros
        black_line.extend((0).to_bytes(4, byteorder='little'))
        black_line.extend((0).to_bytes(4, byteorder='little'))
        
        bright_line.extend((0).to_bytes(4, byteorder='little'))
        bright_line.extend((0).to_bytes(4, byteorder='little'))
        
        R_UP_line.extend((0).to_bytes(4, byteorder='little'))
        R_UP_line.extend((0).to_bytes(4, byteorder='little'))

        B_DN_line.extend((0).to_bytes(4, byteorder='little'))
        B_DN_line.extend((0).to_bytes(4, byteorder='little'))

        RG_line.extend((0).to_bytes(4, byteorder='little'))
        RG_line.extend((0).to_bytes(4, byteorder='little'))

        WW_line.extend((0).to_bytes(4, byteorder='little'))
        WW_line.extend((0).to_bytes(4, byteorder='little'))
            
        BR_dots.extend((0).to_bytes(4, byteorder='little'))
        BR_dots.extend((0).to_bytes(4, byteorder='little'))

        Y_dashes.extend((0).to_bytes(4, byteorder='little'))
        Y_dashes.extend((0).to_bytes(4, byteorder='little'))

        rainbow_line.extend((0).to_bytes(4, byteorder='little'))
        rainbow_line.extend((0).to_bytes(4, byteorder='little'))
            


# drop that lines directly to framebuffer
with open('/dev/fb1','wb') as f:

    ########################################
    #
    # edit code below
    # add or remove f.write with valid lines
    #
    #
    # black_line   # just clock
    # bright_line  # clock and ENable bit for previous line
    # R_UP_line    # red for top screen
    # B_DN_line    # blue for bottom screen
    # RG_line      # red for top screen and green for bottom
    # WW_line      # white for both screens
    # BR_dots      # just dots, pixel by pixel
    # Y_dashes     # wdashes, 3px long
    # rainbow_line # rainbow-like pattern
    #
    ########################################

    #f.write(WW_line)    
    #f.write(BR_dots)    
    #f.write(Y_dashes)    
    #f.write(rainbow_line)    
    #f.write(rainbow_line)    
    #f.write(rainbow_line)    



    #f.write(RG_line)    
    #f.write(WW_line)    
    #f.write(RG_line)    
    #f.write(WW_line) 
    #f.write(WW_line)    
    #f.write(bright_line)
    #f.write(WW_line)    
    #f.write(R_UP_line)    
    #f.write(B_DN_line)    
    #f.write(WW_line) 
    
    
    #f.write(bright_line)
    #f.write(black_line)

    
    ########################################
    #
    # end of playfield
    #
    ########################################
    f.write(black_line)
    f.close()
print("fps: ", 1.0/(time.time()-start_time))


exit()
