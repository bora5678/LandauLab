#REWORK THIS CLASS
#Yokogawa DC source address: 'TCPIP0::169.254.98.45::inst0::INSTR'

import pyvisa


class Keithley2400_predefined_parameters():
    """Class to predefine the Keithley2400 parameters."""

    def __init__(self):
        
        rm = pyvisa.ResourceManager('@py')
        instrument = rm.open_resource('TCPIP0::169.254.98.45::inst0::INSTR')
        print(f"Connected to: {instrument.query('*IDN?')}")
        self.dev = instrument