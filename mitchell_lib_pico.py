
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
    return machine.mem32[reg]

def setRegister(reg, val):
    machine.mem32[reg] = val

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

def getGPIOFunc(gpio):
    '''Returns contents of GPIO control register'''
    return (getRegister(IO_BANK0_BASE+(8*gpio+4)))
    
def setGPIOFunc(gpio, func):
    '''Configures gpio to func'''
    setRegister(IO_BANK0_BASE+(8*gpio+4), 0x0000001f & func)

def getClkGPOUT0Ctl():
    '''Returns contents of GPIO control register'''
    return (getRegister(CLOCKS_BASE))
    
def setClkGPOUT0Ctl(src):
    '''Configures gpio to func'''
    setRegister(CLOCKS_BASE, 0x000001e0 & (src << 5))
    

def roscGetDrive():
    '''Returns a tuple of strength 0-3 for each stage 0-7'''
    a = getRegister(ROSC_BASE+ROSC_FREQA)        
    b = getRegister(ROSC_BASE+ROSC_FREQB)
    rslt = (a & 0x000f, (a & 0x00f0) >> 4, (a & 0x0300) >> 8, (a & 0x3000) >> 12, b & 0x000f, (b & 0x00f0) >> 4, (b & 0x0f00) >> 8, (b & 0xf000) >> 12)
    return (rslt)

def roscSetDrive(stage, strength):
    '''Stage 0-7, strength 0-3.
       Strength 1 decreases stage delay approx tbd % from strength 0.
       Strength 2 decreases stage delay approx tbd % from strength 1.
       Strength 3 decreases stage delay approx tbd % from strength 2.
    '''
    assert (stage >= 0 and stage <= 7 and strength >= 0 and strength <=3)
    if (stage <=3):
        stage_shift = 4 * stage
        mask = 0x0000ffff & (~(0x0f << stage_shift))        # clear passwd and target stage, keep other stages
        cur = getRegister(ROSC_BASE+ROSC_FREQA) & mask
        setRegister(ROSC_BASE+ROSC_FREQA, 0x96960000 | cur | (strength << stage_shift))
    else:
        stage_shift = 4 * (stage - 4)
        mask = 0x0000ffff & (~(0x0f << stage_shift))    # clear passwd and target stage, keep other stages
        cur = getRegister(ROSC_BASE+ROSC_FREQB) & mask
        setRegister(ROSC_BASE+ROSC_FREQB, 0x96960000 | cur | (strength << stage_shift))

        
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
    else: assert (false)
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
    print ("pll_sys  = %dkHz" % f_pll_sys)
    print ("pll_usb  = %dkHz" % f_pll_usb)
    print ("rosc     = %dkHz" % f_rosc)
    print ("clk_sys  = %dkHz" % f_clk_sys)
    print ("clk_peri = %dkHz" % f_clk_peri)
    print ("clk_usb  = %dkHz" % f_clk_usb)
    print ("clk_adc  = %dkHz" % f_clk_adc)
    print ("clk_rtc  = %dkHz" % f_clk_rtc)
    # Can't measure clk_ref / xosc as it is the ref
    
def driveClkOutGPIO(clk):
    '''Uses GPIOs 21,23,24,25'''
    


 

