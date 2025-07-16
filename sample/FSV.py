
#*IDN?                   # Query instrument identification
#:INIT                   # Start measurement
#:ABOR                   # Abort measurement
#:SWE:TYPE FFT           # Set sweep type to FFT
#:TRIG:SOUR EXT          # Set trigger source to external

# =============================================================================
# HOW TO USE THE FSV CLASS
# =============================================================================
# 1. Import the class:
#       from sample.FSV import FSV
#
# 2. Create an instance (this connects to the first available TCPIP instrument):
#       fsv = FSV()
#
# 3. Configure and control the device using the available methods:
#
#    - Set trigger:
#          fsv.trigger(mode=1, delay=0.01, polarity=1, level=-10)
#
#    - Set sweep type:
#          fsv.fsv_sweeptype(sweep_type=2.0)  # 0.0: Auto FFT, 1.0: Sweep, 2.0: FFT
#
#    - Start a scan:
#          fsv.startscan(modevalue=0.0, sweepnumber=1)  # Single sweep
#
#    - Set frequency span:
#          fsv.span(freq_span=1e6)  # Set span to 1 MHz
#
#    - Perform a scan and get data:
#          amplitude, frequency = fsv.scan(points=2001)
#          print("Amplitude:", amplitude)
#          print("Frequency:", frequency)
#
#    - Configure for measurement:
#          fsv.configMaxAvg(sweep_points=2001, center_freq=1e6, freq_span=1e5, sweep_number=3)
#
#    - Set bandwidth and sweep time:
#          fsv.bw(bandwidth=100, sweeppoints=2001, sweepvalue=1.0, sweeptime=1)
#
# 4. Close the connection when done (optional, but recommended):
#       fsv.device.close()
#
# =============================================================================
# Method Summary:
#   trigger(mode, delay, polarity, level)      - Configure trigger settings
#   fsv_sweeptype(sweep_type)                  - Set sweep mode (Auto FFT, Sweep, FFT)
#   startscan(modevalue, sweepnumber)          - Start a sweep (single or continuous)
#   span(freq_span)                            - Set frequency span
#   scan(points)                               - Perform a sweep and get amplitude/frequency arrays
#   configMaxAvg(sweep_points, center_freq, freq_span, sweep_number) - Configure analyzer for measurement
#   bw(bandwidth, sweeppoints, sweepvalue, sweeptime)                - Set bandwidth and sweep time
# =============================================================================

# ...existing code...

from RsInstrument import RsInstrument 
import numpy as np

class FSV:
    """Class to control the FSV"""
