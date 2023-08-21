function [inputSequence, outputSequence] = generateSantaFe(sequenceLength, memoryLength, benchmarkRangeScalar)

%% Script to Generate SantaFe

%% Get Laser Dataset from MATLAB
laserData = cell2mat(laser_dataset);

%% Truncate To Correct Length
laserData = laserData(1:sequenceLength+memoryLength);

%% Set range to between desired range
% Get maximum value in dataset
laserMaximum = max(laserData);

% Divide dataset by maximum value
laserData = laserData/laserMaximum;

% Apply benchmark scalar
laserData = laserData*benchmarkRangeScalar;

%% Generate input and output sequence
inputSequence = laserData(1:end-memoryLength)';
outputSequence = laserData(1+memoryLength:end)';