function [Error_Training, Error_Testing] = Evaluate(experimentName, filepath)
%% Script to evaluate the performance of a delay-feedback resiviour.

%% Seed Randomo
rng(1,'twister');

%% Experiment Run Name
% This loads the files within the "experiments runs" folder
%% Load experiment config
load([fullfile('MATLAB/Experiment Runs/',experimentName,'/config.mat')]);

%% Load experimental data
%load([fullfile('MATLAB/Experiment Runs/',experimentName,'/', filename, '.csv')]);
% outputData = readmatrix(fullfile('MATLAB/Experiment Runs/', experimentName, '/csv/', filename));
outputData = readmatrix(filepath);
%% Analysis Paramaters
% Define error type
config.errorType = 'NRMSE';

% Portion of Data to Train on
config.trainingSize = 0.6;

%% Generate Target and Testing Matrices
% Split into Training and Testing Set
%config.outputSequence = config.outputSequence - mean(config.outputSequence);
TargetMatrix_Training = [config.outputSequence(config.washoutLength+1:config.sequenceLength*config.trainingSize)];
TargetMatrix_Testing = [config.outputSequence(config.sequenceLength*config.trainingSize+1:end)];


%% This is the variable to store the reservoir output
stateMatrix = outputData;
%stateMatrix = stateMatrix - mean(stateMatrix);

%% Split into Training and Testing Set
% This will reshape a column matrix of samples*nodes + tau + 1.
% First we trim the begining of the data, the tau + 1 as these are zero values and no information is present until after a time delay of tau
% Second, we reshape the matrix to NxM so that each column represents a value of the virtual node.
% Third, we split the data according to the trainSize value. This is typically 60/40

% Trim begining data and split data set
StateMatrix_Training = [stateMatrix((config.washoutLength*config.nodes)+1:config.nodes*config.sequenceLength*config.trainingSize)];
%StateMatrix_Testing = [stateMatrix((config.nodes*config.sequenceLength*config.trainingSize)+1:end-(config.nodes+1))];
StateMatrix_Testing = [stateMatrix((config.nodes*config.sequenceLength*config.trainingSize)+1:end)];

% Reshape state matrix into stardard format NxM
StateMatrix_Training = reshape(StateMatrix_Training, config.nodes, []);
StateMatrix_Testing = reshape(StateMatrix_Testing, config.nodes, []);

%% Calculate Weights
% Here we pass the training section of the output of the reservour (StateMatrix_Training) and the desired output of the benchmark (TargetMatrix_Training)
% to generate a set of weights.
outputWeights = trainFuncs(StateMatrix_Training,TargetMatrix_Training);
    
%% Apply weights 
% We apply the weights to the training set
WeightedOutput_Training = (outputWeights*StateMatrix_Training)';

% We apply the weights to the testing set
WeightedOutput_Testing = (outputWeights*StateMatrix_Testing)';

%% Calculate Error
% Now we test the error for the training and testing data set.
% To calculate the error, we pass the weighted output of the system against the expected output of the benchmark
% and we calculate the error between these
% --- Typically we use NRMSE. An NRMSE of 0 means perfect, while an NRMSE of 1 means weighted output is no better than the average of the signal.
Error_Training = calculateError(WeightedOutput_Training,TargetMatrix_Training, config);
Error_Testing = calculateError(WeightedOutput_Testing,TargetMatrix_Testing, config);

%% Store errors within the config
config.Results_Training = Error_Training;
config.Results_Testing = Error_Testing;

%% Save config to .mat file
save([fullfile('MATLAB/Experiment Runs/',experimentName,'/config.mat')],'config','-v7.3');

end
