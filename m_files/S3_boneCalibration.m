%% 
%Calculate the average gray value of the low BMD Phantom images
%Create an array of filenames that make up the image sequence

calibration_folder_1 = '/home/ale/postdoc/microFE/images/Ph250';
calibration_folder_2 = '/home/ale/postdoc/microFE/images/Ph750';

 addpath(calibration_folder_1);
 fileFolder = fullfile(calibration_folder_1);
 dirOutput = dir(fullfile(fileFolder,'Ph****'));
 fileNames = {dirOutput.name}';
 numFrames = numel(fileNames);
 I = imread(fileNames{1});
 
%Preallocate the array
 sequence = zeros([size(I) numFrames],class(I));
 sequence(:,:,1) = I;
 
 %Create image sequence array
 for p = 2:numFrames
      sequence(:,:,p) = imread(fileNames{p}); 
 end
 
 rmpath(calibration_folder_1);
 
 avGrey_Low = mean(mean(mean(sequence,3)));
%% 
%Calculate the average gray value of the high BMD Phantom images
%Create an array of filenames that make up the image sequence
addpath(calibration_folder_2);
 fileFolder = fullfile(calibration_folder_2);
 dirOutput = dir(fullfile(fileFolder,'Ph****'));
 fileNames = {dirOutput.name}';
 numFrames = numel(fileNames);
 I = imread(fileNames{1});
%Preallocate the array
 sequence = zeros([size(I) numFrames],class(I));
 sequence(:,:,1) = I;
 %Create image sequence array
 for p = 2:numFrames
      sequence(:,:,p) = imread(fileNames{p}); 
 end
 rmpath(calibration_folder_2);
 
 avGrey_High = mean(mean(mean(sequence,3)));
%%
% Calculate the coefficient of linear equation of Grey value and BMD
B=[0.75;0.25];
A=[avGrey_High,1;avGrey_Low,1];
C=A\B;
a=C(1);b=C(2);

%Record the value of a and b to do the calibration next based on
%BMD=GV*a + b
%%
% Clean memory
  clearvars -except nBones nMarrows nMediums nElements    ...
                    Marrow_Mask Bone_Mask Medium_Mask a b ...
                    Grey_marrowThreshold;