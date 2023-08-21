function [] = evaluateQuadraticMC(SimulationConfig)

%% Seed Random
rng(1,'twister'); 

%% Select set of results
ResultSet = SimulationConfig.timeStamp;

%% Metric config testing parameters
% Truncate X and Y from parameter sweep by a scallar amount
runScallar = 2;

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

%% Is this a continuation?
if isfile([fullfile('./ParamaterSweeps',SimulationConfig.dataset,SimulationConfig.timeStamp), '/QuadraticMCOutput_Vars.mat'])
   
    QuadraticMCOutput_Vars = importdata([fullfile('./ParamaterSweeps',SimulationConfig.dataset,SimulationConfig.timeStamp), '/QuadraticMCOutput_Vars.mat']);
    QuadraticMCOutput = importdata([fullfile('./ParamaterSweeps',SimulationConfig.dataset,SimulationConfig.timeStamp), '/QuadraticMCOutput.mat']);
	SimulationStep = length(QuadraticMCOutput_Vars) + 1;
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

    calcOutput = calculateQuadraticMC(variables(k).InputScalling, variables(k).TransferFunctionGain, SimulationConfig, MetricConfig);

	QuadraticMCOutput_Vars(k) = variables(k);
	QuadraticMCOutput(k) = calcOutput;
	
	save([fullfile('./ParamaterSweeps',SimulationConfig.dataset,SimulationConfig.timeStamp), '/QuadraticMCOutput_Vars.mat'],'QuadraticMCOutput_Vars','-v7.3');
	save([fullfile('./ParamaterSweeps',SimulationConfig.dataset,SimulationConfig.timeStamp), '/QuadraticMCOutput.mat'],'QuadraticMCOutput','-v7.3');
	
	clear calcOutput;

    disp(["---Completed run ", k, " of ", TotalSimulations]);

end

save([fullfile('./ParamaterSweeps',SimulationConfig.dataset,SimulationConfig.timeStamp), '/MetricConfig_QMC.mat'],'MetricConfig','-v7.3');
