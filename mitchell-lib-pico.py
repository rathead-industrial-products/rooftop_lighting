
#

"""

Utility functions for low-level access to the Raspberry Pi Pico.

"""

import machine, rp2

#
# Register Addresses
#
ROM_BASE = (0x00000000)
XIP_BASE = (0x10000000)
XIP_MAIN_BASE = (0x10000000)
XIP_NOALLOC_BASE = (0x11000000)
XIP_NOCACHE_BASE = (0x12000000)
XIP_NOCACHE_NOALLOC_BASE = (0x13000000)
XIP_CTRL_BASE = (0x14000000)
XIP_SRAM_BASE = (0x15000000)
XIP_SRAM_END = (0x15004000)
XIP_SSI_BASE = (0x18000000)
SRAM_BASE = (0x20000000)
SRAM_STRIPED_BASE = (0x20000000)
SRAM_STRIPED_END = (0x20040000)
SRAM4_BASE = (0x20040000)
SRAM5_BASE = (0x20041000)
SRAM_END = (0x20042000)
SRAM0_BASE = (0x21000000)
SRAM1_BASE = (0x21010000)
SRAM2_BASE = (0x21020000)
SRAM3_BASE = (0x21030000)
SYSINFO_BASE = (0x40000000)
SYSCFG_BASE = (0x40004000)
CLOCKS_BASE = (0x40008000)
CLOCKS_FC0_REF_KHZ = (0x80)
CLOCKS_FC0_MIN_KHZ = (0x84)
CLOCKS_FC0_MAX_KHZ = (0x88)
CLOCKS_FC0_DELAY = (0x8c)
CLOCKS_FC0_INTERVAL = (0x90)
CLOCKS_FC0_SRC = (0x94)
CLOCKS_FC0_STATUS = (0x98)
CLOCKS_FC0_RESULT = (0x9c)
CLOCKS_FC0_SRC_VALUE_PLL_SYS_CLKSRC_PRIMARY = (0x01)
CLOCKS_FC0_SRC_VALUE_PLL_USB_CLKSRC_PRIMARY = (0x02)
CLOCKS_FC0_SRC_VALUE_ROSC_CLKSRC            = (0x03)
CLOCKS_FC0_SRC_VALUE_ROSC_CLKSRC_PH         = (0x04)
CLOCKS_FC0_SRC_VALUE_XOSC_CLKSRC            = (0x05)
CLOCKS_FC0_SRC_VALUE_CLKSRC_GPIN0           = (0x06)
CLOCKS_FC0_SRC_VALUE_CLKSRC_GPIN1           = (0x07)
CLOCKS_FC0_SRC_VALUE_CLK_REF                = (0x08)
CLOCKS_FC0_SRC_VALUE_CLK_SYS                = (0x09)
CLOCKS_FC0_SRC_VALUE_CLK_PERI               = (0x0a)
CLOCKS_FC0_SRC_VALUE_CLK_USB                = (0x0b)
CLOCKS_FC0_SRC_VALUE_CLK_ADC                = (0x0c)
CLOCKS_FC0_SRC_VALUE_CLK_RTC                = (0x0d)
RESETS_BASE = (0x4000c000)
PSM_BASE = (0x40010000)
IO_BANK0_BASE = (0x40014000)
IO_QSPI_BASE = (0x40018000)
PADS_BANK0_BASE = (0x4001c000)
PADS_QSPI_BASE = (0x40020000)
XOSC_BASE = (0x40024000)
PLL_SYS_BASE = (0x40028000)
PLL_USB_BASE = (0x4002c000)
BUSCTRL_BASE = (0x40030000)
UART0_BASE = (0x40034000)
UART1_BASE = (0x40038000)
SPI0_BASE = (0x4003c000)
SPI1_BASE = (0x40040000)
I2C0_BASE = (0x40044000)
I2C1_BASE = (0x40048000)
ADC_BASE = (0x4004c000)
PWM_BASE = (0x40050000)
TIMER_BASE = (0x40054000)
WATCHDOG_BASE = (0x40058000)
RTC_BASE = (0x4005c000)
ROSC_BASE = (0x40060000)
ROSC_CTRL = (0x00)
ROSC_FREQA = (0x04)
ROSC_FREQB = (0x08)
ROSC_DIV = (0x10)
ROSC_STATUS = (0x18)
VREG_AND_CHIP_RESET_BASE = (0x40064000)
TBMAN_BASE = (0x4006c000)
DMA_BASE = (0x50000000)
USBCTRL_DPRAM_BASE = (0x50100000)
USBCTRL_BASE = (0x50100000)
USBCTRL_REGS_BASE = (0x50110000)
PIO0_BASE = (0x50200000)
PIO1_BASE = (0x50300000)
XIP_AUX_BASE = (0x50400000)
SIO_BASE = (0xd0000000)
SIO_FIFO_ST = (0x050)
SIO_FIFO_WR = (0x054)
SIO_FIFO_RD = (0x058)
PPB_BASE = (0xe0000000)



