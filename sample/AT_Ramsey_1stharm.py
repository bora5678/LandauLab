## This script is used to measure the Ramsey sequence
# this script use the R&S spectrum analyser to monitor the mechanical
# resonance and the ringdown
# The Keithley 2401 control the applied voltage
# Keysight 81150a generates arb. pulses that can be generated and loaded from the software
# Benchlink Waveform Builder or the iqtools for a customized arb. pulse.
# Important note: the outputs of the DC source Keithley 2401 and the AWG 81150a
#                 should always be turned on. AWG should be in the trigger
#                 mode permanently

# The main sequence of this script is defined as followed:
# 1. define all the parameters
# 2. frequency regulation to get the initial frequency
# 3. load the arb. function either with iqtools or Benchlink Waveform
#    Builder
# 4. identify initial frequency -> trigger to turn on the ramp to determine
#    the final frequency
# 5. create a set of waiting time for the loop
# 6. in the loop: 2 steps of frequency regulations (noise and sinusoidal
#    drive)

# date: 19th October 2021
# created by: Anh Tuan, Le and Avishek Chowdhury
# python adaptation by: Lucian Ioan, Boar


import os
from datetime import datetime
import shutil
from sample.Keysight_pfag_81150 import Keysight81150
from sample.FSV import FSV
from sample.AT_fsv_findpeak import findpeak
from sample.AT_find_init_final_frequency_wf import find_resonances
from sample.LorentzFit import LorentzFit
from sample.Ramsey_pulse_3rdcorr import Ramsey_pulse_3rdcorr
from sample.AT_SweepAmp import AT_SweepAmp
from sample.Keysight33500b import Keysight33500B
from pymeasure.adapters import Adapter  # type: ignore
from sample.Yokogawa import Yokogawa
import time
import os
from datetime import datetime
import shutil
import numpy as np

