import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit

def fit_lorentzian(freq, amp):
    freq = np.asarray(freq)
    amp = np.asarray(amp)

    # Find indices of min and max amplitude
    max_idx = np.argmax(amp)
    min_idx = np.argmin(amp)
    amp_max = np.mean(amp[max_idx:max_idx+1])  # mean allows expansion via tol
    freq_high_ampl = freq[max_idx]
    omega_n_initial = freq_high_ampl

    # Estimate vertical offset
    amp_min = np.mean(np.concatenate([amp[:20], amp[-20:]]))
    nf_1 = min(np.mean(amp[:20]), np.mean(amp[-20:]))

    # Estimate Gamma
    # Below peak
    lower_mask = freq < freq_high_ampl
    freq_lower = freq[lower_mask]
    amp_lower = amp[lower_mask]
    lower_idx = np.argmin(np.abs(amp_lower - 0.5 * amp_max))
    lower_est = freq_lower[lower_idx]

    # Above peak
    upper_mask = freq > freq_high_ampl
    freq_upper = freq[upper_mask]
    amp_upper = amp[upper_mask]
    upper_idx = np.argmin(np.abs(amp_upper - 0.5 * amp_max))
    upper_est = freq_upper[upper_idx]

    gamma_initial = abs(upper_est - lower_est) / 2
    F_d_initial = amp_max * 2 * omega_n_initial

    # Fit only near peak
    filter_extension = 0.3
    filter_start = int((1 - filter_extension) * lower_idx)
    filter_stop = int((1 + filter_extension) * (max_idx + upper_idx))
    filter_start = max(0, filter_start)
    filter_stop = min(len(freq) - 1, filter_stop)
    freq_filtered = freq[filter_start:filter_stop]
    amp_filtered = amp[filter_start:filter_stop]

    # Lorentzian function (normalized)
    def lorentzian(x, omega_n, gamma, F_d):
        return F_d / np.sqrt((omega_n**2 - x**2)**2 + (2 * gamma * x)**2) + nf_1

    # Initial guess
    p0 = [omega_n_initial, gamma_initial, F_d_initial]

    # Fit
    popt, pcov = curve_fit(lorentzian, freq_filtered, amp_filtered, p0=p0, maxfev=5000)
    omega_n_fit, gamma_fit, F_d_fit = popt
    A_est = F_d_fit / (2 * omega_n_fit)
    Q = omega_n_fit / (2 * gamma_fit)

    # Plot
    plt.figure(figsize=(10, 6))
    plt.plot(freq, amp, 'o', label='Data', markersize=3)
    plt.plot(freq_filtered, amp_filtered, '*', color='#FF8800', label='Fitting Window')
    freq_dense = np.linspace(freq.min(), freq.max(), 10000)
    plt.plot(freq_dense, lorentzian(freq_dense, *popt), '-', label='Fitted Function')
    plt.xlabel("Frequency (Hz)")
    plt.ylabel("Amplitude (V)")
    plt.legend()
    plt.grid(True)
    plt.title("Lorentzian Fit")

    plt.show()

    return omega_n_fit, gamma_fit, Q
