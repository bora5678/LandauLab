
from sample.Keysight33500b import Keysight33500B, NoiseSettings, SineSettings
from sample.LorentzFit import fit_lorentzian
from sample.Yokogawa import Yokogawa
from sample.FSV import FSV, FSVSettings
import time
import numpy as np
from scipy.optimize import minimize 
import matplotlib.pyplot as plt
from time import perf_counter
import threading

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
    

def measurement():
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

    #Fit Parameters
  #  beta = [500000, 1e2, 6.519e-6, 0, 1] # startparameters (quality, drive power, f_res, noise level p1, noise level p2)


    options = {
        'max_nfev': 5000,
        'xtol': 1e-12,   # Equivalent to TolX
        'ftol': 1e-18,   # Equivalent to TolFun
        # 'TolBnd' has no direct equivalent in SciPy. If bounds are used, they're enforced separately.
    }

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

        plt.plot(time_array, power_array,'o',  label=f"ringdown at {int(i)} dBm.fig")
        plt.autoscale
        plt.legend()
        plt.grid(True)  # Optional: add grid like MATLAB
        plt.xlabel("Time")  # Optional
        plt.ylabel("Power")  # Optional
        plt.title(f"Measurement at {i} dBm")
        plt.show()


