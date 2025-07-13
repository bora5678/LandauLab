%% This script is used to measure the avoided crossing of the IP and OOP modes
% this script use the R&S spectrum analyser to monitor the mechanical 
% The Yokogawa GS200 control the applied voltage
% Keysight 33500B controls the noise drive

% The main sequence of this script is defined as followed:
% 1. define all the parameters
% 2. Configure equipments
% 3. Sweep the DC drive and measure the spectra for a specific freq range

% date: 7th March 2023
% created by: Avishek Chowdhury & Ahmed Barakat

%% Define directory of the file
workingDir = pwd; % directory of measurement-scripts
workingFile = [mfilename('fullpath'),'.m']; % filepath of current file
% Define directory
messordner = 'C:\Messung\Lucian\Avoided_Crossing\'; % place for all
dt = datestr(now, 'yyyy-mm-dd_HH-MM');
ordner = [messordner,dt];
mkdir(ordner);
cd(ordner); % change directory to 'ordner',
copyfile(workingFile, [mfilename,'.m'], 'f');
%%
% Pre-configuration of instruments
% Connect to the devices
Open_fsv;
gs200_open;% This function connects the device and saves a handle GS200_inst
FG = ks_33500b;

%% Pre-define parameters

% Yokogawa settings
DC_volt_init =-30 ; % [V]
DC_volt_final =-0; % [V]
DC_volt_step = 0.1;% [V]
sweep_points_vdc=1+(DC_volt_final-DC_volt_init)/DC_volt_step;
Voltage_matrix=DC_volt_init:DC_volt_step:DC_volt_final;

% Keysight 33500b for noise drive
NoiseAmplitudeLow = -30; % [dBm]
NoiseAmplitudeHigh = -5; % [dBm]
NoiseOffset = 0; % [V]
NoiseBW = 10e6; % [Hz]
NoiseUnit = 'DBM';

% FSV
fsv_points = 30000;% set to 20Hz resolution for 600kHz span
fsv_sweeps_noise=1;
fsv_span_noise = 500e3;
fsv_bw_noise = 2; % pre-measurement bandwidth
% freq_cent_IP = 7.1011e6;
% freq_cent_OOP = 6.893e6;
freq_cent=7e6;
freq_matrix=freq_cent-fsv_span_noise/2:fsv_span_noise/(fsv_points-1):freq_cent+fsv_span_noise/2;

%Define the averaging and lists
avg=3;
a1list=zeros(fsv_points,avg);
Spectot=zeros(sweep_points_vdc,fsv_points);

datetime

%% 
%configure FSV

% fsv_span(fsv, fsv_span_noise); % set FSV span
fsv_sweeptype(fsv, 2.0); % FFT mode (2.0)
fsv_bw(fsv, fsv_bw_noise, fsv_points, 1.0, 1); % sweep time auto (1.0)
fsv_configMaxAvg(fsv, fsv_points, freq_cent, fsv_span_noise, fsv_sweeps_noise);

% Set Keysight 33500b (noise drive)
selectNoise(FG, NoiseUnit, NoiseAmplitudeLow, NoiseOffset, NoiseBW);

% Set Yokogawa GS200
gs200_volt_mode(GS200_inst);% Set to volt source mode
 gs200_set_volt(GS200_inst,DC_volt_init);%Set initial voltage
 for ij= 0:-1:DC_volt_init
   gs200_set_volt(GS200_inst,ij);
   pause(3)
 end
% Start to ramp up the noise drive
outp_on(FG, 1);
for ii = NoiseAmplitudeLow:1:NoiseAmplitudeHigh
    selectNoise(FG, NoiseUnit, ii, NoiseOffset, NoiseBW);
    pause(1)
end


%%
% Sweeping the parametric pump Drive for a fixed pump frequency
    jj=0;
    
    %configure fsv
    fsv_configMaxAvg(fsv, fsv_points, freq_cent, fsv_span_noise, fsv_sweeps_noise);

    pause(3)
   

    for DC_volt=DC_volt_init:DC_volt_step:DC_volt_final
    
    jj=jj+1;

    gs200_set_volt(GS200_inst,DC_volt);%Set DC bias

    pause(0.1)

    %record the spectra with averaging
    for kl=1:1:avg
    [a1list(:,kl), ~] = fsv_scan(fsv, fsv_points);%record spectra
    end
    a1=mean(transpose(a1list)); %record mean spectra
    
    Spectot(jj,:)=a1;
     
 
    end
    
    
%%
% Start to ramp down the noise drive
for ik = NoiseAmplitudeHigh:-1:NoiseAmplitudeLow
    selectNoise(FG, NoiseUnit, ik, NoiseOffset, NoiseBW);
    pause(1)
end

% Ramp down the DC bias
for ij= DC_volt_final:-DC_volt_step:DC_volt_init
  gs200_set_volt(GS200_inst,ij);
  pause(3)
end

%Turn off DC bias
%gs200_out_off(GS200_inst);

% Turning off the noise drive
outp_off(FG, 1);

%%
%Save all data
save('data_All.mat','Spectot','freq_matrix','Voltage_matrix');


datetime

%%
linamp = sqrt(50)*10.^((Spectot-30)/20);
x=DC_volt_init:DC_volt_step:DC_volt_final;
[X,Y]=meshgrid(x,freq_matrix);
contourf(X,Y,linamp','LineStyle','none')
clim([0 0.000005])
colorbar
