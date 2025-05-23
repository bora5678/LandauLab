# =============================================================================
# HOW TO USE THE Keysight81150 CLASS
# =============================================================================
# 1. Import the class:
#       from sample.Keysight_pfag_81150 import Keysight81150
#
# 2. Create an instance (this connects to the first available TCPIP instrument):
#       gen = Keysight81150()
#
# 3. Use the available methods to control the device:
#
#    - Turn output on/off:
#          gen.outp_on(channel=1)
#          gen.outp_off(channel=1)
#
#    - Select waveform function and set DC offset:
#          gen.selectFunction(channel=1, name="SINusoid", offset=0.0)
#
#    - Set DC offset:
#          gen.setDCOffset(offset=0.5)
#
#    - Sweep DC offset finely between two values:
#          gen.setdc_fine(start=0.0, stop=1.0)
#
#    - Set voltage level and offset:
#          gen.setvoltage(unit="VPP", level=2.0, offset=0.0)
#
#    - Call arbitrary waveform:
#          gen.callArbVolatileFunc(channel=1, unit="VPP", level=2.0, offset=0.0, waveform="MYWAVE", freq=1000)
#
#    - Set trigger mode:
#          gen.setTriggerMode(mode="EXTernal")
#
#    - Send manual trigger:
#          gen.sendMANTrig()
#
#    - Disconnect the device:
#          gen.disconnect()
#
# =============================================================================
# Method Summary:
#   outp_on(channel)                          - Turn output on for a channel
#   outp_off(channel)                         - Turn output off for a channel
#   selectFunction(channel, name, offset)     - Select waveform function and set offset
#   setDCOffset(offset)                       - Set DC offset
#   setdc_fine(start, stop)                   - Sweep DC offset finely between two values
#   setvoltage(unit, level, offset)           - Set voltage level and offset
#   callArbVolatileFunc(channel, unit, level, offset, waveform, freq) - Call arbitrary waveform
#   setTriggerMode(mode)                      - Set trigger mode
#   sendMANTrig()                             - Send manual trigger
#   disconnect()                              - Disconnect the device
# =============================================================================



import pyvisa
import numpy as np
import time

class Keysight81150:
    """Class to control the Keysight 81150A Pulse Function Arbitrary Generator"""
    
    def __init__(self, dev=None, stat=None, msg=None):
        self.dev = dev
        self.stat = stat
        self.msg = msg

        rm = pyvisa.ResourceManager('@py')
        devices = rm.list_resources('?*')
        # Find the first device with 'TCPIP' in its name
        tcpip_devices = [dev for dev in devices if 'TCPIP' in dev.upper()]
        if not tcpip_devices:
            raise Exception("No TCPIP device found.")
        my_device = tcpip_devices[0]
        instrument = rm.open_resource(my_device)
        print(f"Connected to: {instrument.query('*IDN?')}")
        instrument.write('DISP On')
        self.dev = instrument

    def errorcheck(self):
        """Function to check for errors in the device"""
        status = self.dev.query('*STB?').strip()
        self.stat = status[1] if len(status) > 1 else status
        if self.stat != '0':
            self.msg = self.dev.query(':SYSTem:ERRor?').strip()
        else:
            self.msg = None

    def disconnect(self):
        """Function to disconnect the device"""
        self.dev.close()
        print("Device disconnected.")
    
    def outp_on(self, channel):
        """Function to turn on the output of the device"""
        self.dev.write(f'OUTP{channel}: ON')
        self.errorcheck()
        if self.msg:
            print(f"Error: {self.msg}")
        else:
            print(f"Output {channel} turned on.")
    
    def outp_off(self, channel):
        """Function to turn off the output of the device"""
        self.dev.write(f'OUTPut{channel}: OFF')
        self.errorcheck()
        if self.msg:
            print(f"Error: {self.msg}")
        else:
            print(f"Output {channel} turned off.")

    def selectFunction(self, channel, name, offset):
        """Function to select the waveform function"""
        #1 name [string]: {SINusoid|SQUare|RAMP|PULSe|NOISe|USER|DC
        self.dev.write(f'SOURce{channel}:FUNCtion {name}')
        self.dev.write(f'VOLT:OFFS {offset}')
     
    def setDCOffset(self, offset):
        """Function to set the DC offset"""
        self.dev.write(f'VOLT:OFFS {offset}')

    def setdc_fine(self, start, stop):
        """Function to set the DC offset in fine mode"""
        if start < stop:
            for dcvolt in np.range(start, stop+1, 0.01):
                self.dev.write(f'VOLT:OFFS {dcvolt}')
                time.sleep(0.01)
        elif start > stop:
            for dcvolt in np.range(start, stop-1, -0.01):
                self.dev.write(f'VOLT:OFFS {dcvolt}')
                time.sleep(0.01)

    def setvoltage(self, unit, level, offset):
        """Function to set the voltage level"""
        #set unit VPP|VRMS|DBM, caution put prime(') 'unit' when defining the
        #unit

        self.outp_off(unit, 1)
        self.dev.write(f'VOLT:AMPL {level}')
        self.dev.write(f'VOLT:OFFS {offset}')

    def callArbVolatileFunc(self, channel, unit, level, offset, waveform, freq):
        """Function to call the arbitrary waveform"""
        self.dev.write(f'VOLT:UNIT {unit}')
        self.dev.write(f'VOLT:AMPL {level}')
        self.dev.write(f'VOLT:OFFS {offset}')
        self.dev.write(f'SOURce{channel}:FUNCtion:ARB USER')
        self.dev.write(f':FUNC1:USER {waveform}')
        self.dev.write(f'FREQ {freq}')

    def setTriggerMode(self, mode):
        """Function to set the trigger mode""" #{IMMediate|INTernal[1]|INTernal[2]|EXTernal|BUS| MANual}
        self.dev.write(f'ARM:SOUR1 {mode}')
    
    def sendMANTrig(self):
        """Function to send the manual trigger"""
        self.dev.write(':TRIG')
      