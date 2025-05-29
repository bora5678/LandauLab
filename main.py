from sample.Keysight_pfag_81150 import Keysight81150
from sample.FSV import FSV
from sample.Yokogawa import Keithley2400_predefined_parameters
from sample.AT_fsv_findpeak import findpeak
from sample.AT_find_init_final_frequency_wf import find_resonances
from sample.LorentzFit import LorentzFit
from sample.Ramsey_pulse_3rdcorr import Ramsey_pulse_3rdcorr
from sample.AT_SweepAmp import AT_SweepAmp
from sample.Keysight33500b import Keysight33500b
import os
from datetime import datetime
import shutil

if __name__ == '__main__':

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

   