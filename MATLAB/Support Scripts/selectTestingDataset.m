function [inputSequence, outputSequence] = selectTestingDataset(datasetConfig)

%% Function to determine which dataset to test system on.

%% Select dataset
switch datasetConfig.dataset

    %% Generate NARMA data sequence
    case 'NARMA'
        [inputSequence, outputSequence] = generateNARMA(datasetConfig.sequenceLength, datasetConfig.memorySize, datasetConfig.washoutLength, datasetConfig.benchmarkRangeScalar);

    %% Generate Santa Fe data sequence
    case 'santafe'
        [inputSequence, outputSequence] = generateSantaFe(datasetConfig.sequenceLength, datasetConfig.memorySize, datasetConfig.benchmarkRangeScalar);

end



