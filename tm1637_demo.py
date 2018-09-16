#!/usr/bin/env python
import os
import sys 
import time
from TM1637 import TM1637

def delay(ms):
    time.sleep( ms / 1000 )

def fancy_demo():

    print("Starting display test!")

    # CLK, DIO
    display = TM1637(18, 19)

    TEST_DELAY = 200

    SEG_DONE = [
	TM1637.SEG_B | TM1637.SEG_C | TM1637.SEG_D | TM1637.SEG_E | TM1637.SEG_G,           # d
	TM1637.SEG_A | TM1637.SEG_B | TM1637.SEG_C | TM1637.SEG_D | TM1637.SEG_E | TM1637.SEG_F,   # O
	TM1637.SEG_C | TM1637.SEG_E | TM1637.SEG_G,                           # n
	TM1637.SEG_A | TM1637.SEG_D | TM1637.SEG_E | TM1637.SEG_F | TM1637.SEG_G            # E
	]
    k = 0
    data = [ 0xff, 0xff, 0xff, 0xff]
    display.set_brightness(0x0f)

    # add segments on
    display.set_segments(data)

    # selectivally set different digits 
    data[0] = 0b01001001
    data[1] = display.encode_digit(1)
    data[2] = display.encode_digit(2)
    data[3] = display.encode_digit(3)

    for k in range(3, -1, -1):
        display.set_segments([data[0]], k)
        delay(TEST_DELAY)

    display.set_segments(data[2:], 2)
    delay(TEST_DELAY)

    display.set_segments(data[2:], 1)
    delay(TEST_DELAY)

    display.set_segments(data[1:], 1)
    delay(TEST_DELAY) 

    # show decimal numbers with/without leading zeroes
    lz = False
    for z in range(2):
        k = 0
        while k < 10000: 
            display.display(k, lz)
            delay(TEST_DELAY)
            k += 4 * k + 7
        lz = True
    
    # show decimla number whose length is smaller than 4
    for k in range(4):
        data[k] = 0
    display.set_segments(data)

    # run through all the dots
    for k in range(4):
        display.display(0, True, 4, 0, (0x80 >> k))
        delay(TEST_DELAY)

def simple_demo():
    print("Starting simple display test!")

    # construct display on pins 18, 19
    display = TM1637(18, 19)

    # test: write all segments 
    segments = [ 0xff, 0xff, 0xff, 0xff]
    display.set_brightness(0x0f, True)
    # all segments on 
    display.set_segments(segments)
    # print 123
    delay(1000)
    display.display(123, True)
    pass

if __name__ == "__main__":
    simple_demo()
    #fancy_demo()