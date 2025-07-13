clear;
close all;
%linamp = sqrt(50)*10.^((Spectot-30)/20);
%load Meas_5.05.mat
%load VDC=0_00000.mat

load C:\Messung\Lucian\Avoided_Crossing\2025-07-10_17-59\data_All.mat
Voltage_0 = Voltage_matrix;
freq_0 = freq_matrix;
linamp_0 = sqrt(50)*10.^((Spectot-30)/20);

load C:\Messung\Lucian\Avoided_Crossing\2025-07-10_19-48\data_All.mat

%freq_matrix=freq; Voltage_matrix=x; linamp=ampmap;
linamp = sqrt(50)*10.^((Spectot-30)/20);





figure;
imagesc(Voltage_matrix, freq_matrix, linamp');
axis xy;
colorbar;

centerX = -15;
centerY = 7e6;
zoomWidth = 6;
zoomHeight = 0.2e6;


xlim([centerX - (zoomWidth/2), centerX + (zoomWidth/2)]);
ylim([centerY - zoomHeight/2, centerY + zoomHeight/2]);

  
xl = xlim;
yl = ylim;

mask_1 = Voltage_matrix >= xl(1) & Voltage_matrix <= xl(2);
mask_2 = freq_matrix >= yl(1) & freq_matrix <= yl(2);
x_zoomed = Voltage_matrix(mask_1);
y_zoomed = freq_matrix(mask_2);
z = linamp';
z_zoomed = z(mask_2, mask_1);

imagesc(x_zoomed, y_zoomed, z_zoomed);
colorbar;

[x, y] = meshgrid(x_zoomed, y_zoomed);


%%find the start values for w1 and w2

%linamp_smooth = sgolayfilt(linamp_at_0, 11, 121); if it needs smoothing

figure;
plot(freq_0, linamp_0(2,:), 'o');
hold on;

amp0 = linamp_0(2,:);
freq0 = freq_0;
[w, l] = findpeaks(amp0, "MinPeakHeight",3e-6, "NPeaks",5); % w contains w1 and w2

w1 = freq0(l(1));
w2 = freq0(l(3));

plot(freq0(l(1)), w(1) , 'ro', 'MarkerSize', 8);
plot(freq0(l(3)), w(3), 'ro', 'MarkerSize', 8);


%% Isolate the dataset the fitting will be done on.
% We shall isolate a 2D Graph of the avoided Crossing from the 3D data we
% measured.


% Initialize result vectors
n = size(x_zoomed, 2);
x1_plus = zeros(n, 1);
x2_plus = zeros(n, 1);
x1_minus = zeros(n, 1);
x2_minus = zeros(n, 1);


for i = 1:n
    z_col = z_zoomed(:, i);
    mid_point = round(length(z_zoomed(:,i))/2);
    z_up = z_col(1:mid_point);
    z_down = z_col(mid_point+1:end);
    [peak_up, peak_up_ind] = max(z_up);
    [peak_down, peak_down_ind] = max(z_down);

    peak_down_ind = peak_down_ind + mid_point;

    x1_plus(i) = x_zoomed(i);
    x2_plus(i)= y_zoomed(peak_up_ind);
    
    x1_minus(i) = x_zoomed(i);
    x2_minus(i) = y_zoomed(peak_down_ind);

end

for j = length(x2_minus):-1:1
    if (x2_minus(j)>7.04e6)
        x2_minus(j)=[];
        x1_minus(j)=[];
    end
end
% x2_minus(1) = [];
% x1_minus(1) = [];
% x2_minus(1) = [];
% x1_minus(1) = [];
% x2_minus(5) = [];
% x1_minus(5) = [];
% x2_minus(5) = [];
% x1_minus(5) = [];
% x2_minus(5) = [];
% x1_minus(5) = [];
% x2_minus(5) = [];
% x1_minus(5) = [];
% x2_minus(5) = [];
% x1_minus(5) = [];
% x2_minus(5) = [];
% x1_minus(5) = [];
% x2_minus(5) = [];
% x1_minus(5) = [];
% x2_minus(5) = [];
% x1_minus(5) = [];
% x2_minus(5) = [];
% x1_minus(5) = [];
% x2_minus(5) = [];
% x1_minus(5) = [];
% x2_minus(5) = [];
% x1_minus(5) = [];
% x2_minus(3) = [];
% x1_minus(3) = [];
% x2_minus(2) = [];
% x1_minus(2) = [];
% x2_minus(2) = [];
% x1_minus(2) = [];
% 3

  figure;
    plot (x1_plus, x2_plus, 'o');
    hold on;
    plot (x1_minus, x2_minus, 'o');

%%find the avoided crossing
x2_plus_ac = max(x2_plus);
x1_plus_ac = mean((x1_plus(x2_plus == x2_plus_ac)));

x2_minus_ac = min(x2_minus);
x1_minus_ac = x1_minus(x2_minus == x2_minus_ac);

%@AC
omega_ac = ((min(x2_plus)^2+max(x2_minus)^2)/2); %squared

lambda_0 = sqrt(abs(x2_minus_ac^2 - omega_ac));
disp(['lambda = ', num2str(lambda_0)]);

gamma = sqrt(abs(2*omega_ac-2*sqrt(omega_ac^2-lambda_0^4)));
disp(['gamma = ', num2str(gamma)]);

gamma_approx = lambda_0^2/sqrt(omega_ac);
disp (['gamma_approx = ', num2str(gamma_approx)]);

gamma_read = abs(min(x2_plus)-max(x2_minus));
disp (['gamma_read = ', num2str(gamma_read)]);

dw1_0 = sqrt(abs(omega_ac-x2_plus_ac^2));
disp(['dw1_0 = ', num2str(dw1_0)]);

dw2_0 = sqrt(abs(x2_minus_ac^2-omega_ac));
disp(['dw2_0 = ', num2str(dw2_0)]);

%% Calculate the eigenfrequencies and fit them on our avoided Crossing


%w1_0 = 6.85e6;    % base frequency in Hz
%w2_0 = 7.1e6;
%dw1 = 0.5e6;        % voltage slope in Hz/V
%dw2 = -1e6;
%lambda = 20e5;     % coupling in Hz


p1_0= 143;
p2_0= 141;

vdc_ac=-15;%From Measurement


dw1_2 = @(p1, x) + 2*w1*p1*(x + vdc_ac).^2;%dw1_0.^2
dw2_2 = @(p2, x) - 2*w2*p2*(x + vdc_ac).^2;%dw2_0.^2

beta0 = [p1_0, p2_0, lambda_0];   

% Coupled mode frequencies 
omega_plus = @(p1, p2, lambda, x) sqrt(0.5*(w1.^2 + dw1_2(p1, x) + w2.^2 + dw2_2(p2, x)) + ...
                       0.5*sqrt((w2.^2 + dw2_2(p2, x) - w1.^2 - dw1_2(p1, x)).^2 + 4 * lambda^4));
omega_minus = @(p1, p2, lambda, x) sqrt(0.5*(w1.^2 + dw1_2(p1, x) + w2.^2 + dw2_2(p2, x)) - ...
                       0.5*sqrt((w2.^2 + dw2_2(p2, x) - w1.^2 - dw1_2(p1, x)).^2 + 4 * lambda^4));


% Fit functions
fit_omega_plus = @(p, x) omega_plus(p(1), p(2), p(3), x);
fit_omega_minus = @(p, x) omega_minus(p(1), p(2), p(3), x);

% Perform fits
fitted_omega_plus = fitnlm(x1_minus, x2_minus, fit_omega_plus, beta0);
fitted_omega_minus = fitnlm(x1_plus, x2_plus, fit_omega_minus, beta0);

% Extract parameters
params_plus = fitted_omega_plus.Coefficients.Estimate;
params_minus = fitted_omega_minus.Coefficients.Estimate;

% Plot
plot(x_zoomed, omega_plus(params_plus(1), params_plus(2), params_plus(3), x_zoomed), 'r'); hold on;
plot(x_zoomed, omega_minus(params_minus(1), params_minus(2),params_minus(3), x_zoomed), 'b');

save('fit', 'params_plus', 'params_minus', 'vdc_ac');