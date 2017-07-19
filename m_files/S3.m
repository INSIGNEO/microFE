addpath(calibration_folder_1);
fileFolder = fullfile(calibration_folder_1);
dirOutput = dir(fullfile(fileFolder,calibration_names));
fileNames = {dirOutput.name}';
numFrames = numel(fileNames);
I = imread(fileNames{1});

sequence = zeros([size(I) numFrames],class(I));
sequence(:,:,1) = I;

for p = 2:numFrames
    sequence(:,:,p) = imread(fileNames{p});
end

rmpath(calibration_folder_1);

avGrey_Low = mean(mean(mean(sequence,3)));

addpath(calibration_folder_2);
fileFolder = fullfile(calibration_folder_2);
dirOutput = dir(fullfile(fileFolder,calibration_names));
fileNames = {dirOutput.name}';
numFrames = numel(fileNames);
I = imread(fileNames{1});

sequence = zeros([size(I) numFrames],class(I));
sequence(:,:,1) = I;

for p = 2:numFrames
    sequence(:,:,p) = imread(fileNames{p});
end
rmpath(calibration_folder_2);

avGrey_High = mean(mean(mean(sequence,3)));

B=[0.75;0.25];
A=[avGrey_High,1;avGrey_Low,1];
C=A\B;
a=C(1);b=C(2);

clearvars -except nBones nMarrows nMediums nElements Marrow_Mask Bone_Mask Medium_Mask a b Grey_marrowThreshold;
