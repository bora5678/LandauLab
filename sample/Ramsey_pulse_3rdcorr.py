import numpy as np

def Ramsey_pulse_3rdcorr(freq, t_w, delta, c, d):
    """
    Generates the Ramsey pulse sequence.
    freq: Output frequency of AWG in Hz
    t_w: Waiting time in ms
    delta: Offset for ramp down sequence
    c, d: Arrays of coefficients (length 4)
    Returns:
        time: time array (seconds)
        pulse: pulse amplitude array
    """
    numtot = 500000
    t_init = 1000
    ratio_pulse = 1e4
    t_ramp = numtot / ratio_pulse
    t_wait = freq * numtot * t_w / 1e6
    t0 = t_ramp + t_init
    t1 = t_wait + t0
    t2 = 2 * t_ramp + t_wait + t_init
    a = -1 + delta
    numslope = 1000
    numend = t_init
    t_constant = numtot - (numslope + numend)
    t_slope = t_constant + numslope
    t_end = t_slope + numend

    t = np.arange(0, numtot)
    time = t / (numtot - 1) / freq

    # Piecewise pulse definition
    pulse = np.zeros_like(t, dtype=float)

    # Section 1: t < t_init
    idx1 = t < t_init
    pulse[idx1] = -1

    # Section 2: t_init <= t < t0
    idx2 = (t >= t_init) & (t < t0)
    tt = (t[idx2] - t_init) / t_ramp * np.pi
    pulse[idx2] = -1 * (
        np.cos(tt)
        + c[0] * (1 - np.cos(2 * 1 * tt))
        + c[1] * (1 - np.cos(2 * 2 * tt))
        + c[2] * (1 - np.cos(2 * 3 * tt))
        + c[3] * (1 - np.cos(2 * 4 * tt))
        + d[0] * np.sin(2 * 1 * tt)
        + d[1] * np.sin(2 * 2 * tt)
        + d[2] * np.sin(2 * 3 * tt)
        + d[3] * np.sin(2 * 4 * tt)
    )

    # Section 3: t0 <= t < t1
    idx3 = (t >= t0) & (t < t1)
    pulse[idx3] = 1

    # Section 4: t1 <= t < t2
    idx4 = (t >= t1) & (t < t2)
    tt = (-1) * (t[idx4] - t1) / (t2 - t1) * np.pi
    pulse[idx4] = (1 - delta / 2) * (
        -1
        * (
            -np.cos(tt)
            + c[0] * (1 - np.cos(2 * 1 * tt))
            + c[1] * (1 - np.cos(2 * 2 * tt))
            + c[2] * (1 - np.cos(2 * 3 * tt))
            + c[3] * (1 - np.cos(2 * 4 * tt))
            + d[0] * np.sin(2 * 1 * tt)
            + d[1] * np.sin(2 * 2 * tt)
            + d[2] * np.sin(2 * 3 * tt)
            + d[3] * np.sin(2 * 4 * tt)
        )
        + delta / 2
    )

    # Section 5: t2 <= t < t_constant
    idx5 = (t >= t2) & (t < t_constant)
    pulse[idx5] = -1 + delta

    # Section 6: t_constant <= t < t_slope
    idx6 = (t >= t_constant) & (t < t_slope)
    pulse[idx6] = a - ((1 + a) / numslope) * (t[idx6] - t_constant)

    # Section 7: t_slope <= t <= t_end
    idx7 = (t >= t_slope) & (t <= t_end)
    pulse[idx7] = -1

    return time, pulse

# Example usage:
# freq = 1e6
# t_w = 1
# delta = 0.1
# c = [0, 0, 0, 0]
# d = [0, 0, 0, 0]
# time, pulse = Ramsey_pulse_3rdcorr(freq, t_w, delta, c, d)