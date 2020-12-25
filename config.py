import numpy as np
import subprocess

# DPI outputs to bit offsets
B_0 = 1<< 0
B_1 = 1<< 1
B_2 = 1<< 2
B_3 = 1<< 3
B_4 = 1<< 4
B_5 = 1<< 5
B_6 = 1<< 6
B_7 = 1<< 7
G_0 = 1<< 8
G_1 = 1<< 9
G_2 = 1<<10
G_3 = 1<<11
G_4 = 1<<12
G_5 = 1<<13
G_6 = 1<<14
G_7 = 1<<15
R_0 = 1<<16
R_1 = 1<<17
R_2 = 1<<18
R_3 = 1<<19
R_4 = 1<<20
R_5 = 1<<21
R_6 = 1<<22
R_7 = 1<<23

# GPIO notation to DPI
GPIO0 = "CLK"
GPIO1 = "DEN"
GPIO2 = "Vsync"
GPIO3 = "Hsync"
GPIO4 = B_0
GPIO5 = B_1
GPIO6 = B_2
GPIO7 = B_3
GPIO8 = B_4
GPIO9 = B_5
GPIO10 = B_6
GPIO11 = B_7
GPIO12 = G_0
GPIO13 = G_1
GPIO14 = G_2
GPIO15 = G_3
GPIO16 = G_4
GPIO17 = G_5
GPIO18 = G_6
GPIO19 = G_7
GPIO20 = R_0
GPIO21 = R_1
GPIO22 = R_2
GPIO23 = R_3
GPIO24 = R_4
GPIO25 = R_5
GPIO26 = R_6
GPIO27 = R_7

# physical numberst to DPI
PIN1 = "3v3"
PIN2 = "5v"
PIN3 = "Vsync"
PIN4 = "5v"
PIN5 = "Hsync"
PIN6 = "GND"
PIN7 = B_0
PIN8 = G_2
PIN9 = "GND"
PIN10 = G_3
PIN11 = G_5
PIN12 = G_6
PIN13 = R_7
PIN14 = "GND"
PIN15 = R_2
PIN16 = R_3
PIN17 = "3v3"
PIN18 = R_4
PIN19 = B_6
PIN20 = "GND"
PIN21 = B_5
PIN22 = R_5
PIN23 = B_7
PIN24 = B_4
PIN25 = "GND"
PIN26 = B_3
PIN27 = "CLK"
PIN28 = "DEN"
PIN29 = B_1
PIN30 = "GND"
PIN31 = B_2
PIN32 = G_0
PIN33 = G_1
PIN34 = "GND"
PIN35 = G_7
PIN36 = G_4
PIN37 = R_6
PIN38 = R_0
PIN39 = "GND"
PIN40 = R_1


#############################
#
# hardware description 
#
#############################
#
# binary counter to ABCD input
#
# Vsync to counter RESET
# Hsync to counter CLK
#
# Hsync to data latch
#
#############################

clk = B_0
enable = B_3

R1 = R_4
G1 = R_3
B1 = B_4
R2 = G_6
G2 = G_3
B2 = R_5



# push that definitions inside NumPy array, as a LUT thing
out_map = np.zeros((2, 3), dtype="uint32")
out_map = [[R1, G1, B1],
           [R2, G2, B2]]


# clear framebuffer before starting
subprocess.run("cp /dev/zero /dev/fb1", shell=True)


# grab DPI framebuffer size in pixels 
xf = subprocess.check_output("fbset -s -fb /dev/fb1 | grep '\".*\"' | grep -m 1 -o '[0-9][0-9][0-9]\+x' | tr -d 'x'", shell=True)
xf = int(xf.rstrip())
print(xf)
yf = subprocess.check_output("fbset -s -fb /dev/fb1 | grep '\".*\"' | grep -m 1 -o 'x[0-9][0-9][0-9]\+' | tr -d 'x'", shell=True)
yf = int(yf.rstrip())
print(yf)

# grab host framebuffer size in pixels 
xhost = subprocess.check_output("fbset -s -fb /dev/fb0 | grep '\".*\"' | grep -m 1 -o '[0-9][0-9][0-9]\+x' | tr -d 'x'", shell=True)
xhost = int(xhost.rstrip())

yhost = subprocess.check_output("fbset -s -fb /dev/fb0 | grep '\".*\"' | grep -m 1 -o 'x[0-9][0-9][0-9]\+' | tr -d 'x'", shell=True)
yhost = int(yhost.rstrip())



# scp -r pi@10.0.0.3:/home/pi/python/* ./python/.
# scp -r ./python/* pi@10.0.0.3:/home/pi/python/



