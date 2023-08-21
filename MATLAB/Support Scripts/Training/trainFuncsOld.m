function [outputWeights] = trainFuncs(stateMatrix, target_matrix)


%% Script to generate output weights using Moore–Penrose pseudo-inverse
% Training --- Moore–Penrose pseudo-inverse Wout = B * pinv(A) --- 
    
%% Training --- Moore–Penrose pseudo-inverse Wout = B * pinv(A) --- 
outputWeights = target_matrix' * pinv(stateMatrix);

%% Clean up
% Remove NaNs
outputWeights(isnan(outputWeights)) = 0;
        
end