def getRegister(reg):
    return machine.mem32(reg)

def setRegister(reg, val):
    machine.mem32(reg) = val

def coreFifoRd():
    return (getRegister(SIO_BASE+FIFO_RD))

def coreFifoWr(val):
    return (setRegister(SIO_BASE+FIFO_WR))

def coreFifoStatus():
    return (getRegister(SIO_BASE+FIFO_ST))

def coreFifoEmpty():
    return ((coreFifoStatus() & ~0x01) == 0)

def coreFifoFull():
    return ((coreFifoStatus() & ~0x02) == 0)

def roscGetDrive():
    '''Returns a tuple of strength 0-3 for each stage 0-7'''
    a = getRegister(ROSC_BASE+ROSC_FREQA)        
    b = getRegister(ROSC_BASE+ROSC_FREQB)
    rslt = (a & 0x03, a & 0x0c >> 2, a & 0x30 >> 4, a & 0xc0 >> 6, b & 0x03, b & 0x0c >> 2, b & 0x30 >> 4, b & 0xc0 >> 6)
    return (rslt)

def roscSetDrive(stage, strength):
    '''Stage 0-7, strength 0-3.
       Strength 1 decreases stage delay approx tbd % from strength 0.
       Strength 2 decreases stage delay approx tbd % from strength 1.
       Strength 3 decreases stage delay approx tbd % from strength 2.
    '''
    assert (stage >= 0 and stage <= 7 and strength >= 0 and strength <=3)
    if (stage <=3):
        mask = 0x0000ffff & (~0x03 << stage)        # clear passwd and target stage, keep other stages
        cur = getRegister(ROSC_BASE+ROSC_FREQA) & mask
        setRegister(ROSC_BASE+ROSC_FREQA, 0x96960000 | cur | (strength << stage))        
    else:
        mask = 0x0000ffff & (~0x03 << (stage-4))    # clear passwd and target stage, keep other stages
        cur = getRegister(ROSC_BASE+ROSC_FREQA) & mask
        setRegister(ROSC_BASE+ROSC_FREQB, 0x96960000 | cur | (strength << (stage-4)))
        
def roscSetDiv(val):
    '''0 = divide by 32, otherwise divide by val.'''
    assert (val < 32)
    setRegister(ROSC_BASE+ROSC_DIV, 0xaa00000 | val)
    
def roscSetRange(range):
    '''Also enables the ROSC.'''
    assert (range == 'LOW' or range == 'MEDIUM' or range == 'HIGH')
    if range == 'LOW': code = 0xfa4
    if range  == 'MEDIUM': code = 0xfa5
    if range  == 'HIGH': code = 0xfa7
    else assert (false)
    setRegister(ROSC_BASE+ROSC_CTRL, 0xd1e0000 | code)
    
def freqCountKHz(src):
    '''Copied from C SDK uint32_t frequency_count_khz(uint src). The reference is clk_ref. Doc syss accuracy is 1 KHz.'''
    while (getRegister(CLOCKS_BASE+CLOCKS_FC0_STATUS) & 0x00000100): pass    # RUNNING bit - wait for freq ctr to stop running
    setRegister(CLOCKS_BASE+CLOCKS_FC0_REF_KHZ, 48000)     # frequency of reference clock in KHz (clk_ref)
    setRegister(CLOCKS_BASE+CLOCKS_FC0_INTERVAL,15)     # highest resolution interval
    setRegister(CLOCKS_BASE+CLOCKS_FC0_MIN_KHZ, 0)
    setRegister(CLOCKS_BASE+CLOCKS_FC0_MAX_KHZ,0xffffffff)
    setRegister(CLOCKS_BASE+CLOCKS_FC0_SRC,src)     # start measurement of src using sys clk 
    while (getRegister(CLOCKS_BASE+CLOCKS_FC0_STATUS) & 0x00000010): pass    # DONE bit - wait for freq ctr finish
    return (getRegister(CLOCKS_BASE+CLOCKS_FC0_RESULT))

