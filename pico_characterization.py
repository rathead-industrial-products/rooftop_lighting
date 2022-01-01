
#

"""

Experiment with the Raspberry Pi Pico to understand its behavior
and the Python SDK.

"""
import time
import machine
import rp2
import mitchell_lib_pico

from   mitchell_lib_pico import *

"""
Measure core clock frequency.
Verify RTC functionality.
Characterize ROSC freq adjusters.

"""



def roscCharactorize():
    """
        Set up output to gpio pin.
        Set up freq measurement using xosc as freq reference.
        Set default configuration.
            measure freq (nom 6.5 MHz)
        Shorten ring to double freq
            measure freq (nom 13 MHz)
        Change divider from 16 to 4
            measure freq (nom 52 MHz)
        Change drive strength stages 0-4, drives 0-3
            measure freq
        
        
    """
    
    # Reset drive in all stages to zero
    for stage in range(8):
        roscSetDrive(stage, 0)
    
    prev = freqCountKHz(CLOCKS_FC0_SRC_VALUE_ROSC_CLKSRC)
    print (roscGetDrive(), prev, 0)
    for strength in range(1,4):
        for stage in range(8):
            roscSetDrive(stage, strength)
            time.sleep(0.1)
            next = freqCountKHz(CLOCKS_FC0_SRC_VALUE_ROSC_CLKSRC)
            print (roscGetDrive(), next, (100*(next - prev))/prev)
            prev = next
# main
#measureFreqs()
roscCharactorize()



