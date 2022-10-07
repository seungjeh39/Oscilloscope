import RPi.GPIO as GPIO
import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import savgol_filter
from scipy.signal import argrelextrema
from time import sleep

import busio
import digitalio
import board
import adafruit_mcp3xxx.mcp3008 as MCP
from adafruit_mcp3xxx.analog_in import AnalogIn


# create spi bus
spi = busio.SPI(clock=board.SCK, MISO=board.MISO, MOSI=board.MOSI)

# create cs (chip select)
cs = digitalio.DigitalInOut(board.D22)

# create mcp object
mcp = MCP.MCP3008(spi, cs)

# create an analog input channel on pin 0
chan = AnalogIn(mcp, MCP.P0)

print("Setup Completed")

# while True:
#     print('Raw ADC Value: ', chan.value)
#     print('ADC Voltage: ' + str(chan.voltage) + 'V')
#     print("--------------------------------")
#     sleep(0.001)
    

def waveReader(dataVal, tStep):

    stdev = np.std(dataVal)
    maxVal = max(dataVal)
    minVal = min(dataVal)
    ratio = (maxVal - minVal) / stdev   # ily dspguide.com/ch2/2.htm
    if 1.8 < ratio < 2.2:
        return "Square"
    elif 2.6 < ratio < 3.0:
        return "Sine"
    elif 3.2 < ratio < 3.7:
        return "Triangle"

    

def freqReader(dataVolt, tStep):

    ndxCrossingOne = []
    for i in range(0, len(dataVolt)-1):
        if dataVolt[i] <= 1 and dataVolt[i+1] > 1:
            ndxCrossingOne.append(i)
    intervalSum = 0
    for i in range(0, len(ndxCrossingOne)-1):
        intervalSum += ndxCrossingOne[i+1] - ndxCrossingOne[i]
    avgPeriod = intervalSum / (len(ndxCrossingOne) - 1) * 0.0001
    freq = 1 / avgPeriod * 0.02
    return freq



dataVal = []  
dataVolt = []
t = 0.0
tStep = 0.0001

try:
    while True:
        # collect data points
        if len(dataVal) >= 200:
            dataVal.pop(0)
            dataVolt.pop(0)
        dataVal.append(chan.value)
        dataVolt.append(chan.voltage)
        t += tStep
        sleep(tStep)

        # run waveReader() & freqReader()
        if len(dataVal) > 100:
            print(waveReader(dataVal, tStep))
            print("Freq: ",freqReader(dataVolt, tStep))

except KeyboardInterrupt:
    x = np.arange(0,len(dataVal), 1)
    y = np.array(dataVal)
    plt.plot(x, y)
    plt.show()