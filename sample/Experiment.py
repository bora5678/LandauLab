
from sample.Keysight33500b import Keysight33500B, NoiseSettings, SineSettings
from sample.LorentzFit import fit_lorentzian
from sample.Yokogawa import Yokogawa
from sample.FSV import FSV, FSVSettings
import time
import numpy as np
import matplotlib.pyplot as plt
from time import perf_counter
import threading
from sample.Keysight_pfag_81150 import Keysight81150, AWGSettings

def find_initial_frequency() -> float:
    """Find the starting point of the measurement."""
    gs200 = Yokogawa()
    gs200.set_range(30)
    gs200.set_voltage(-20)
    time.sleep(1)  # Allow some time for the voltage to stabilize

    ks = Keysight33500B()
    ks.selectSine(unit="VPP", amp=0.1, freq=6.6647e6, offset=0.0)
    ks.outp_on()
    time.sleep(1)  # Allow some time for the signal to stabilize

    fsv = FSV()
    fsv.span(1e6)  
    fsv.bw(10, 2001, 1.0, 1)  
    fsv.fsv_sweeptype(0.0)
    fsv.configMaxAvg(2001, 7e6, 1e6, 1)  

    a, f = fsv.scan(2001)  

    pos = np.where(a == np.max(a))

    print(f)

    return f[pos[0][0]]

def precise_delay(delay_sec):
    start = perf_counter()
    while perf_counter() - start < delay_sec:
        pass  # Busy wait

def sine_off(ks):
    ks.outp_off()

def scan(fsv):
    fsv.startZeroSpan()
    

def Ringdown_measurement():
    """Perform the measurement."""

    ks = Keysight33500B()
    fsv = FSV()
    gs200 = Yokogawa()

    noise_cfg = NoiseSettings()
    sine_cfg = SineSettings()
    fsv_cfg = FSVSettings()

    # Other standalone variables
    sleep_duration = 0.2  # seconds
    detector_frequency = 0  # Hz

    gs200.set_range(30)
    gs200.set_voltage(-20)

    #Start main loop:

    for i in np.arange(sine_cfg.start, sine_cfg.stop, sine_cfg.step):

        #Noise Measurement

        ks.outp_on()
        for j in np.arange(noise_cfg.start, noise_cfg.stop+1, noise_cfg.step):
            ks.selectNoise(unit = noise_cfg.unit, amplitude = j, offset= noise_cfg.offset, bandwidth= noise_cfg.bandwidth)
            
            print(f'{j}')
            time.sleep(1)

        
        fsv.bw(fsv_cfg.bw, fsv_cfg.points, 1.0, 2)
        fsv.configMaxAvg(sweep_points = fsv_cfg.points, center_freq = fsv_cfg.center_freq, freq_span = fsv_cfg.span, sweep_number = fsv_cfg.sweeps)
        amp, freq = fsv.scan(fsv_cfg.points)
        amp = np.sqrt(50) * 10 ** (amp.T / 20 - 3/2)
      #  time.sleep(2)
        ks.outp_off()
        #plt.plot(freq, amp)
        # Set beta[2] to the frequency at the max amplitude

        fitted_parameter:list = fit_lorentzian(freq, amp)

        print(fitted_parameter)

        
       # plt.plot(freq, lorentzian(freq, *fitted_parameter))

        res_freq_fit = fitted_parameter[0]
        Q_fct = fitted_parameter[2]

        #Save data

        # fprintf('The resonance frequency of the string is at %.5f MHz\n',res_freq_fit/1e6);
        print(f'The resonance frequency of the string is at {res_freq_fit/1e6}')

        ##Sine Drive

        center_freq = res_freq_fit+detector_frequency
        fsv.configZeroSpan(center_freq, fsv_cfg.points, fsv_cfg.bandwidth_ringdown, fsv_cfg.sweep_time)

        t1 = threading.Thread(target=scan, args=(fsv,))
        t2 = threading.Thread(target=sine_off, args=(ks,))

        

        ks.selectSine(sine_cfg.unit, -10, center_freq, sine_cfg.offset)

        ks.outp_on()
        precise_delay(1)
        
        t1.start()
        precise_delay(5.2)
        t2.start()

        t1.join()
        t2.join()

        power, t = fsv.getDataZeroSpan()
 

        # Split string into list of floats
        time_array = np.array([float(x) for x in t.split(',')])
        power_array = np.array([float(x) for x in power.split(',')])

        power_array = np.sqrt(50) * 10 ** (power_array / 20 - 1.5)
        print(power_array)
            
        plt.figure(i)  # Create or switch to figure number ct

        print(f"Index i: {i} (type: {type(i)})")
        print(f'Power type:{type(power_array)}')

        plt.plot(time_array, power_array,'o',  label=f"ringdown at {int(10)} dBm.fig")
        plt.autoscale
        plt.legend()
        plt.grid(True)  # Optional: add grid like MATLAB
        plt.xlabel("Time")  # Optional
        plt.ylabel("Power")  # Optional
        plt.title(f"Measurement at {i} dBm")
        plt.show()


