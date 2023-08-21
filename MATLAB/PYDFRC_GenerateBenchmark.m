function PYDFRC_GenerateBenchmark(config)

% Check that all fields are present in the struct
fields = {'experimentName', 'memorySize', 'sequenceLength', 'washoutLength', 'nodes', 'dataset'};
if ~all(isfield(config, fields))
    error('Some fields are missing from the input struct')
end
%% Script to generate benchmark data for a delay-feedback resiviour.

%% Seed Random
rng(1,'twister');

%% Experiment Run Name
% This saves the files within the "experiments runs" folder
% config.experimentName = "Mackey-Glass_Evaluation_15us_Unshifted";

%% System Paramaters
% How many virtual nodes within the system
% config.nodes = 100;

%% Dataset Parameters 
% Define type of Dataset
% config.dataset = 'NARMA';

% Define Length of dataset sequence and memory size
% config.sequenceLength = 6000;
%config.memorySize = 10;

% Define scalar benchmark
config.benchmarkRangeScalar = 1;

% Give length of desired washout period of dataset
% config.washoutLength = 100;

%% Masking Parameters
% Define type of masking
config.maskingType = 'random';
config.maskingOffset = 'false';

%% Generate Dataset
[config.inputSequence, config.outputSequence] = selectTestingDataset(config);

%% Mask NARMA Data
config.inputSequenceMasked = timeMultiplexing(config.inputSequence, config.sequenceLength, config.nodes, config.maskingType, config.maskingOffset);

%% Save output
% Create directory
mkdir(fullfile('MATLAB/Experiment Runs',config.experimentName));

% Save config to .mat file
save([fullfile('MATLAB/Experiment Runs/',config.experimentName,'/config.mat')],'config','-v7.3');

% Save pre-masked input sequence as CSV
writematrix(config.inputSequenceMasked, [fullfile('MATLAB/Experiment Runs/',config.experimentName,'/inputSequenceMasked.csv')]);