def measureFreqs():
    '''Copied from Example// hello_48MHz.c'''
    f_pll_sys  = freqCountKHz(CLOCKS_FC0_SRC_VALUE_PLL_SYS_CLKSRC_PRIMARY);
    f_pll_usb  = freqCountKHz(CLOCKS_FC0_SRC_VALUE_PLL_USB_CLKSRC_PRIMARY);
    f_rosc     = freqCountKHz(CLOCKS_FC0_SRC_VALUE_ROSC_CLKSRC);
    f_clk_sys  = freqCountKHz(CLOCKS_FC0_SRC_VALUE_CLK_SYS);
    f_clk_peri = freqCountKHz(CLOCKS_FC0_SRC_VALUE_CLK_PERI);
    f_clk_usb  = freqCountKHz(CLOCKS_FC0_SRC_VALUE_CLK_USB);
    f_clk_adc  = freqCountKHz(CLOCKS_FC0_SRC_VALUE_CLK_ADC);
    f_clk_rtc  = freqCountKHz(CLOCKS_FC0_SRC_VALUE_CLK_RTC);
    print ("pll_sys  = %dkHz\n" % f_pll_sys)
    print ("pll_usb  = %dkHz\n" % f_pll_usb)
    print ("rosc     = %dkHz\n" % f_rosc)
    print ("clk_sys  = %dkHz\n" % f_clk_sys)
    print ("clk_peri = %dkHz\n" % f_clk_peri)
    print ("clk_usb  = %dkHz\n" % f_clk_usb)
    print ("clk_adc  = %dkHz\n" % f_clk_adc)
    print ("clk_rtc  = %dkHz\n" % f_clk_rtc)
    # Can't measure clk_ref / xosc as it is the ref


 





CONFIGURATION_FILE = "rooftop_lighting_config.json"
ROOFTOP_LIGHTING_PORT = 7663        # 'roof' on telephone keypad
SYSTEM_HOSTS = ("roof_cm", "roof_dm")

# log files running as a linux service require an absolute path
LOG_PATH_BASE = "/home/pi/rooftop_lighting/server/logs/"
MASTER_LOG    = LOG_PATH_BASE + "master_log.txt"      # messages from all loggers
SERVER_LOG    = LOG_PATH_BASE + "server_log.txt"
CM_LOG        = LOG_PATH_BASE + "cm_log.txt"
DM_LOG        = LOG_PATH_BASE + "dm_log.txt"


class tempThread(threading.Thread):
    SAMPLE_INTERVAL = 60    # sample temperature once every minute

    def __init__(self):
        threading.Thread.__init__(self)
        self.daemon = True
        self.temp_indoor    = 0.0
        self.temp_outdoor   = 0.0
        self.temp_discharge = 0.0
        healthThread.registerCallback(self._jsonReport)

    def _jsonReport(self):
        temp = dict(temp=dict(indoor=self.temp_indoor, outdoor=self.temp_outdoor, discharge=self.temp_discharge))
        return temp

    def _readTempF(self, sensor):
        lines = ["empty list",]
        while lines[0].strip()[-3:] != 'YES':
            time.sleep(0.2)
            with open(sensor) as f:
                lines = f.readlines()
        equals_pos = lines[1].find('t=')
        if equals_pos != -1:
            temp_string = lines[1][equals_pos + 2:]
            temp_c = float(temp_string) / 1000.0
            temp_f = temp_c * 9.0 / 5.0 + 32.0
            return round(temp_f, 1)

    def run(self):
        server_log.info("tempThread running")

        # Set up 1-wire communications
        # There are two devices on the 1-wire bus
        # The Raspbian distribution supports 1-wire through a device file
        base_dir = '/sys/bus/w1/devices/'
        sensor_indoor    = base_dir + '28-000000030b19' + '/w1_slave'
        sensor_outdoor   = base_dir + '28-000000037af4' + '/w1_slave'
        sensor_discharge = base_dir + '28-000000028428' + '/w1_slave'

        while True:
            self.temp_indoor    = self._readTempF(sensor_indoor)
            self.temp_outdoor   = self._readTempF(sensor_outdoor)
            self.temp_discharge = self._readTempF(sensor_discharge)

            # add to log file
            record = time.strftime("%m/%d/%Y %H:%M") + "\t%.1f" % self.temp_indoor + "\t%.1f" % self.temp_outdoor + "\t%.1f" % self.temp_discharge
            temp_log.info(record)

            time.sleep(tempThread.SAMPLE_INTERVAL)


