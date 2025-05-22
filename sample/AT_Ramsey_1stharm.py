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

def directory_management():
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
