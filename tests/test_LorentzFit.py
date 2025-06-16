#used Github Copilot to generate the code below
import numpy as np
from sample.LorentzFit import LorentzFit

def test_lorentzfit_basic():
    """Test basic functionality of LorentzFit with synthetic data."""
    # Generate synthetic Lorentzian-like data
    freq = np.linspace(1e6, 2e6, 1000)
    # True parameters: q, d, f_res, n1, n2
    true_params = [80000, 1e8, 1.5e6, 0.1, 0.0]
    def lorentzian(x, q, d, f_res, n1, n2):
        numerator  = q * d
        denominator = q*x**2 - q*f_res**2 - 1j*x*f_res
        noise = np.abs(n1)*np.exp(1j*n2)
        return np.abs((numerator / denominator) + noise)
    signal = lorentzian(freq, *true_params) + np.random.normal(0, 0.01, freq.shape)

    # Run LorentzFit with empty start (should auto-select)
    yfit, popt, dcoef = LorentzFit(freq, signal, [])

    assert isinstance(yfit, np.ndarray)
    assert isinstance(popt, np.ndarray)
    assert isinstance(dcoef, np.ndarray)
    assert yfit.shape == signal.shape
    assert popt.size == 5
    assert dcoef.size == 6  # 5 std errors + adjusted R^2

def test_lorentzfit_with_start():
    """Test LorentzFit with a specific starting point."""
    freq = np.linspace(1e6, 2e6, 500)
    signal = np.ones_like(freq)
    start = [75000, 1e8, 1.5e6, 0, 1]
    yfit, popt, dcoef = LorentzFit(freq, signal, start)
    assert isinstance(yfit, np.ndarray)
    assert isinstance(popt, np.ndarray)
    assert isinstance(dcoef, np.ndarray)