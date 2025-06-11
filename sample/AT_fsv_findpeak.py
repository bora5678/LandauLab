from sample.FSV import FSV
import numpy as np
import time
from sample.LorentzFit import LorentzFit


def findpeak(span, freq) -> tuple:
    """This function performs searches for a peak in the 
    given frequency intervall and gives back the peak 
    frequency"""

    fsv = FSV()
    fsv.span(span)
    fsv.fsv_sweeptype(2.0)
    fsv.bw(10, 2001, 1.0, 1) #Note to self: sweeptime, the last parameter is not lways used so maybe improve that
    check = 1
    while np.abs(check - 1000)>10:
        fsv.configMaxAvg(2001, freq, span, 1)
        time.sleep(2)
        amplitude: np.ndarray 
        frequency: np.ndarray  
        amplitude, frequency = fsv.startscan(1.0, 3)
        pos = np.where(amplitude == np.max(amplitude))
        if np.abs(pos[0][0] - 1000) < 800:
            freq = frequency[pos[0][0]]
        check = pos[0][0]
    fpeak = freq

    lindata: tuple = (frequency, 10**((amplitude/20) - 3/2))
    yfit, coef, dcoef = LorentzFit(lindata[0], lindata[1], [])
    ffit = coef[2]

    return fpeak, ffit