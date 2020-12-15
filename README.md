# PoC-rPi-LED-matrix
Look mum I can have high speed DMA on rPi. // This is improvement (prof of concept) to [hzeller][url]'s code. My method uses different hardware to reduce CPU load. 



What is the LED matrix? 
-
- Really stupid piece of display. Basically no internal memory. 
- Requires constant refreshing. Almost like CRT monitor. 
- Binary color (on or off). Software-based dimming. 
- A lot of input lines. Hard to drive with uC (easy for FPGA). 

What is the [DPI interface][DPI] found in rPi boards? 
-
- Basically a VGA port without analog part. 
- Bare video output with 24 bit color depth, separate synchronization lines and even pixel clock. 
- No analog part. 24 bits color depth equals to 24 digital output lines. One line per bit. 8 lines (bits) per color. 
- Great for driving old LCD panels (ones with TTL input). Not compatible with modern panels (ones with LVDS input od display port). 
- Output resolution up to 1920x1080 (HD) @ 60hz. Pixel clock can be set to any value, up to 120Mhz. 
- Fast and reliable. DMA-like transfers from system RAM to output (GPIO pins) have priority over CPU issued data transfers. Basically if system run out of RAM bandwidth, DPI interface will work (refreshing VGA CRT monitor) and CPU will wait. 
- Important note, DPI interface IS ILLEGAL. High speed digital signals will cause some radio signal emission, interference, and similar problems. You need certification to produce and sell electronic devices but DPI interface without shielding wouldn't pass the test. Not a problem for hobbyists, huge deal for real business. Play at your own risk or ask local amateur radio operators for advice. 

How to drive LED matrix? 
-
- Send image to the panel, one line at the time, no PWM / brightness control, only on/off for each sub-pixel. 
- Select active line, store the data, enable output drivers (shine the LEDs). Wait certain amount of time. Preload next line while counting time. 
- Repeat through all display lines. 
- Do the soft PWM. Redraw whole screen again. This time shine the LEDs for half of the time and different set of data. This is called bit planes. 
- Done. Single frame displayed. Now draw second frame and another and another... Basically keep refreshing the screen. 

Available solutions for driving the matrix? 
-
- FPGA based driver. Buy it ([example 1][fp1]) or cook your own solution using FPGA ([example 2][fp2]), ([example 3][fp3]), ([example 4][fp4]). 
- SPI interface. Display takes serial data input, right? Wrong. Display takes 6 lanes of serial data. 3 lines (one per color - RGB) for upper half of the matrix and second set for lower half. All 6 SPI lines can be daisy chained in small display setup but that generates wiring problems and slows down the refresh rate. [Example 1][ex1], [example 2][ex2]. DMA controller and high speed SPI transmitter (SPI master) is mandatory. 
- Calculate all signals on CPU and bit-bang them to GPIO pins. This approach gives the best flexibility, but comes at a cost of high CPU usage. CPU have to keep perfect timing to achieve the effect. Doable ([example][url]) but not recommended on single CPU system like rPi zero. 
- Bit-bang approach with DMA? Here comes this project. Platform like rPi have very slow DMA controller (hzeller reported about 2Mhz output speed, way below 30Mhz display limit). However DPI interface don't have such speed limit. Just enable it and give it a try. 


[url]: https://github.com/hzeller/rpi-rgb-led-matrix
[DPI]: https://pinout.xyz/pinout/dpi
[fp1]: https://www.adafruit.com/product/1453
[fp2]: https://www.youtube.com/watch?v=Sq8SxVDO5wE
[fp3]: https://www.open-electronics.org/a-fpga-controlled-rgb-led-matrix-for-incredible-effects-the-hardware/
[fp4]: https://learn.adafruit.com/fpga-rgb-matrix?view=all
[ex1]: https://www.hackster.io/brian-lough/rgb-led-matrix-with-an-esp8266-a16fa9
[ex2]: https://github.com/GurraB/LED_display

Enabling the DPI interface. 
- 
In this setup You need 2 separate framebuffers. One for HDMI screen (just a canvas for the OS to draw on) and one for DPI interface to pull data from. Add these lines to `/boot/config.txt` or just copy-paste example config.txt and replace your existing one. 
```
# Uncomment this to enable infrared communication.
#dtoverlay=gpio-ir,gpio_pin=17
#dtoverlay=gpio-ir-tx,gpio_pin=18

#enable DPI output interface
dtoverlay=dpi24
framebuffer_priority=2
enable_dpi_lcd=1
#display_default_lcd=0

dpi_group=2
dpi_mode=87
max_framebuffers=2

dpi_output_format=0xc017
dpi_timings= 240 0 10 20 10 360 0 1 1 1 0 0 0 60 0 40000000 3
#            ^ horizontal    ^ vertical             ^ pixel clock
# Additional overlays and parameters are documented /boot/overlays/README
```
Where: 
- Horizontal resolution have to be greater than length of the string, times two. 64px wide panel need 130-140px at least. Too little might give You troubles with too high horizontal refresh rate. My panel gives up above 200hz. 
- Vertical resolution need to fit all lines we like to push in. 32px height panel requires 16 lines per bitplane (reduced brightness) and 16 misc lines on top. 
- Pixel clock - start with low value, then ramp up as high as You need. LED panel require 2 pixels for 1 clock pulse. Typical panels accepts up to 35Mhz so pixel clock can be as high as 70 millions (70000000). 

Hardware setup. 
-
- RGB LED matrix requires 3 separate inputs. 5V logic. 
  - Data input. 6 pins (2 sets of RGB) unique for each panel. 
  - Row control. 3, 4 or 5 lines, shared across all connected panels. Sometimes as simple as binary counting, sometimes have own shift register. 
  - Clock, Enable and Latch. 3 lines shared across all connected panels.
- DPI interface sends 5 signals. 3v3 logic. 
  - 24 bits as the image data. Easy to encode informations. 
  - Horizontal synch. 
  - Vertical synch. 
  - Pixel clock, always active. Basically unusable in this project. 
  - Data valid / data enable, basically a gating signal for pixel clock. 
- ![](img/schemat.png)
  - Voltage translators between rPi and matrix are mandatory. 
  - All data pins, clock and OE have to be attached to DPI data output (24 pins). 
  - Extra outputs on rPi DPI interface can be used (and abused) to some point but can't be reconfigured. Enable pin and horizontal synch can be used to count lines and/or latch data. Vertical synch can be used as synchronization and refresh rate indicator. Pixel clock is useless :( 
  - Pixel clock for the matrix have to stop as the latch pulse comes. This mean the clock signal have to be generated via DPI data output. Dedicated clock output can't be used. 
  - Output enable for the matrix also have to be generated, otherwise it's hard to achieve dimming. 
  - I decide to add binary counter to ease on code side. Horizontal sync triggers the latch pin and count up lines on the matrix. Lines of the matrix (counter) are synched with lines of framebuffer thanks to the reset input connected to vertical synch. 
  - All pins can be reconfigured across DPI data pins. Bare in mind GPIO 0, 1, 2, 3 have strict functions and can't be reconfigured. 

Theory of operation. 
-

Example 1. Can I have some output. 
...

Example 2. Displaying test pattern. 
...

Example 3. Mirror main screen. 
...

Example 4. Gain some speed. 
...

Example 5. NumPy'fy everything. 
...

Calculating the speed. 
Summary. 
...