def Landau_Zener():
    
    ks = Keysight33500B()
    fsv = FSV()
    gs200 = Yokogawa()
    awg = Keysight81150()

    noise_cfg = NoiseSettings()
    sine_cfg = SineSettings()
    fsv_cfg = FSVSettings()
    awg_cfg = AWGSettings()

    # Other standalone variables
    sleep_duration = 0.2  # seconds
    detector_frequency = 0  # Hz

    gs200.set_range(30)
    gs200.set_voltage(-20)

    #Reset fsv

    fsv.trigger('IMM', 0, 1, 0.9)
    fsv.singlesweep()

    #Initialize awg
    
    awg.setTriggerMode('IMM')
    awg.selectFunction(1, 'DC', 0)
    awg.setDCOffset(0)


    #Noise Measurement

    ks.outp_on()
    for j in np.arange(noise_cfg.start, noise_cfg.stop+1, noise_cfg.step):
        ks.selectNoise(unit = noise_cfg.unit, amplitude = j, offset= noise_cfg.offset, bandwidth= noise_cfg.bandwidth)
            
        print(f'{j}')
        precise_delay(1)

        
    fsv.bw(fsv_cfg.bw, fsv_cfg.points, 1.0, 2)
    fsv.configMaxAvg(sweep_points = fsv_cfg.points, center_freq = fsv_cfg.center_freq, freq_span = fsv_cfg.span, sweep_number = fsv_cfg.sweeps)
    amp, freq = fsv.scan(fsv_cfg.points)
    amp = np.sqrt(50) * 10 ** (amp.T / 20 - 3/2)
    

    fitted_parameter:list = fit_lorentzian(freq, amp)

    print(fitted_parameter)
    print(f'The resonance frequency of the string is at {fitted_parameter[0]/1e6}')
    #Search for peak at target Voltage:
    vlt = float(input('Target Voltage: '))
    f = float(input('Expected final freq: '))
    for i in np.arange(-20, vlt+1, 1):
        gs200.set_voltage(i)
        precise_delay(1)

    fsv.bw(fsv_cfg.bw, fsv_cfg.points, 1.0, 2)
    fsv.configMaxAvg(sweep_points = fsv_cfg.points, center_freq = f, freq_span = fsv_cfg.span, sweep_number = fsv_cfg.sweeps)
    amp_fin, freq_fin = fsv.scan(fsv_cfg.points)
    amp_fin = np.sqrt(50) * 10 ** (amp_fin.T / 20 - 3/2)
    

    fitted_parameter_fin:list = fit_lorentzian(freq_fin, amp_fin)
    land_freq=fitted_parameter_fin[0]
    print(land_freq)
    print(fitted_parameter_fin)

    for i in np.arange(vlt, -21, -1):
        gs200.set_voltage(i)
        precise_delay(1)


    #Prepare ramp function
 
    awg.outp_off(1)
    precise_delay(0.2)
    awg.callArbVolatileFunc(1, awg_cfg.AWGUnit, awg_cfg.AWGLevel, 0, 'AWG_S6', 1)
    precise_delay(0.2)
    
    awg.setTriggerMode('EXT')
   
    precise_delay(1)
    awg.outp_on(1)
    precise_delay(0.2)
  
    res_freq_fit = fitted_parameter[0]
    Q_fct = fitted_parameter[2]
    center_freq = res_freq_fit+detector_frequency
    fsv.configZeroSpan(land_freq, fsv_cfg.points, fsv_cfg.bandwidth_ringdown, fsv_cfg.sweep_time)
    fsv.trigger('EXT', 0, 1, 0.9)
    fsv.contsweep
    precise_delay(1)
    

    # Main measurement

    awg.outp_off(1)
    precise_delay(0.2)
    awg.setTriggerMode('MAN')
    precise_delay(1)
    
    awg.callArbVolatileFunc(1,awg_cfg.AWGUnit, awg_cfg.AWGLevel, awg_cfg.AWGOffset, awg_cfg.AWGWaveform, awg_cfg.AWGFreq)
    precise_delay(0.2)
    awg.outp_on(1)
    print('asdfas')
    precise_delay(5)

    ks.selectSine(sine_cfg.unit, -10, center_freq, sine_cfg.offset)
    precise_delay(1)
    ks.outp_on()

    awg.sendMANTrig()

    power, time = fsv.getDataZeroSpan()

    # Split string into list of floats
    time = np.array([float(x) for x in time.split(',')])
    power = np.array([float(x) for x in power.split(',')])

    power = np.sqrt(50) * 10 ** (power / 20 - 1.5)

    plt.plot(time, power,'o',  label=f"Landau Zener at {int(10)} dBm.fig")
    plt.autoscale
    plt.legend()
    plt.grid(True)  # Optional: add grid like MATLAB
    plt.xlabel("Time")  # Optional
    plt.ylabel("Power")  # Optional
    plt.title(f"Landau Zener")
    plt.show()

    #cleanup

    fsv.trigger('IMM', 0, 1, 0.9)
    awg.outp_off(1)
    fsv.singlesweep()
    ks.outp_off()