class viThread(threading.Thread):
    SAMPLE_INTERVAL = 60    # sample voltage and current once every minute
    READ_VIN = 0xD0
    READ_CUR = 0xF0

    def __init__(self):
        threading.Thread.__init__(self)
        self.daemon = True

    def run(self):
        global g_vi_latest
        global g_vi_lock

        server_log.info("viThread running")

        # Set up SPI communications
        cs = digitalio.DigitalInOut(board.D22)      # NC, ignored. SPI_CS0 is used
        comm_port = busio.SPI(board.SCK, MOSI=board.MOSI, MISO=board.MISO)
        device = adafruit_bus_device.spi_device.SPIDevice(comm_port, cs)

        command = bytearray(3)
        result  = bytearray(3)

        while True:
            with device as spi:
                command[0] = viThread.READ_VIN
                command[1] = 0x00
                command[2] = 0x00
                spi.write_readinto(command, result)

            adc_value = int.from_bytes(result, byteorder='big')>>7 # bits 8-19 are valid
            vin = (33 * adc_value) / 4096     # adc input is Vin/10

            with device as spi:
                command[0] = viThread.READ_CUR
                command[1] = 0x00
                command[2] = 0x00
                spi.write_readinto(command, result)

            adc_value = int.from_bytes(result, byteorder='big')>>7 # bits 8-19 are valid
            cur = (1000 * adc_value) / 4096      # adc input is 3.3V @ 1000 mA of current

            if vi_q.full(): # remove oldest item if queue full
                try:
                    vi_q.get_nowait()
                except:
                    pass    # ignore if something else emptied queue first

            try:
                vi_q.put_nowait((vin, cur))
            except:
                server_log.error("Unable to add record to vi_q")

            # update global variable with latest sample
            with g_vi_lock:
                g_vi_latest = (vin, cur)

            # add to log file
            record = time.strftime("%m/%d/%Y %H:%M")+"\t%.1f"%vin+"\t%d"%cur
            vi_log.info(record)

            time.sleep(viThread.SAMPLE_INTERVAL)


