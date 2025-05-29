from sample.AT_fsv_findpeak import findpeak
from Keysight_pfag_81150 import Keysight81150
import time

def find_resonances(device1, device2, fres, fdelta, span1, span2, delay) -> tuple:
    """Pre-Measurement of the Landau-Zener in order to localize the positions of 
    the initiate and measurement resonances. Use AWG in DC mode to increase 
    to the final voltage."""

    fmeas = fres + fdelta  # Final frequency for measurement
    # Find the initial resonance frequency
    
    finitpeak1, fit = findpeak(span1, fres)
    finitpeak2, finitfit2 = findpeak(span2, finitpeak1 )

    key = Keysight81150()
    key.sendMANTrig()
    time.sleep(delay)  # Wait for the device to stabilize

    fmeaspeak1, fitmeas1 = findpeak(span1, fmeas)
    fmeaspeak2, fitmeas2 = findpeak(span2, fmeaspeak1)

    print(f"Peak measurement final frequency: {fmeaspeak2/1e6} MHz")
    print(f"Fit measurement final frequency: {fitmeas2/1e6} MHz")

    return finitpeak2, fmeaspeak2

