
from sample.Keysight33500b import Keysight33500B, NoiseSettings, SineSettings
from sample.LorentzFit import LorentzFit, lorentzian
from sample.Yokogawa import Yokogawa
from sample.FSV import FSV, FSVSettings
import time
import numpy as np
from scipy.optimize import minimize 
import matplotlib.pyplot as plt


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

def measurement():
    """Perform the measurement."""

    ks = Keysight33500B()
    fsv = FSV()
  #  gs200 = Yokogawa()

    noise_cfg = NoiseSettings()
    sine_cfg = SineSettings()
    fsv_cfg = FSVSettings()

    # Other standalone variables
    sleep_duration = 0.2  # seconds
    detector_frequency = 0  # Hz

    #Fit Parameters
    beta = [500000, 1e2, 6.519e-6, 0, 1] # startparameters (quality, drive power, f_res, noise level p1, noise level p2)


    options = {
        'max_nfev': 5000,
        'xtol': 1e-12,   # Equivalent to TolX
        'ftol': 1e-18,   # Equivalent to TolFun
        # 'TolBnd' has no direct equivalent in SciPy. If bounds are used, they're enforced separately.
    }

    # Example usage with minimize:
    # result = minimize(fun, x0, method='L-BFGS-B', bounds=bounds, options=options)

    #Control if accidentally drive too much
    if (noise_cfg.start > -5) or (noise_cfg.stop > -5) or (sine_cfg.start_0 > -40) or (sine_cfg.stop > 1) or (sine_cfg.step_0 > 1):

        raise Exception ('Out of safe range')

    #Start main loop:

    for i in np.arange(sine_cfg.start, sine_cfg.stop+1, sine_cfg.step):

        #Noise Measurement

       
        for j in np.arange(noise_cfg.start, noise_cfg.stop+1, noise_cfg.step):
            ks.selectNoise(unit = noise_cfg.unit, amplitude = j, offset= noise_cfg.offset, bandwidth= noise_cfg.bandwidth)
            ks.outp_on()
            print(f'{j}')
            time.sleep(1)

        

        fsv.configMaxAvg(sweep_points = fsv_cfg.points, center_freq = fsv_cfg.center_freq, freq_span = fsv_cfg.span, sweep_number = fsv_cfg.sweeps)
        amp, freq = fsv.scan(fsv_cfg.points)
        amp = np.sqrt(50) * 10 ** (amp.T / 20 - 3/2)

        ks.outp_off()

        # Define the "weird peak" frequencies and tolerance
        weird_peaks = np.array([6.518610e6, 6.518710e6, 6.518800e6, 6.51915e6, 6.52007e6])
        tolerance = 1e-5
        # Make sure freq is a numpy array
        freq = np.array(freq)

        # Reshape freq to (5000, 1) so it broadcasts against (1, 5)
       

        # Find indices close to weird peaks
        tf = np.any(np.isclose(freq[:, None], weird_peaks[None, :], atol=tolerance), axis=1)
        ind = np.where(tf)[0]

        # Find the index of the max amplitude not in tf
        amps_clean = amp[~tf]
        freqs_clean = freq[~tf]
        pos_max_clean = np.argmax(amps_clean)

        # Set beta[2] to the frequency at the max amplitude
        beta[2] = freqs_clean[pos_max_clean]  # Adjust index if beta has other elements

        fitted_parameter:list = LorentzFit(freqs_clean, amps_clean, beta, options)

        print(fitted_parameter)

        plt.plot(freq, amp)
        plt.plot(freq, lorentzian(freq, *fitted_parameter))

        res_freq_fit = fitted_parameter[2]
        Q_fct = fitted_parameter[0]

        #Save data

        # fprintf('The resonance frequency of the string is at %.5f MHz\n',res_freq_fit/1e6);
        print(f'The resonance frequency of the string is at {res_freq_fit/1e6}')

        ##Sine Drive

        center_freq = res_freq_fit+detector_frequency
        ctr = 0

        ks.outp_on()

        fsv.configZeroSpan(center_freq, fsv_cfg.points, fsv_cfg.bandwidth, fsv_cfg.sweep_time)
        ks.selectSine(sine_cfg.unit, i, center_freq, sine_cfg.unit)
        

        fsv.startZeroSpan()
        tic = time.time()
        time.sleep(sleep_duration)
        ks.outp_off()
        toc = time.time()
        tic1 = time.time()
        t, power = fsv.getDataZeroSpan()
        toc1 = time.time()

        # Split string into list of floats
        time_array = np.array([float(x) for x in t.split(',')])
        power_array = np.array([float(x) for x in power.split(',')])

        


        power_rg = []
        time_rg = []

        power_rg.append(power_array)
        time_rg.append(time_array)

        print(f'Tau = {toc1 - tic1}')
          
        plt.figure(i)  # Create or switch to figure number ct

        print(f"Index i: {i} (type: {type(i)})")
        print(f'Power type:{type(power_array)}')
        print(f'Time type: {type(time_array)}')

        plt.plot(power_array, time_array,  label=f"ringdown at {int(i)} dBm.fig")
        plt.autoscale
        plt.legend()
        plt.grid(True)  # Optional: add grid like MATLAB
        plt.xlabel("Time")  # Optional
        plt.ylabel("Power")  # Optional
        plt.title(f"Measurement at {i} dBm")
        plt.show()


