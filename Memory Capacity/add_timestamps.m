% The path of the file
csvFile = 'masked_input.txt'; 

% The masking signal theta (change to your desired value)
theta = 30e-6; % in seconds

% Read the voltage data from csv file
input_masked = csvread(csvFile);

% Generate the timestamps
timestamps = (0:theta:theta*(length(input_masked)-1))';

% Create the doubled length matrix
dataWithTimestamps = zeros(2*length(timestamps)-1, 2);

% Populate the doubled matrix
for i = 1:length(timestamps)
    dataWithTimestamps(2*i-1, 1) = timestamps(i);
    dataWithTimestamps(2*i-1, 2) = input_masked(i);
    
    if i < length(timestamps)
        dataWithTimestamps(2*i, 1) = timestamps(i+1) - 2e-6; % Subtract a small value to set time just before the next point
        dataWithTimestamps(2*i, 2) = input_masked(i);
    end
end

% Create or open file.
SpiceInputFile = 'SpiceInput.txt'; 
fileID = fopen(SpiceInputFile, 'w');

% Write the output to the new text file in the format needed by LTSpice
for i = 1:length(dataWithTimestamps)
    fprintf(fileID, '%.15f %.15f\n', dataWithTimestamps(i,1), dataWithTimestamps(i,2));
end

% Close the file
fclose(fileID);