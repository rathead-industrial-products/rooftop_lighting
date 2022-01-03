.program neopixel_rx

; neopixel data stream receiver
; 32 bit rgbw format - SK6812 timing
; T0H  - 0.300 +/- 0.150 us = 0.450 us max 0 pulse width
; T1H  - 0.600 +/- 0.150 us = 0.450 us min 1 pulse width
; TRST - 80 us
;
; pio clock = sys_clk @ 125 MHz / 8 ns
;
; pulse edge recognition has 2 instruction window plus 1 clock sampling uncertainty
; pulse edge recognition = actual edge +2/-0 clocks (+16/-0 ns)
;
; target data sample point is 450 ns after pulse edge recognition (56.25 clks)
; actual sample point is 55 +2/-0 clocks
; register y must be loaded with reset pulse width time TRST = 80 us / 10,000 clocks
;
; IN pin 0 is mapped to the GPIO connected to the neopixel data
; Autopush must be enabled with a threshold of 32

.wrap_target
    wait 1 pin 0
pulse_recognized:
    nop    [29]     ; 55-1 clock delay from pulse leading edge to data sample point
    nop    [23]
    in pins, 1      ; sample the data bit
    wait 0 pin 0    ; end of 0 or 1 pulse
    mov  x, y       ; initialize reset pulse width counter
wait_for_pulse:
    jmp pin, pulse_recognized
    jmp x--, wait_for_pulse
    mov  isr, null  ; reset recognized, sync input register to start of frame by clearing ISR counter
.wrap


