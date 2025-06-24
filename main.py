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
    i = find_initial_frequency() 
    f, amp, freq = measurement()

    amp_lin = dbm_to_vrms(amp, R=50)

    print(f'Amplitudes vector: {amp_lin}')
    print(f'Freq vector: {freq}')
    print(f"Initial frequency: {i} Hz")
    print(f"Final frequency: {f} Hz")

    vlt = np.linspace(-20, -12, len(amp_lin))
    plt.scatter(vlt, amp_lin, color='blue', marker='o')                  
    plt.xlabel("Voltage")
    plt.ylabel("Amplitude(Vrms)")
    plt.title("Mechanical Mode")
    plt.grid(False)
    plt.show()