class fpLightingThread(threading.Thread):
    STD_COLOR     = { "RED" : npdrvr.COLOR_RED, "GREEN" : npdrvr.COLOR_GREEN, "BLUE" : npdrvr.COLOR_BLUE, "WHITE" : npdrvr.COLOR_WHITE }
    STD_INTENSITY = { "LOW" : npdrvr.INTENSITY_LOW, "MEDIUM" : npdrvr.INTENSITY_MEDIUM, "HIGH" : npdrvr.INTENSITY_HIGH }
    STROBE_ON_TIME      = 0.010     # 10 mS
    STROBE_INTERVAL     = 1.0       # flash every 1 second
    THROB_INTERVAL      = 4.0       # seconds from dark to set intensity and back to dark
    THROB_STEPS         = 20        # num-1 (steps include 0) of discrete intensities between dark and set intensity
    MARCH_POSTS         = 2         # MARCH pattern is 2 posts on, 2 posts off, stepping 1 post per interval
    MARCH_INTERVAL      = 1.0       # post pattern marches every second
    TWINKLE_INTERVAL    = 0.5       # sec

    def __init__(self):
        threading.Thread.__init__(self)
        self.daemon = True
        self.light_style = ("DISPLAY", "WHITE", "LOW", "STEADY")
        self.delay = 1.0      # 10 ms
        self.color = npdrvr.COLOR_WHITE
        self.intensity = npdrvr.INTENSITY_LOW
        self.strobe = False     # True = ON (flash), False = OFF
        self.throb  = False     # True = increasing intensity, False = decreasing intensity
        self.throb_step = 1     # Must be 0 < self.throb_step < THROB_STEPS
        self.march_on   = True  # True = turn post LEDs on, False = turn post LEDs off
        self.march_step = 0

    def _colorLookup(self, color):
        if color in self.STD_COLOR:
            pixel_color = self.STD_COLOR[color]
        elif color == "RAINBOW":
            pixel_color = npdrvr.wheel(random.randint(1, 255))
        else:
            pixel_color = npdrvr.COLOR_WHITE
        return pixel_color

    def _intensityLookup(self, intensity):
        return self.STD_INTENSITY.get(intensity, npdrvr.INTENSITY_LOW)

    def run(self):
        server_log.info("fpLightingThread running")

        # set LED string to default condition
        npdrvr.set_all_pixels(self.color, self.intensity)

        while True:

            # sleep until display needs updating
            # check for incoming messages, update light_style
            # do whatever is needed to display light_style

            time.sleep(self.delay)

            try:
                msg = lighting_cmd_q.get_nowait()
                lighting_cmd_q.task_done()
                self.light_style = msg
            except:
                pass

            if self.light_style[0] == "DISPLAY" :       # message type = (DISPLAY, COLOR, INTENSITY, PATTERN)

                # display color is one of (RED, GREEN, BLUE, WHITE, RAINBOW)
                self.color = self._colorLookup(self.light_style[1])

                # display intensity is one of (LOW, MEDIUM, HIGH)
                self.intensity = self._intensityLookup(self.light_style[2])

                # display pattern is one of (STEADY, STROBE, THROB, MARCH, TWINKLE)
                if   self.light_style[3] == "STEADY":
                    self.delay = 0.1
                    npdrvr.set_all_pixels(self.color, self.intensity)

                elif self.light_style[3] == "STROBE":
                    if self.strobe:
                        self.strobe = False
                        self.intensity = npdrvr.INTENSITY_OFF
                        self.delay = self.STROBE_INTERVAL
                    else:
                        self.strobe = True
                        self.delay = self.STROBE_ON_TIME
                    npdrvr.set_all_pixels(self.color, self.intensity)

                elif self.light_style[3] == "THROB":
                    if self.throb:                              # increasing intensity
                        self.throb_step += 1
                        if self.throb_step >= self.THROB_STEPS: # full intensity
                            self.throb = False                  # now start reducing intensity
                    else:                                       # decreasing intensity
                        self.throb_step -= 1
                        if self.throb_step <= 0:                # min intensity (off)
                            self.throb = True                   # now start increasing intensity
                    # scale intensity INTENSITY_LOW -> 1
                    intensity = npdrvr.INTENSITY_LOW + (((self.intensity - npdrvr.INTENSITY_LOW) * self.throb_step) / self.THROB_STEPS)
                    npdrvr.set_all_pixels(self.color, intensity)
                    self.delay = (self.THROB_INTERVAL / 2) / (self.THROB_STEPS + 1)

                elif self.light_style[3] == "MARCH":
                    pixel_list = npdrvr.get_all_pixels()
                    for i in reversed(range(npdrvr.N_LEDS_PER_POST, npdrvr.N_LEDS_PER_STRING[0])):  # scroll pixels one post
                        pixel_list[i] = pixel_list[i-npdrvr.N_LEDS_PER_POST]

                    npdrvr.set_all_pixels(self.color, 0.0)
                    '''

                    self.march_step += 1
                    if self.march_step >= self.MARCH_POSTS:
                        self.march_step = 0
                        self.march_on = not self.march_on   # toggle on/off state of post at start of string
                    if not self.march_on:
                        self.intensity = npdrvr.INTENSITY_OFF
                    for i in range(npdrvr.N_LEDS_PER_POST):
                        pixel_list[i] = npdrvr.set_intensity(self.color, self.intensity)
                    '''

                    npdrvr.copy_all_pixels(pixel_list)
                    self.delay = self.MARCH_INTERVAL

                elif self.light_style[3] == "TWINKLE":
                    pixel_list = npdrvr.get_all_pixels()
                    n_pixels = len(pixel_list)
                    for j in range(int(n_pixels/4)):     # randomly change state of 1/4 of the pixels
                        i = random.randint(0, n_pixels-1)
                        if pixel_list[i] == (0, 0, 0):
                            pixel_list[i] = npdrvr.set_intensity(self.color, self.intensity)
                        else:
                            pixel_list[i] = (0, 0, 0)
                    npdrvr.copy_all_pixels(pixel_list)
                    self.delay = self.TWINKLE_INTERVAL

                else:   # unrecognized pattern, reset to default
                    self.light_style[3] = "STEADY"
                    self.delay = 0.0
                    server_log.warning("Unrecognized lighting pattern = %s", self.light_style[3])

            elif self.light_style[0] == "LIGHTING":       # message type = (LIGHTING, FENCEPOST NUMBER, ORIENTATION, COLOR, BRIGHTNESS)
                self.color = self.light_style[3]
                self.intensity = self.light_style[4]
                pixel_list = npdrvr.get_all_pixels()
                i_start = pixel_index(int(int(self.light_style[1])), self.light_style[2], position=1)
                for i in range(i_start, i_start+npdrvr.N_LEDS_PER_POST):
                    pixel_list[i] = npdrvr.set_intensity(self.color, self.intensity)
                npdrvr.copy_all_pixels(pixel_list)

            else:   # unrecognized type, reset to default
                self.light_style = ("DISPLAY", "WHITE", "LOW", "STEADY")
                self.delay = 0.0
                server_log.warning("Unrecognized lighting message type = %s", self.light_style[0])

