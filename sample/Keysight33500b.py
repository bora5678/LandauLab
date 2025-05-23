# =============================================================================
# HOW TO USE THE Keysight33500B CLASS
# =============================================================================
# 1. Import the class:
#       from sample.Keysight33500b import Keysight33500B
#
# 2. Create an instance (this connects to the first available TCPIP instrument):
#       gen = Keysight33500B(dev=None, stat=None, msg=None)
#
# 3. Use the available methods to control the device:
#
#    - Turn output on/off:
#          gen.outp_on(channel=1)
#          gen.outp_off(channel=1)
#
#    - Select sine wave:
#          gen.selectSine(unit="VPP", amp=2.0, freq=1000, offset=0.0)
#
#    - Select DC wave:
#          gen.selectDC(offset=0.5)
#
#    - Select square wave:
#          gen.selectSquare(unit="VPP", amp=2.0, freq=1000, offset=0.0, dutycycle=50)
#
#    - Select noise wave:
#          gen.selectNoise(unit="VPP", amplitude=1.0, offset=0.0, bandwidth=10000)
#
#    - Enable burst mode:
#          gen.burst_mode(state="ON", ncycle=5)
#
#    - Set trigger:
#          gen.set_trigger(source="EXTernal")
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
#   selectSine(unit, amp, freq, offset)       - Select sine wave output
#   selectDC(offset)                          - Select DC output
#   selectSquare(unit, amp, freq, offset, dutycycle) - Select square wave output
#   selectNoise(unit, amplitude, offset, bandwidth)  - Select noise output
#   burst_mode(state, ncycle)                 - Enable/disable burst mode and set cycles
#   set_trigger(source)                       - Set trigger source
#   sendMANTrig()                             - Send manual trigger
#   disconnect()                              - Disconnect the device
# =============================================================================

# ...existing code...



import pyvisa



class Keysight33500B:
    """Class to define functions and values used for the control of Keysight 33500b"""

    def __init__(self):
        self.dev = None
        self.stat = None
        self.msg = None

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

    def selectSine(self, unit, amp, freq, offset):
        """Function to select the sine wave"""
        self.dev.write(f'VOLT:UNIT {unit}')
        self.dev.write('SOURce1:FUNCtion SINusoid')
        self.dev.write(f'SOURce1:VOLTage {amp}')
        self.dev.write(f'SOURce1:FREQuency {freq}')
        self.dev.write(f'SOURce1:VOLTage:OFFSet {offset}')

    def selectDC(self, offset):
        """Function to select the DC wave"""
        self.dev.write('SOURce1:FUNCtion DC')
        self.dev.write(f'SOURce1:VOLTage:OFFSet {offset}')

    def selectSquare(self, unit, amp, freq, offset, dutycycle):
        """Function to select the square wave"""
        self.dev.write(f'VOLT:UNIT {unit}')
        self.dev.write(f'SOURce1:VOLTage {amp}')
        self.dev.write('SOURce1:FUNCtion SQUare')
        self.dev.write(f'SOURce1:FREQuency {freq}')
        self.dev.write(f'SOURce1:VOLTage:OFFSet {offset}')
        self.dev.write(f'SOURce1:FUNCtion:SQUare:DUTYcycle {dutycycle}')

    def selectNoise(self, unit, amplitude, offset, bandwidth):
        """Function to select the noise wave"""
        self.dev.write(f'VOLT:UNIT {unit}')
        self.dev.write('SOURce1:FUNCtion NOISe')
        self.dev.write(f'SOURce1:VOLTage {amplitude}')
        self.dev.write(f'SOURce1:VOLTage:OFFset {offset}')
        self.dev.write(f'SOURce1:FUNCtion:NOISe:BANDwidth {bandwidth}')

    def burst_mode(self, state, ncycle):
        """Function to set the burst mode state ON|OFF"""
        self.dev.write('SOUR:BURS:MODE TRIG')
        self.dev.write(f'SOUR1:BURS:STAT {state}')
        self.dev.write(f'BURS:NCYC {ncycle}')

    def set_trigger(self, source):
        """Function to set the trigger"""
        #{IMMediate|EXTernal|TIMer|BUS}
        self.dev.write(f'TRIG:SOUR {source}')
        self.dev.write('BURS:STAT ON')
        self.dev.write('BURS:MODE TRIG')
        self.dev.write('OUTP:TRIG ON')


    def sendMANTrig(self):
        """Function to send the manual trigger"""
        self.dev.write(':TRIG')