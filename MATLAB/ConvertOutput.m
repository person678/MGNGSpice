function ConvertOutput(filepath, theta, sequenceLength, nodes)

    % Import the data
    data = importdata(filepath);

    % Number of virtual nodes
    N = nodes;

    % Extract time and voltage columns
    time = data.data(:, 1);
    voltage = data.data(:, 2);

    % Define the times where you want to estimate voltage
    time_query = 0:theta:max(time);

    % Interpolate the voltage values at the desired times
    voltage_interp = interp1(time, voltage, time_query);
    voltage_interp = voltage_interp(1:N * sequenceLength);

    % Reshape time_query to ensure it's a column vector
    % time_query = time_query(:);

    % Reshape voltage_query to ensure it's a column vector
    voltage_interp = voltage_interp(:);

    % Format the voltages into columns per set of nodes (each coloumn has 1
    % response from each node)
    voltages_as_matrix = reshape(voltage_interp, [N, numel(voltage_interp)/N]);

    % Construct output filepath
    [filepath_dir, name, ~] = fileparts(filepath);
    output_filepath = fullfile(filepath_dir, strcat(name, 'Converted.csv'));

    % Write the output matrix to a file
    writematrix(voltages_as_matrix, output_filepath);

end
