function PYconvert_input_to_LTSpice(experimentName, theta, shift)
% The path of the csv file
csvFile = strcat('MATLAB/Experiment Runs/', experimentName, '/inputSequenceMasked.csv'); 

% The masking signal theta (change to your desired value)
% theta = 15e-6; % in seconds

% Read the voltage data from csv file
voltage = csvread(csvFile);
if shift == 1
    voltage = voltage + 1;
end

% Generate the timestamps
timestamps = (0:theta:theta*(length(voltage)-1))';

% Concatenate timestamps and voltage data into a single matrix
dataWithTimestamps = [timestamps, voltage];

% Create or open file.
LTSpiceInputFile = strcat('MATLAB/Experiment Runs/', experimentName, '/LTSpiceInput.txt'); 
fileID = fopen(LTSpiceInputFile, 'w');

% Write the output to the new text file in the format needed by LTSpice
for i = 1:length(dataWithTimestamps)
    fprintf(fileID, '%.15f %.15f\n', dataWithTimestamps(i,1), dataWithTimestamps(i,2));
end

% Close the file
fclose(fileID);
end