# add return values to the functions
# add error handling
    def __init__(self):

        instr_list = RsInstrument.list_resources('?*')
        print(instr_list)
        # Find the first device with 'TCPIP' in its name. Change code for other communication methods
       # tcpip_devices = [dev for dev in instr_list if 'TCPIP' in dev.upper()]
        #if not tcpip_devices:
         #   raise Exception("No TCPIP device found.")
        my_device = 'TCPIP0::10.157.136.135::inst0::INSTR'
        instrument = RsInstrument(my_device)
        print(f"Connected to: {instrument.query('*IDN?')}")
        self.device = instrument
    

    def trigger(self, mode, delay, polarity, level):
            """
        Configures the trigger for the device.
        mode: 0 - free run, 1 - external, 2 - IF power
        polarity: 0 - negative, 1 - positive
        """

            # Set trigger source
            self.device.write(f'TRIG:SOUR {mode}')
            
            # Set trigger delay and polarity
            self.device.write(f'TRIG:HOLD {delay}')
            self.device.write(f'TRIG:SLOP {"POS" if polarity == 1 else "NEG"}')
            
            # If external trigger, set level
            if mode == 1:
                self.device.write(f'TRIG:LEV {level}')

    def fsv_sweeptype(self, sweep_type):
        """
        Sets the FSV sweep mode.
        sweep_type: 0.0 - Auto FFT, 1.0 - Sweep, 2.0 - FFT
        """
        # Map numeric type to SCPI command string (adjust as needed for your instrument)
        if sweep_type == 0.0:
            mode = 'AUTO'
        elif sweep_type == 1.0:
            mode = 'SWE'
        elif sweep_type == 2.0:
            mode = 'FFT'
        else:
            raise ValueError("Invalid sweep_type")

        self.device.write(f":SWE:TYPE {mode}")
    
    def startscan(self, modevalue, sweepnumber):
        """
        Starts a sweep on the FSV spectrum analyzer.
        Parameters:
            device: Instrument session (PyVISA or RsInstrument object)
            modevalue: 0.0 for single sweep, 1.0 for continuous sweep
            sweepnumber: Number of sweeps to perform
        """
        # Set sweep mode: single or continuous
        if modevalue == 0.0:
            self.device.write(":INIT:CONT OFF")  # Single sweep
            # Start sweep
            self.device.write(":INIT")
            self.device.query("*OPC?")  # Waits until operation complete
            self.device.write(":FORM ASC")
            amp_data = self.device.query(":TRAC? TRACE1")
            act_amp = np.array([float(i) for i in amp_data.strip().split(',')])
            points = int(self.device.query(":SWE:POIN?"))  # holt Anzahl der Sweep-Punkte vom Gerät


            start_freq = float(self.device.query(":FREQ:START?"))
            stop_freq = float(self.device.query(":FREQ:STOP?"))
            act_freq = np.linspace(start_freq, stop_freq, points)

            return act_amp, act_freq

        else:
            self.device.write(":INIT:CONT ON")   # Continuous sweep
            # Set number of sweeps (if supported)
            self.device.write(f":SWE:COUN {int(sweepnumber)}")
            # Start sweep
            self.device.write(":INIT")
            self.device.query("*OPC?")  # Waits until operation complete
            self.device.write(":FORM ASC")
            amp_data = self.device.query(":TRAC? TRACE1")
            act_amp = np.array([float(i) for i in amp_data.strip().split(',')])
            points = int(self.device.query(":SWE:POIN?"))  # holt Anzahl der Sweep-Punkte vom Gerät


            start_freq = float(self.device.query(":FREQ:START?"))
            stop_freq = float(self.device.query(":FREQ:STOP?"))
            act_freq = np.linspace(start_freq, stop_freq, points)

            return act_amp, act_freq

        

      
    # Usage example:
    # fsv_startscan(0.0, 1)  # Single sweep

    def span(self, freq_span):
        """
        Set the span for the device.
        span: span value
        """
        self.device.write(f':FREQ:SPAN {freq_span}')

    def scan(self, points):
        """
    Performs a sweep with the FSV and returns the frequency and amplitude arrays.
    Assumes the device is already configured.
    
    Parameters:
        device: Instrument session (PyVISA or RsInstrument object)
        points: Number of points in the sweep
    
    Returns:
        act_amp: Amplitude array
        act_freq: Frequency array
    """

        self.device.write(':INIT')
        self.device.query('*OPC?')

        self.device.write(":FORM ASC")
        amp_data = self.device.query(":TRAC? TRACE1")
        act_amp = np.array([float(i) for i in amp_data.strip().split(',')])


        start_freq = float(self.device.query(":FREQ:START?"))
        stop_freq = float(self.device.query(":FREQ:STOP?"))
        act_freq = np.linspace(start_freq, stop_freq, points)

        return act_amp, act_freq


    def __readscan(self, points):
        """Performs a sweep with the fsv and gives back the frequency and amplitude of the trace"""
        #Does the same as the scan function, I dont understand why Thuan wanted to have it

    def configMaxAvg(self, sweep_points, center_freq, freq_span, sweep_number):
        """Configures the FSV4 Spectrum analyzer for measurement"""
        #The valeus have to be set before performing the sweep

        self.device.write(f':SWE:POIN {sweep_points}')
        self.device.write(f':FREQ:CENT {center_freq}')
        self.device.write(f':FREQ:SPAN {freq_span}')
        self.device.write(f':SWE:COUN {sweep_number}')

    def bw(self, bandwidth, sweeppoints, sweepvalue, sweeptime):
        """Defines the bandwidth and sweeptime of the FSV
        1.0 - sweep time auto, 0.0 - sweep time manual
        """
        self.device.write(f':BAND:RES {bandwidth}') # double check the command
        self.device.write(f':SWE:POIN {sweeppoints}')
        
        if sweepvalue == 1.0:
            mode = 'AUTO'
        elif sweepvalue == 0.0:
            mode = 'Manual'
        else:
            raise ValueError("Invalid sweepvalue")
        self.device.write(f':SWE:MODE {mode}')
        if mode == 'Manual':
            self.device.write(f':SWE:TIME {sweeptime}')

    
    
#      function configZeroSpan(obj, center, points, bw, sweepTime)
#            fprintf(obj.dev,['FREQuency:CENTer ', num2str(center)]); % Set center frequency
#            fprintf(obj.dev,['FREQuency:SPAN ', num2str(0)]); % Set frequency span
#            fprintf(obj.dev,['SWEep:POINts ', num2str(points)]); % Set number of points
#            fprintf(obj.dev,['BANDwidth ', num2str(bw)]); % Adjust RBW
# %             fprintf(obj.dev,['SWEep:TIME:AUTO OFF ']); % Adjust sweepTime
#            fprintf(obj.dev,['SWEep:TIME ', num2str(sweepTime)]); % Adjust sweepTime
#            fprintf(obj.dev,'SWEep:COUNT 0'); % No averaging
#        end
        
    def configZeroSpan(self, center, points, bw, sweepTime):
        self.device.write(f'FREQuency:CENTer {center}')
        self.device.write(f'FREQuency:SPAN {0}')
        self.device.write(f'SWEep:POINts {points}')
        self.device.write(f'BANDwidth {bw}')
        self.device.write(f'SWEep:TIME {sweepTime}')
        self.device.write(f'SWEep:COUNT {0}')

    def startZeroSpan(self):
        # fprintf(obj.dev,'INITiate;*WAI'); % *WAI; Initiate measurement and until any prior commands have been completed before continuing on to the next command
        self.device.write(f'INITiate;*WAI')

    def getDataZeroSpan(self):
        #function [time, power] = getDataZeroSpan(obj)
        #    power = str2num(query(obj.dev,'TRACe:DATA? TRACE1'));
        #    time = str2num(query(obj.dev,'TRACe:DATA:X? TRACE1'));
        #end

        power = self.device.query('TRACe:DATA? TRACE1')
        time = self.device.query('TRACe:DATA:X? TRACE1')

        return power, time

    def singlesweep(self):
        """Sets number of sweeps to 1"""
        self.device.write('INIT:CONT OFF')

    def contsweep(self):
        """Sets continuous sweep"""
        self.device.write('INIT:CONT ON')


from dataclasses import dataclass

@dataclass
class FSVSettings:
    center_freq: float = 6.8922e6  # Hz
    span: float = 10e3
    points: int = 5000
    sweeps: int = 1
    bandwidth_ringdown: float = 1000
    bw: float = 1.0
    sweep_time: float = 0.3  # second


