from machine import Pin, PWM#, deepsleep

pin4 = Pin(4, Pin.OUT, Pin.PULL_UP)

def builtInLed():
    return Pin(2, Pin.OUT)