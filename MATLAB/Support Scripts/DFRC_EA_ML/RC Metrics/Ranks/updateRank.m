
%% Clear workspace
clear
close all

%% Seed Random
rng(1,'twister'); 

%% Global parameters
% Percentage of max value for threshold
SVD_ThresholdPercent = 0.01;

%% Select set of results
ResultSet = "metrics/10_20";

%% Import Simulation Results and Configuration
load([fullfile('./ParamaterSweeps/',ResultSet,'/SimulationConfig.mat')]);
load([fullfile('./ParamaterSweeps/',ResultSet,'/generalisationOutput.mat')]);
load([fullfile('./ParamaterSweeps/',ResultSet,'/kernalOutput.mat')]);

%% Sanity Check

% Check if correct experiment has been loaded
%if strcmp(ResultSet,SimulationConfig.timeStamp) == false
    
%    disp('Invalid Experiment')
%    return;
%end

%% Update rank value for kernel quality
for i = 1:width(kernalOutput)

%     SVD_Matrix = kernalOutput(i).kernalSVD;
% 
%     SVD_MatrixSum = sum(SVD_Matrix);
%     SVD_MatrixThreshold = SVD_MatrixSum * SVD_ThresholdPercent;
% 
%     SVD_ThresholdIndex = find(abs(SVD_Matrix)<SVD_MatrixThreshold);
%     SVD_Matrix(SVD_ThresholdIndex) = 0;
% 
%     kernalOutput(i).rank = nnz(SVD_Matrix);

    SVD_Matrix = kernalOutput(i).kernalSVD;

    tmp_rank_sum = 0;
    full_rank_sum = 0;
    e_rank = 1;
    for l = 1:length(SVD_Matrix)
        full_rank_sum = full_rank_sum + SVD_Matrix(l);
        while (tmp_rank_sum < full_rank_sum * 0.99)
            tmp_rank_sum = tmp_rank_sum + SVD_Matrix(e_rank);
            e_rank= e_rank+1;
        end
    end

    kernalOutput(i).rank_m = e_rank-1;

end

%% Update rank value for generalisiation rank
for i = 1:width(generalisationOutput)

%     SVD_Matrix = generalisationOutput(i).kernalSVD;
% 
%     SVD_MatrixSum = sum(SVD_Matrix);
%     SVD_MatrixThreshold = SVD_MatrixSum * SVD_ThresholdPercent;
% 
%     SVD_ThresholdIndex = find(abs(SVD_Matrix)<SVD_MatrixThreshold);
%     SVD_Matrix(SVD_ThresholdIndex) = 0;
% 
%     generalisationOutput(i).rank = nnz(SVD_Matrix);

    SVD_Matrix = generalisationOutput(i).kernalSVD;

    tmp_rank_sum = 0;
    full_rank_sum = 0;
    e_rank = 1;
    for l = 1:length(SVD_Matrix)
        full_rank_sum = full_rank_sum + SVD_Matrix(l);
        while (tmp_rank_sum < full_rank_sum * 0.99)
            tmp_rank_sum = tmp_rank_sum + SVD_Matrix(e_rank);
            e_rank= e_rank+1;
        end
    end

    generalisationOutput(i).rank_m = e_rank-1;

end

save([fullfile('./ParamaterSweeps',ResultSet, '/kernalOutput.mat')],'kernalOutput','-v7.3');
save([fullfile('./ParamaterSweeps',ResultSet, '/generalisationOutput.mat')],'generalisationOutput','-v7.3');