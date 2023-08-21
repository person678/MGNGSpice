function [] = evaluateAllMetrics(SimulationConfig)

%% Seed Random
rng(1,'twister'); 

%% Select set of results
ResultSet = SimulationConfig.timeStamp;

%% Truncate X and Y from parameter sweep by a scallar amount
runScallar = 2;

%% Parameters for finding Kernal Quality and Generalisation Rank
% How many input vectors should be tested? 
%   Nodes + Washout
MetricConfig.numberInputVectorWashout_Rank = 100;

% What should be the length of each input vector? 
%   Scallar*Nodes + Washout
MetricConfig.lengthInputVectorScallar_Rank = 5;

% Maximum amplitude of the noise level
MetricConfig.noiseAmplitude_Rank = 0.1;

% Threshold for determining SVD cutoff
MetricConfig.SVDThresholdPercentage = 0.01;

%% Parameters for finding  memory capacity

% How many input vectors should be tested? 
%   extra vectors + Nodes
MetricConfig.memoryExtraVectors_MC = 100;

% What should be the length of each input vector? 
%   Scallar*Nodes + Washout
MetricConfig.lengthInputVector_MC = 6000;

% Define washout length
MetricConfig.washOut = 100;

% Define masking type
MetricConfig.maskingType = 'random';

%% Metric config training parameters
%
MetricConfig.errorType = 'NRMSE';

% Portion of Data to Train on
MetricConfig.trainingSize = 0.8;

%% Calculate Sweep Parameters

% Apply Scallar to runs
TransferFuncGain_Steps = SimulationConfig.TransferFuncGain_Steps/runScallar;
InputScalling_Steps = SimulationConfig.InputScalling_Steps/runScallar;

InputScalling_Increment = SimulationConfig.InputScalling_Increment*runScallar;
TransferFuncGain_Increment = SimulationConfig.TransferFuncGain_Increment*runScallar;

InputScalling_Initial = SimulationConfig.InputScalling_Initial*runScallar;
TransferFuncGain_Initial = SimulationConfig.TransferFuncGain_Initial*runScallar;

% Calculate Total Amount of Simulations
TotalSimulations = (TransferFuncGain_Steps)*(InputScalling_Steps);

% Caulculate Final Values
InputScalling_Final = InputScalling_Initial + (InputScalling_Steps-1)*InputScalling_Increment;
TransferFuncGain_Final = TransferFuncGain_Initial + (TransferFuncGain_Steps-1)*TransferFuncGain_Increment;

%% Pre
variables=struct('InputScalling',zeros(TotalSimulations,1), 'TransferFunctionGain',zeros(TotalSimulations,3));

%% Create Array of configs
for i = 1:TotalSimulations
    
    % Set parameters under test
    variables(i).InputScalling = InputScalling_Initial + (mod(i-1,InputScalling_Steps)*InputScalling_Increment);
    variables(i).TransferFunctionGain = TransferFuncGain_Initial + (mod(floor((i-1)/InputScalling_Steps),TransferFuncGain_Steps)*TransferFuncGain_Increment);
end

for k = 1:TotalSimulations

    kernalOutput(k) = calculateRanks(variables(k).InputScalling,variables(k).TransferFunctionGain,SimulationConfig,MetricConfig,'kernelQuality');
    generalisationOutput(k) = calculateRanks(variables(k).InputScalling,variables(k).TransferFunctionGain,SimulationConfig,MetricConfig,'generalisationRank');
    LinearMCOutput(k) = calculateLinearMC(variables(k).InputScalling, variables(k).TransferFunctionGain, SimulationConfig, MetricConfig);
    QuadraticMCOutput(k) = calculateQuadraticMC(variables(k).InputScalling, variables(k).TransferFunctionGain, SimulationConfig, MetricConfig);

    disp(["---Completed run ", k, " of ", TotalSimulations]);

end

save([fullfile('./ParamaterSweeps',SimulationConfig.dataset,SimulationConfig.timeStamp), '/kernalOutput.mat'],'kernalOutput','-v7.3');
save([fullfile('./ParamaterSweeps',SimulationConfig.dataset,SimulationConfig.timeStamp), '/generalisationOutput.mat'],'generalisationOutput','-v7.3');
save([fullfile('./ParamaterSweeps',SimulationConfig.dataset,SimulationConfig.timeStamp), '/LinearMCOutput.mat'],'LinearMCOutput','-v7.3');
save([fullfile('./ParamaterSweeps',SimulationConfig.dataset,SimulationConfig.timeStamp), '/QuadraticMCOutput.mat'],'QuadraticMCOutput','-v7.3');