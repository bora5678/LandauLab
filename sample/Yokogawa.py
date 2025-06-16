#REWORK THIS CLASS
#Yokogawa DC source address: 'TCPIP0::169.254.98.45::inst0::INSTR'

import pyvisa
from pyvisa.errors import VisaIOError


class Yokogawa():
    """Class to predefine the Keithley2400 parameters."""

    def __init__(self):
        
        rm = pyvisa.ResourceManager()
        instrument = rm.open_resource('TCPIP0::169.254.98.45::inst0::INSTR')
        #print(f"Connected to: {instrument.query('*IDN?')}")
        self.dev = instrument
       
    def reconnect(self):
        rm = pyvisa.ResourceManager()  
        self.dev = rm.open_resource('TCPIP0::169.254.98.45::inst0::INSTR')
        self.dev.timeout = 100000000
        #print("Neu verbunden:", self.dev.query("*IDN?"))

    def set_voltage(self, voltage):
        """Sets the output voltage of the Yokogawa DC source."""
        try: 
            self.dev.write(f':SOUR:LEV:FIX {voltage}')
        except Exception as e:
            print("Session scheint abgelaufen. Versuche, erneut zu verbinden...")
            self.reconnect()
            self.dev.write(f':SOUR:LEV:FIX {voltage}')

    def set_range(self, range_value):
        """Sets the output range of the Yokogawa DC source."""
        self.dev.write(f':SOUR:RANG {range_value}')
   