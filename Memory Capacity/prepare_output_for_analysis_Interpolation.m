%% Interpolates the values from the dataset. 

data = importdata('OutputFixed.txt');
load('config.mat')
% Number of virtual nodes
N = 100;

% Assuming data is a two-column matrix, where the first column is time
time = data(:, 1);
voltage = data(:, 2);

% Removing duplicate time values and corresponding voltage values
[time, unique_indices] = unique(time, 'first');
voltage = voltage(unique_indices);

% Define the desired timestep
theta = 30e-6; 

% Define the times where you want to estimate voltage
time_query = 0:theta:max(time);
% Interpolate the voltage values at the desired times
voltage_interp = interp1(time, voltage, time_query);
voltage_interp = voltage_interp(1:N * 1000);

% Reshape time_query to ensure it's a column vector
time_query = time_query(:);

% Reshape voltage_query to ensure it's a column vector
voltage_interp = voltage_interp(:);
voltage_interp(1:100) = [];

% Format the voltages into columns per set of nodes (each coloumn has 1
% response from each node )
%voltages_as_matrix = reshape(voltage_interp, [N, numel(voltage_interp)/N]);

writematrix(voltage_interp, "OutputData_MC.txt");

% 
% % Define the Nth timestep
% Nth_timestep = 100000;
% 
% % Find the Nth interpolated value
% Nth_interp_value = voltage_interp(Nth_timestep);
% 
% % Find the time at Nth timestep
% Nth_time = time_query(Nth_timestep);
% 
% % Find index of the closest time in 'time' to the Nth_time
% [~, idx] = min(abs(time - Nth_time));
% 
% % Find the nearest original value
% nearest_orig_value = voltage(idx);
% 
% % Compare the Nth interpolated value and the nearest original value
% comparison_diff = abs(Nth_interp_value - nearest_orig_value);
% 
% % Calculate the difference as a percentage
% comparison_percentage = (comparison_diff / abs(nearest_orig_value)) * 100;
% 
% fprintf('The %dth interpolated value: %e\n', Nth_timestep, Nth_interp_value);
% fprintf('Nearest original value: %e\n', nearest_orig_value);
% fprintf('Difference between them: %e (%.4f%%)\n', comparison_diff, comparison_percentage);
