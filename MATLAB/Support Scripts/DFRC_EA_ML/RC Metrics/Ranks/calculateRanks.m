function [kernelRankConfig] = calculateRanks(gainInput, gainTransferFunction, SimulationConfig, MetricConfig, metricType)

%% Script to evaluate the Kernal Quality or Generalisation Rank from a Simulation Config

%% First, generate a sequence of random numbers between 0 and 1 of length k
% All but k-1 are used to warm up the resiviour.
% At the kth value, the state space of the matrix is taken
% This implies the following. State space is taken at every Theta
% The samples are fed in at a speed of Tau
% K is to be atleast twice N plus washout
%% This is performed N times

%% Seed Random
rng(1,'twister'); 

%% How many simulations should run at a time?
ParallelRuns = 100;

%% Rank Parameters 

% How many input vectors should be tested? 
%   Scallar*Nodes
kernelRankConfig.numberInputVectorWashout = MetricConfig.numberInputVectorWashout_Rank;

% What should be the length of each input vector? 
%   Scallar*Nodes + Washout
kernelRankConfig.lengthInputVectorScallar = MetricConfig.lengthInputVectorScallar_Rank;

% Define what type of rank metric to be run
kernelRankConfig.metricType = metricType;

% SVD threshold percentage
kernelRankConfig.SVDThresholdPercentage = MetricConfig.SVDThresholdPercentage;

%% Calculate parameters

% How many input vectors should be tested? 
%   Recomended atleast twice that of the amount of nodes.
kernelRankConfig.numberInputVectors = SimulationConfig.nodes + kernelRankConfig.numberInputVectorWashout;

% What should be the length of each input vector? 
%   Recomended atleast twice that of the amount of nodes plus washout
kernelRankConfig.lengthInputVector = (kernelRankConfig.lengthInputVectorScallar*SimulationConfig.nodes) + SimulationConfig.washoutLength;

% Calculate How Many Runs
TotalRuns = ceil(kernelRankConfig.numberInputVectors/ParallelRuns);
ParallelRunsLimit = SimulationConfig.ParallelRuns;

%% Generate Input Vectors Dependent on Metric

% If testing for Kernel Quality
if (strcmp(metricType,'kernelQuality')) 

    % Generate a large number of random input vectors
    config.InputVectors = 2*rand(kernelRankConfig.lengthInputVector,kernelRankConfig.numberInputVectors)-1;

% If testing for Generalisation Rank
elseif (strcmp(metricType,'generalisationRank')) 

    % Maximum amplitude of the noise level
    kernelRankConfig.noiseAmplitude = MetricConfig.noiseAmplitude_Rank;
    
    % Create a large number of test vectors all centred around 1 with added random noise
    config.InputVectors = 0.8 + kernelRankConfig.noiseAmplitude*rand(kernelRankConfig.lengthInputVector,kernelRankConfig.numberInputVectors)-(kernelRankConfig.noiseAmplitude/2);

else
    disp('Selection Invalid')
    return;
end

%% Mask Input Vectors
for i = 1:kernelRankConfig.numberInputVectors
    % Mask with settings of previous experiment
    config.InputVectors_Masked(:,i) = timeMultiplexing(config.InputVectors(:,i), kernelRankConfig.lengthInputVector, SimulationConfig.nodes, SimulationConfig.maskingType, SimulationConfig.maskingOffset);
end

%% Calculate Simulation and Input Vector Time

% Simulation Length
kernelRankConfig.simulationTime = SimulationConfig.signalPeriod*kernelRankConfig.lengthInputVector;

% Input Vector Time
config.InputSignalTime = (0:SimulationConfig.maskingPeriod:(SimulationConfig.signalPeriod*kernelRankConfig.lengthInputVector)-SimulationConfig.maskingPeriod)';

%% Create config for Simulink Simulation

% Set constant variables
config.theta = SimulationConfig.maskingPeriod;
config.tau = SimulationConfig.signalPeriod;
config.Timescale = SimulationConfig.Timescale;
config.simulationTimeStep = SimulationConfig.simulationTimeStep;
config.simulinkTime = kernelRankConfig.simulationTime;

% Set parameter variables
config.InputScalling = gainInput;
config.TransferFunctionGain = gainTransferFunction;

%% Open simulink model
%open_system('DFR_TimescaleModel_ParaSweep');

%% Tell user how many simulations are to be ran
disp(["Running ", kernelRankConfig.numberInputVectors, " in ", TotalRuns, " blocks."]);

for j = 1:TotalRuns

    %% Generate Tests
    for k = 1:ParallelRuns
    
        % Find corosponding varible index from master config
        InputIndex = k + (j-1)*ParallelRuns;

        % Set simulation model
        in(k) = Simulink.SimulationInput('DFR_TimescaleModel_ParaSweep');
    
        % Set config with static simulation variables
        in(k) = in(k).setVariable('config',config);
    
        % Retreive and set input test vector
        config.DFR_Input = [config.InputSignalTime(:),config.InputVectors_Masked(:,InputIndex)];
        in(k) = in(k).setVariable('DFR_Input',config.DFR_Input);
    
        % Set gain parameters
        in(k) = in(k).setVariable('InputScalling',config.InputScalling);
        in(k) = in(k).setVariable('TransferFunctionGain',config.TransferFunctionGain);

        % Check if we have reached the limit of simulations to run
        if (InputIndex >= kernelRankConfig.numberInputVectors)

            ParallelRunsLimit = k;
            break;
        end
    
    end
    
    %% Run Tests
    out = parsim(in,'ShowSimulationManager','off','ShowProgress','on','UseFastRestart','on');
    
    %% Retreive state matrix of system output.
    %   For the kernal rank, the last N points are recorded from the simulated state matrix
    
    % Loop through simulated results
    for l = 1:ParallelRunsLimit

        % Find corosponding varible index from master config
        WriteIndex = l + (j-1)*ParallelRuns;

        kernelRankConfig.KernelMatrix(:,WriteIndex) = out(l).DFR_Out.signals.values(end-(SimulationConfig.nodes-1):end)';
    end

    % Clear previous vectors
    clear in;
    disp([metricType, "Finished Run ", j, " with ", WriteIndex, " outputs saved."]);

end

% Catch any errors
kernelRankConfig.KernelMatrix(isnan(kernelRankConfig.KernelMatrix)) = 0;
kernelRankConfig.KernelMatrix(isinf(kernelRankConfig.KernelMatrix)) = 0;

%% Evaluate Kernal Quality

% Perform Singular Value Decomposition
kernelRankConfig.kernalSVD = svd(kernelRankConfig.KernelMatrix);

SVD_Matrix = kernelRankConfig.kernalSVD;

SVD_MatrixSum = sum(SVD_Matrix);
SVD_MatrixThreshold = SVD_MatrixSum * kernelRankConfig.SVDThresholdPercentage;

SVD_ThresholdIndex = abs(SVD_Matrix)<SVD_MatrixThreshold;
SVD_Matrix(SVD_ThresholdIndex) = 0;

kernelRankConfig.rank = nnz(SVD_Matrix);

disp([metricType, "Finished"]);
