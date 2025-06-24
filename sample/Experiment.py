from sample.Keysight33500b import Keysight33500B
from sample.Yokogawa import Yokogawa
from sample.FSV import FSV
import time
import numpy as np


def find_initial_frequency() -> float:
    """Find the starting point of the measurement."""
    gs200 = Yokogawa()
    gs200.set_range(30)
    gs200.set_voltage(-20)
    time.sleep(1)  # Allow some time for the voltage to stabilize

    ks = Keysight33500B()
    ks.selectSine(unit="VPP", amp=0.1, freq=6.6647e6, offset=0.0)
    ks.outp_on(channel=1)
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

    amp = []
    freq = []

    a_peak = []
    f_peak = []

 

    gs200 = Yokogawa()
    gs200.set_range(30)
    gs200.set_voltage(-20)

    key = Keysight33500B()
    key.selectSine(unit="VPP", amp=0.1, freq=6.6647e6, offset=0.0)
    key.outp_on(channel=1)
    time.sleep(1)  # Allow some time for the signal to stabilize

    tau = 1

    for i in np.arange(-20, -12, 0.1):
        gs200.set_voltage(i)

        fsv = FSV()
        fsv.span(1e6)  
        fsv.bw(10, 2001, 1.0, 1)  
        fsv.fsv_sweeptype(0.0)
        fsv.configMaxAvg(2001, 7e6, 1e6, 1)  
        amp, freq = fsv.scan(2001)  

        a_peak.append(np.max(amp))
        pos = np.where(amp == np.max(amp))
        f_peak.append(freq[pos[0][0]])
   
        time.sleep(tau)

    fsv = FSV()
    fsv.span(1e6)  # Set span to 20 MHz
    fsv.bw(10, 2001, 1.0, 1)  # Set bandwidth to 0.2 MHz, sweep points to 2001
    fsv.fsv_sweeptype(0.0)
    fsv.configMaxAvg(2001, 7e6, 1e6, 1)  # Configure for measurement
  
    a,f = fsv.scan(2001)  # Perform a scan with 2001 points
    pos = np.where(a == np.max(a))
    freq_final = f[pos[0][0]]
    print(f)
    return freq_final, a_peak, f_peak