
#

"""

Raspberry Pi Nano boot.py file for Rooftop Lighting Distibution Module (DM).

This is the 'bootloader' equivalent for the DM. It establishes a serial connection
to the Control Module (CM). Input data comes from the NeoPixel Din Data line.
Output data is current modulated onto the 48VDC supply line.

The RP2040 is clocked from the internal Ring Oscillator (ROSC). This clock's frequency
is unknown and varies subject to PVT variations. To provide stability the ROSC
frequency is adjusted and slaved to the bit rate of the NeoPixel data line to
achieve a CPU core clock frequency of 100 MHz +/- 2%.

After reset, boot.py spawns a task on the 2nd CPU. This task frequency locks the ROSC
to the Din data stream and creates a stream-like object device driver for the REPL.

Control is then passed to the REPL. At this point the CM can launch main.py, or (e.g)
load new firmware (a new main.py). 

After reset, boot.py:
(1) Waits for serial Din in WS2812 format.
    Ignores data, servos the RP2040 RCLK to 100 MHz (+/- 2%) using the serial data as a freq reference.
    After a 32 bit block has been received, modulates a current sink attached to the 48VDC supply to signal the Control Module.
    if the clock has sync'd, sends the control module a status byte.
    If the clock has not yet successfully sync'd, sends the control module a break code and loops to (1).

(2) Drops into REPL, using the now established serial connection.



https://docs.micropython.org/en/v1.9.2/pyboard/library/uos.html
uos.dupterm(stream_object)

    Duplicate or switch MicroPython terminal (the REPL) on the passed stream-like object. The given object must implement the readinto() and write() methods. If None is passed, previously set redirection is cancelled.



"""

import rp2
import _thread


DIN  = "Pin TBD"     # Input data. This is the NeoPixel data line.
DOUT = "Pin TBD"     # Output Data. A '1' driven on this line sinks current from the 48VDC supply.

bit_start_time = 0
bit_time       = 0   # measured WS2812 bit time
pulse_width    = 0   # measured WS2812 pulse high time
f_rtc_set      = False    # Real-time clock not initialized

def dinRisingEdgeIRQHandler():
    '''Din rising edge interrupt handler. Compute bit time.'''
    global bit_start_time, bit_time
    prev = bit_start_time
    #bit_start_time = <read sysclk>
    # bit_time = diff(prev, bit_start_time) # compensate for sysclk rollover
    
def dinFallingEdgeIRQHandler():
    '''Din falling edge interrupt handler. Compute pulse high time.'''
    global bit_start_time, pulse_width
    # edge_f = <read sysclk>
    # pulse_width = diff(bit_start_time, edge_f)
    
def roscFreqInc(percent):
    '''Increase ROSC frequency by approximately percent.'''
    pass

def roscFreqDec(percent):
    '''Decrease ROSC frequency by approximately percent.'''
    pass

def rtcSetUp(time_stamp):
    '''Configure RTC for 100 MHz clock. Set time to time_stamp.'''
    pass


#
# Main
#

# start REPL
# REPL should set RTC
# and optionally add/remove/change files (e.g. main.py)
# When done with housekeeping, launch main.py







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
