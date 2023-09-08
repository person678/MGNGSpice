% The path of the file
csvFile = 'masked_input.txt'; 

% The masking signal theta (change to your desired value)
theta = 29.08e-6; % in seconds

% Read the voltage data from csv file
input_masked = csvread(csvFile);

% Generate the timestamps
timestamps = (0:theta:theta*(length(input_masked)-1))';

% Create a matrix to store data with timestamps
dataWithTimestamps = [];

% Populate the list
for i = 1:length(timestamps)
    
    % Always add the current value
    dataWithTimestamps = [dataWithTimestamps; timestamps(i), input_masked(i)];
    
    if i < length(timestamps) && input_masked(i) ~= input_masked(i+1)
        % If the current value is different from the next value, add an intermediate point
        dataWithTimestamps = [dataWithTimestamps; timestamps(i+1) - 1.5e-6, input_masked(i)];
    end
end

% Create or open file.
SpiceInputFile = 'SpiceInput29_08.txt'; 
fileID = fopen(SpiceInputFile, 'w');

% Write the output to the new text file in the format needed by LTSpice
for i = 1:length(dataWithTimestamps)
    fprintf(fileID, '%.15f %.15f\n', dataWithTimestamps(i,1), dataWithTimestamps(i,2));
end

% Close the file
fclose(fileID);