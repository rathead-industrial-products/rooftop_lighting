
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
Start 2 threads, one in each core.
Stop the thread in Core0, drop into REPL.
See what happens with Core1.

*** Core1 continues to run when Core0 drops into REPL. ***
*** Clicking Thonny 'Stop' stops both cores. ***

"""


# main

import time, _thread, machine

def task(n, delay):
    led = machine.Pin(25, machine.Pin.OUT)
    for i in range(n):
        led.high()
        time.sleep(delay)
        led.low()
        time.sleep(delay)
    print('done')


_thread.start_new_thread(task, (200, 0.5))
for i in range (5):
    print (i)
    time.sleep(1)



