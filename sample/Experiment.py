from signal import pause
from sample.Keysight33500b import Keysight33500B, NoiseSettings, SineSettings
from sample.LorentzFit import LorentzFit
from sample.Yokogawa import Yokogawa
from sample.FSV import FSV, FSVSettings
import time
import numpy as np
from scipy.optimize import minimize 
from sample.LorentzFit import LorentzFit


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
    gs200 = Yokogawa()

    noise_cfg = NoiseSettings()
    sine_cfg = SineSettings()
    fsv_cfg = FSVSettings()

    # Other standalone variables
    sleep_duration = 0.2  # seconds
    detector_frequency = 0  # Hz

    #Fit Parameters
    beta = [500000, 1e2, 6.519e-6, 0, 1] # startparameters (quality, drive power, f_res, noise level p1, noise level p2)


    options = {
        'maxiter': 5000,
        'xatol': 1e-12,   # Equivalent to TolX
        'fatol': 1e-18,   # Equivalent to TolFun
        # 'TolBnd' has no direct equivalent in SciPy. If bounds are used, they're enforced separately.
    }

    # Example usage with minimize:
    # result = minimize(fun, x0, method='L-BFGS-B', bounds=bounds, options=options)

    #Control if accidentally drive too much
    if (noise_start > -5) or (noise_stop > -5) or (sine_start_0 > -40) or (sine_stop > 1) or (sine_step_0 > 1):

        raise Exception ('Out of safe range')

    #Start main loop:

    for _ in range(sine_cfg.start, sine_cfg.stop, sine_cfg.step):

        #Noise Measurement

        for j in range(noise_cfg.start, noise_cfg.stop, noise_cfg.step)
            ks.selectNoise(unit = noise_cfg.unit, amplitude = j, offset= noise_cfg.offset, bandwidth= noise_cfg.bandwidth)
            pause(1)

        fsv.configMaxAvg(sweep_points = fsv_cfg.points, center_freq = fsv_cfg.center_freq, freq_span = fsv_cfg.span, sweep_number = fsv_cfg.sweeps)
        amp, freq = fsv.scan(fsv_cfg.points)
        amp = np.sqrt(50) * 10 ** (amp.T / 20 - 3/2)

        # Define the "weird peak" frequencies and tolerance
        weird_peaks = np.array([6.518610e6, 6.518710e6, 6.518800e6, 6.51915e6, 6.52007e6])
        tolerance = 1e-5

        # Find indices close to weird peaks
        tf = np.any(np.isclose(freq, weird_peaks[None, :], atol=tolerance), axis=1)
        ind = np.where(tf)[0]

        # Find the index of the max amplitude not in tf
        amps_clean = amp[~tf]
        freqs_clean = freq[~tf]
        pos_max_clean = np.argmax(amps_clean)

        # Set beta[2] to the frequency at the max amplitude
        beta[2] = freqs_clean[pos_max_clean]  # Adjust index if beta has other elements

        fitted_parameter:list = LorentzFit(freqs_clean, amps_clean, beta, options)


