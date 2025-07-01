from pickle import FALSE
from sample.Experiment import find_initial_frequency, measurement
import matplotlib.pyplot as plt
import numpy as np

def dbm_to_vrms(dbm, R=50):

    """Convert dBm to RMS voltage"""
    dbm = np.array(dbm)
    amp_power_watts = 10 ** (dbm / 10) * 1e-3
    amp_voltage_rms = np.sqrt(amp_power_watts * R)
    return amp_voltage_rms

if __name__ == '__main__':
    """Main function that runs everything."""
    measurement()
