from sample.Keysight_pfag_81150 import Keysight81150
from sample.FSV import FSV

if __name__ == '__main__':
    fsv = FSV()
    gen = Keysight81150()

    # The following line is unrelated to Keysight33500B and uses FSV as intended fsv.bw(bandwidth=100, sweeppoints=2001, sweepvalue=1.0, sweeptime=1)  # Set bandwidth and sweep time
    fsv.span(freq_span=1e6)  # Set frequency span to 1 MHz
    fsv.fsv_sweeptype(sweep_type=2.0)  # 0.0: Auto FFT, 1.0: Sweep, 2.0: FFT
    fsv.scan(points=2001)  # Perform a scan with 2001 points
    fsv.fsv_sweeptype(sweep_type=0.0)  # 0.0: Auto FFT, 1.0: Sweep, 2.0: FFT
    fsv.startscan(modevalue=0.0, sweepnumber=1)  # Single sweepq
