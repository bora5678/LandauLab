import numpy as np
from scipy.optimize import curve_fit

def lorentzian(x, q, d, f_res, n1, n2) -> np.ndarray:
    """Lorentzian function"""
    # q - quality, d - drive power, f_res, n1 - noise level p1, n2 - noise level p2
    numerator  = q * d
    denominator = q*x**2 - q*f_res**2 - 1j*x*f_res
    noise = np.abs(n1)*np.exp(1j*n2)
    return np.abs((numerator / denominator) + noise)

def LorentzFit(freq, signal, start) -> tuple:
    """Fit linear data with mechanical susceptibility (data in V proportional to displacement)"""
    x = np.reshape(freq, (-1,))
    y = np.reshape(signal, (-1,))

    index_max_sig = np.where(y = max(y))

    if np.size(start) == 0:
        start = [75000, 1e8, x(index_max_sig), 0, 1] # q - quality, d - drive power, f_res, n1 - noise level p1, n2 - noise level p2
    else:
        start[2] = x(index_max_sig)
    fit_options = {
    'max_nfev': 5000,      # Equivalent to MaxIter
    'ftol': 1e-18,         # Function tolerance (TolFun)
    'xtol': 1e-12,         # Parameter tolerance (TolX)
    }

    popt, pcov = curve_fit(lorentzian, x, y, p0=start, method='trf', **fit_options)
    
    yfit = lorentzian(x, *popt)
    ss_res = np.sum((y - yfit)**2)
    ss_tot = np.sum((y - np.mean(y))**2)
    r_squared = 1 - (ss_res / ss_tot)
    adjusted_r_squared = 1 - (1 - r_squared) * (len(y) - 1) / (len(y) - len(popt) - 1)
    standard_errors = np.sqrt(np.diag(pcov))
    dcoef = np.append(standard_errors, adjusted_r_squared)
   
    return yfit, popt, dcoef 