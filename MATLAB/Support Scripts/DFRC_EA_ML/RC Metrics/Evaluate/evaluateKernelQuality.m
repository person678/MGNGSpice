function [] = evaluateKernelQuality(SimulationConfig)

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
%   Scallar*Nodes
MetricConfig.lengthInputVectorScallar_Rank = 2;

% Threshold for determining SVD cutoff
MetricConfig.SVDThresholdPercentage = 0.01;

%% Is this a continuation?
if isfile([fullfile('./ParamaterSweeps',SimulationConfig.dataset,SimulationConfig.timeStamp), '/kernalOutput_Vars.mat'])
   
    kernalOutput_Vars = importdata([fullfile('./ParamaterSweeps',SimulationConfig.dataset,SimulationConfig.timeStamp), '/kernalOutput_Vars.mat']);
    kernalOutput = importdata([fullfile('./ParamaterSweeps',SimulationConfig.dataset,SimulationConfig.timeStamp), '/kernalOutput.mat']);
    SimulationStep = length(kernalOutput_Vars) + 1;
else
    SimulationStep = 1;
end

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

for k = SimulationStep:TotalSimulations

    calcOutput = calculateRanks(variables(k).InputScalling,variables(k).TransferFunctionGain,SimulationConfig,MetricConfig,'kernelQuality');

	kernalOutput_Vars(k) = variables(k);
	kernalOutput(k) = calcOutput
	
	save([fullfile('./ParamaterSweeps',SimulationConfig.dataset,SimulationConfig.timeStamp), '/kernalOutput_Vars.mat'],'kernalOutput_Vars','-v7.3');
	save([fullfile('./ParamaterSweeps',SimulationConfig.dataset,SimulationConfig.timeStamp), '/kernalOutput.mat'],'kernalOutput','-v7.3');

	clear calcOutput;

    disp(["---Completed run ", k, " of ", TotalSimulations]);

end

save([fullfile('./ParamaterSweeps',SimulationConfig.dataset,SimulationConfig.timeStamp), '/MetricConfig_KQ.mat'],'MetricConfig','-v7.3');