def Ramsey_measurement():
    """Function to manage the current working file, and save locations."""

    workingdir = os.getcwd()
    workingFile = os.path.dirname(os.path.realpath(__file__))
    messordner = 'C:\\Messung\\Anh_Tuan\\3DCavity\\Coax\\Munich\\' # place for all measurements
    messung = 'Ramsey\\1stharm_corr\\repeat_afterVent\\4th_iter_p400mV\\' # name of measurement
    dt = datetime.now()
    ordner = os.path.join(messordner, messung, dt)
    os.makedirs(ordner, exist_ok=True)
    os.chdir(ordner)
    print('Current working directory:', os.getcwd())
    # copy the script to the measurement folder
    shutil.copy(workingFile, ordner)
    workingdir = os.getcwd()
    workingFile = os.path.dirname(os.path.realpath(__file__))
    messordner = 'C:\\Messung\\Anh_Tuan\\3DCavity\\Coax\\Munich\\' # place for all measurements
    messung = 'Ramsey\\1stharm_corr\\repeat_afterVent\\4th_iter_p400mV\\' # name of measurement
    dt = datetime.now()
    dt_str = dt.strftime("%Y%m%d_%H%M%S")
    ordner = os.path.join(messordner, messung, str(dt_str))
    os.makedirs(ordner, exist_ok=True)
    os.chdir(ordner)
    print('Current working directory:', os.getcwd())
    # copy the script to the measurement folder
    #shutil.copy(workingFile, ordner) #Permission Denied

    #Pre-define parameters
    # Keithley SourceMeter 24001
    keith_volt = -20.5 # [V]
    keith_volt_init = -20.5
    keith_regstep_init = 20e-4 # voltage regulation step for resonance frequency regulation
    keith_regstep = 20e-4 # voltage regulation step for resonance frequency regulation
    # Keysight 33500b
    NoiseAmplitudeLow = 0 # [dBm]
    NoiseAmplitudeHigh = 14 # [dBm]
    NoiseOffset = 0 # [V]
    NoiseBW = 8e6 # [Hz]
    NoiseUnit = 'DBM'
    SineUnit = 'DBM'
    SineAmplitude = -20
    # FSV
    fsv_points = 2001
    fsv_sweeps_noise = 3
    fsv_bw_noise = 10 #pre-measurement bandwidth
    fsv_points_low = 1001 # low number of points
    fsv_points_high = 2001 #large number of points

    fsv_span_noise0 = 20e3 # span for pre-noise measurement
    fsv_span_noise = 5e3 # span for noise measurement
    fsv_zerospan = 0 # span for ring down measurement

    fsv_bw_reg = 100 # bandwidth for regulation measurement
    fsv_sweeptime_reg = 1 # sweeptime for regulation measurement
    fsv_sweeps_reg = 1 # sweep count for regulation measurement

    average = 30 # number of averages
    fres_init = 7.075e6

    # Yokogawa GS200
    gs200 = Yokogawa()
    gs200.set_range(30)
    gs200.set_voltage(keith_volt)
   # Keysight 33500B
    key3350b = Keysight33500B()  
    key3350b.selectNoise(NoiseUnit, NoiseAmplitudeLow, NoiseOffset, NoiseBW)    

    #FSV
    fsv = FSV()
    fsv.span(fsv_span_noise0)
    fsv.fsv_sweeptype(2.0)
    fsv.bw(fsv_bw_noise, fsv_points_high, 1.0, 1)  # Note to self: sweeptime, the last parameter is not always used so maybe improve that
    fsv.configMaxAvg(fsv_points, fres_init, fsv_span_noise0, fsv_sweeps_noise)

    #Start to ramp up the noise drive
    key3350b.outp_on(1)
    for i in range(NoiseAmplitudeLow, NoiseAmplitudeHigh + 1, 1):
        key3350b.selectNoise(NoiseUnit, i, NoiseOffset, NoiseBW)
        time.sleep(1)
    
    ##INITIAL FREQUENCY REGULATION - noise driven resonance peak
    a, f = fsv.scan(fsv_points_high)
    pos = np.where(a == np.max(a))
    freg = f[pos[0][0]]
    delta = freg - fres_init

    if delta > 0:
        while delta >0:
            keith_volt -= 2*keith_regstep_init
            gs200.set_voltage(keith_volt)
            time.sleep(2)

            a, f = fsv.scan(fsv_points_high)
            pos = np.where(a == np.max(a))
            freg = f[pos[0][0]]
            delta = freg - fres_init
        keith_volt += keith_regstep_init
    elif delta < 0:
        while delta < 0:
            keith_volt += 2*keith_regstep_init
            gs200.set_voltage(keith_volt)
            time.sleep(2)

            a, f = fsv.scan(fsv_points_high)
            pos = np.where(a == np.max(a))
            freg = f[pos[0][0]]
            delta = freg - fres_init
        keith_volt -= keith_regstep_init
    gs200.set_voltage(keith_volt)

    finitpeak1, _ = findpeak(fres_init, fsv_span_noise0)
    finitpeak2, finitfit2 = findpeak(finitpeak1, fsv_span_noise)
    print(f" 1. Init Peak resonance frequency: {finitpeak2/1e6, 7}, MHz")
    print(f"1. Init Fit resonance frequency: {finitfit2/1e6, 7}, MHz")

    # calculate the ramp Voltage "deltaU"
    _ , deltaU =  AT_SweepAmp(finitfit2, -20)

    # Keysight PFAG 81150A
    AWGMode = 'DC'
    AWGInitial = 0.014

    # Keysight PFAG 81150A (Ramsey Pulse)
    TriggerMode = 'MAN'
    AWG_Final_Voltage = deltaU + 0.4
    AWGUnit = 'VPP'
    AWGLevel = AWG_Final_Voltage / 2
    AWGOffset = AWGLevel / 2
    AWGWaveform = 'VOLATILE'  # the ramp function is in volatile memory (use BenchLink WF Builder to create ramp function)

    # Frequency used to determine initial and final frequency
    AWGFreq_reg = 0.01
    # Frequency for the actual measurement
    AWGFreq = 110289 / 1e4

    # Other parameters
    freq_res = finitfit2
    freq_delta = 25e2  # f_final - f_initial
    c_eff = 23190      # conversion factor Hz/V
    V_final = keith_volt_init + (freq_delta) / c_eff
    Delta_pulse = 2 * abs(keith_volt_init - V_final) / AWG_Final_Voltage
    Delta_V = abs(keith_volt_init - V_final) / 2 + AWGInitial
    delay = 1

    # Note: the ratio of ramp and waiting duration is 1:10,000

    # Final measurement parameters
    fsv_bw_meas = 20e2      # resolution bandwidth of the spectrum analyzer
    fsv_sweeptime = 10e-3   # ringdown time
    fsv_delay = 0           # delay after the trigger for the FSV
    fsv_level = 0.9         # trigger level
    minsig = -75            # drive signal lower threshold
    maxsig = -72
    count = 0

    # Initialize devices

    fsv.span(fsv_span_noise0)
    fsv.fsv_sweeptype(2.0)
    fsv.bw(fsv_bw_noise, fsv_points_high, 1.0, 1)  # Note to self: sweeptime, the last parameter is not always used so maybe improve that
    fsv.configMaxAvg(fsv_points, finitfit2, fsv_span_noise0, fsv_sweeps_noise)

    # create an arbitrary pulse and use Ramsey_pulse function to load in to the AWG
    c = [0.272035, 0, 0, 0]
    d = [-0.815085, 0, 0, 0]
    _ , pulseform1 = Ramsey_pulse_3rdcorr(AWGFreq_reg, 20, Delta_pulse, c, d )
    awg = Keysight81150()
    awg.configure_arb_waveform(pulseform1, sample_rate=AWGFreq_reg*5e5, channel=1, name="Ramsey")