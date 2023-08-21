function [outputWeights] = trainFuncsMulti(stateMatrix, target_matrix)


%% Script to generate output weights using Ridge Regression 
% Ridge Regression Weights = BA'(AA'-λI)^-1
% Where A is state matrix, B is the desired output, 
% and λ is a regression term.

%target_matrix = repmat(training_outputSequence,1,length(training_outputSequence));

% Find best reg parameter
regParam = [10e-1 10e-3 10e-5 10e-7 10e-9 10e-11];

    for i = 1:length(regParam)
        % Perform Ridge Regression
        
        outputWeights(i,:) = (target_matrix'*stateMatrix') * ...
            inv(stateMatrix*stateMatrix' - regParam(i)*eye(size(stateMatrix*stateMatrix')));
      
    end
        
    %% Training --- Moore–Penrose pseudo-inverse Wout = B * pinv(A) --- 
    outputWeights(i+1,:) = target_matrix' * pinv(stateMatrix);
    
    %% Clean up
    % Remove NaNs
    outputWeights(isnan(outputWeights)) = 0;
        
end