class healthThread(threading.Thread):
    # The health thread reports regularly a remote URL
    # The report is a JSON structure containing, as a minimum, the host name
    # Other threads can add key-value pairs by registering a callback that is
    # called every time this thread reports.
    #
    # Example:
    # {
    #   "host": "flowmeter",
    #   "vi": {
    #       "vin": 3.28,
    #       "cur": 0.12
    #   },
    #   "temp": {
    #       "indoor": 68.3,
    #       "outdoor": 47.5
    #   },
    # }
    HEARTBEAT_INTERVAL = 60    # report health every minute
    REMOTE_URL = "http://mindmentum.com/cgi-bin/ha.py"
    json_callback = []

    def __init__(self, host, node_t):
        threading.Thread.__init__(self)
        self.host_name = host
        self.node_type = node_t
        self.daemon = True

    @staticmethod
    def registerCallback(callback):
        healthThread.json_callback.append(callback)

    def run(self):
        server_log.info("healthThread running")

        while True:
            health_status = { 'host' : self.host_name }  # dictionary of health related parameters
            for callback in self.json_callback:     # append additional json data from other threads
                health_status.update(callback())

            # post health to remote server
            try:
                response = requests.post(self.REMOTE_URL, json=health_status)
                if (response.status_code != 200):
                    server_log.warning("Could not connect to mindmentum.com:", response.content)
            except:
                server_log.warning("Connection error exception with mindmentum.com")

            # report health to magic mirror
            # fireriser is out of magic mirror's local network
            if (self.node_type != "fireriser"):
                msg = ("HEALTH_NOTICE", health_status)  # message must be a list
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                try:
                    s.connect(("magicmirror", HOME_AUTOMATION_PORT))
                except:
                    server_log.warning("healthThread failed to report to magic mirror, socket could not be established.")
                else:
                    s.sendall(pickle.dumps(msg, pickle.HIGHEST_PROTOCOL))
                    s.close()

            time.sleep(self.HEARTBEAT_INTERVAL)



class serverThread(threading.Thread):
    def __init__(self, node_t):
        threading.Thread.__init__(self)
        node_type = node_t
        self.daemon = True

    def run(self):
        server_log.info("serverThread running")

        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind(('', ROOFTOP_LIGHTING_PORT)) # listen on all IP addresses on this host
        s.listen(5)
        server_log.info("Listening on port (%s, %d)", "''", HOME_AUTOMATION_PORT)

        while True:
            buf = b''
            client, addr = s.accept()   # block until connection request
            while True:
                data = client.recv(4096)
                if data:
                    buf += data
                if not data:
                    # client has sent message and shut down connection
                    break

            msg = pickle.loads(buf) # depickle network message back to a message list
            server_log.debug("Received message: %s", str(msg))
            msg_t = msg[0]

            # validate message can be handled by this node type
            if msg_t not in MSG_TYPES:
                server_log.warning("Unknown message type received: %s" % msg_t)
            else:
                if node_type not in MSG_TYPES[msg_t]:
                    server_log.warning("Message type %s cannot be handled by this node type" % msg_t)

                else:   # decode and respond to message
                    if msg_t == "VI_QUERY":
                        # fetch global variable with latest vi sample
                        with g_vi_lock:
                            (vin, cur) = g_vi_latest
                        client.sendall(pickle.dumps((vin, cur), pickle.HIGHEST_PROTOCOL))

                    elif msg_t == "SOUND":
                        # get mp3 file and drive output
                        pass

                    elif msg_t == "VI_HISTORY":
                        vi_list = []
                        if not vi_q.empty():
                            vi_list.append(vi_q.get_nowait())
                        client.sendall(pickle.dumps(vi_list, pickle.HIGHEST_PROTOCOL))

                    elif msg_t == "DISPLAY":
                        lighting_cmd_q.put(msg)

                    elif msg_t == "FLOW_QUERY":
                        # client.sendall() included in lock in case gal, etc are references to flow_t variables
                        with g_flow_lock:
                            gal  = flow_t.flowGal()
                            gpm  = flow_t.flowGPM()
                            zone = flow_t.flowZone()
                            client.sendall(pickle.dumps((gpm, gal, zone), pickle.HIGHEST_PROTOCOL))

                    elif msg_t == "FLOW_HISTORY":
                        with open('flowrecord.txt', 'r') as f:
                            history = f.readlines()
                            client.sendall(pickle.dumps(history.reverse(), pickle.HIGHEST_PROTOCOL))

                    elif msg_t == "HEALTH_NOTICE":
                        mm.nodeStatusHandler(msg[1])    # pass JSON payload
                        pass

            client.close()



