from sample.Keysight33500b import Keysight33500B
from sample.Yokogawa import Yokogawa
from sample.FSV import FSV
import time
import numpy as np


def find_initial_frequency() -> float:
    """Find the starting point of the measurement."""
    gs200 = Yokogawa()
    gs200.set_range(30)
    gs200.set_voltage(-18)

    fsv = FSV()
    fsv.span(1e6)  # Set span to 20 MHz
    fsv.bw(10, 2001, 1.0, 1)  # Set bandwidth to 10, sweep points to 2001
    fsv.fsv_sweeptype(0.0)
    fsv.configMaxAvg(2001, 7e6, 1e6, 1)  # Configure for measurement

    a, f = fsv.scan(2001)  # Perform a scan with 2001 points

    pos = np.where(a == np.max(a))
    return f[pos[0][0]]

def measurement():
    """Perform the measurement."""
    gs200 = Yokogawa()
    gs200.set_range(30)
    gs200.set_voltage(-18)

    key = Keysight33500B()
    key.selectSine(unit="VPP", amp=2.0, freq=6.6647e6, offset=0.0)
    key.outp_on(channel=1)
    time.sleep(1)  # Allow some time for the signal to stabilize

    tau = 1

    for i in range(-18, -12, 0.1):
        gs200.set_voltage(i)
        time.sleep(tau)

    freq_init = find_initial_frequency()

    fsv = FSV()
    fsv.span(20e6)  # Set span to 20 MHz
    fsv.bw(0.2e6, 2001, 1.0, 1)  # Set bandwidth to 0.2 MHz, sweep points to 2001
    fsv.fsv_sweeptype(0.0)
    fsv.configMaxAvg(2001, 7e6, 1e6, 1)  # Configure for measurement
  
    a,f = fsv.scan(2001)  # Perform a scan with 2001 points
    pos = np.where(a == np.max(a))
    freq_final = f[pos[0][0]]

    return freq_init, freq_final