#
# Main
#

host_name = socket.gethostname()
if not host_name[:7] in SYSTEM_HOSTS:   # strip DM identifier number
    node_type = 'unknown: ' + host_name
else:
    node_type = host_name[:7]

# log configuration
log_format  ='%(asctime)s ' + host_name + ' %(levelname)s %(message)s'
log_datefmt = '%m/%d/%Y %H:%M:%S '
log_formatter  = logging.Formatter(fmt=log_format, datefmt=log_datefmt)

# 256K max file size, 4 files max
# delay=True to prevent file from being created until used, so e.g. dm_log isn't created in CM
master_log_fh = logging.handlers.RotatingFileHandler(MASTER_LOG, maxBytes=(256*1024), backupCount=3, delay=True)
server_log_fh = logging.handlers.RotatingFileHandler(SERVER_LOG, maxBytes=(256*1024), backupCount=3, delay=True)
cm_log_fh     = logging.handlers.RotatingFileHandler(CM_LOG, maxBytes=(256*1024), backupCount=3, delay=True)
dm_log_fh     = logging.handlers.RotatingFileHandler(DM_LOG, maxBytes=(256*1024), backupCount=3, delay=True)

# master_log records eveything, level='DEBUG'
master_log_fh.setLevel('DEBUG')
master_log_fh.setFormatter(log_formatter)
server_log_fh.setLevel('INFO')
server_log_fh.setFormatter(log_formatter)
cm_log_fh.setLevel('INFO')
cm_log_fh.setFormatter(log_formatter)
dm_log_fh.setLevel('INFO')
dm_log_fh.setFormatter(log_formatter)

# configure and instantiate loggers
# don't use root logger
# https://www.electricmonk.nl/log/2017/08/06/understanding-pythons-logging-module
# master_log is the top of the hierarchy, root is not used
master_log = logging.getLogger('rl')
master_log.addHandler(master_log_fh)
master_log.setLevel(logging.DEBUG)

server_log = logging.getLogger('rl.server')
server_log.addHandler(server_log_fh)
if node_type == 'roof_cm':
    cm_log = logging.getLogger('rl.cm')
    cm_log.addHandler(cm_log_fh)
if node_type == 'roof_dm':
    dm_log = logging.getLogger('rl.cm')
    dm_log.addHandler(dm_log_fh)

server_log.info("")
server_log.info("SERVER STARTING...")
server_log.info("Host name is %s", host_name)
server_log.info("Node type is %s", node_type)

# start threads
if node_type in MSG_TYPES['DISPLAY']:
    fpl_t = fpLightingThread()
    fpl_t.start()
if node_type in MSG_TYPES['VI_QUERY']:
    vi_t = viThread()
    vi_t.start()
if node_type in MSG_TYPES['FLOW_QUERY']:
    flow_t = flowThread()
    flow_t.start()
if node_type in MSG_TYPES['TEMP_QUERY']:
    temp_t = tempThread()
    temp_t.start()
if node_type in MSG_TYPES['PLAY_AUDIO']:
    audio_t = audioThread()
    audio_t.start()


health_t = healthThread(host_name, node_type)
health_t.start()

server_t = serverThread(node_type)
server_t.start()

while True:
    pass
