% read the microCT image datasetas a 3D matrix in greyscale by calling the
% tifRead function

img_folder = '/home/ale/postdoc/microFE/images/ConvergenceCube';

addpath(img_folder);
fileFolder = fullfile(img_folder);
dirOutput = dir(fullfile(fileFolder,'Scan1_****'));
fileNames = {dirOutput.name}';
numFrames = numel(fileNames);
I = imread(fileNames{1});
%Preallocate the array
Grey_Rec = zeros([size(I) numFrames],class(I));
Grey_Rec(:,:,1) = I;
%Create image sequence array
for p = 2:numFrames
  Grey_Rec(:,:,p) = imread(fileNames{p});
  Grey_Rec  = double(Grey_Rec);
end
rmpath(img_folder);

%%
% Input the sumsampling factor
%   options = {'1','2','4','8','16'};
%   message = 'options to subsampling:';
%   [selection, ok] = listdlg('PromptString',message,'ListString',options);
%   nCells = str2num(options{selection});
nCells = 1;

% Call subSampling function
  Grey_Sub = subSampling(Grey_Rec, nCells);

% Clean memory
  clearvars -except Grey_Sub nCells ;

%%
% Bone elements
% Threshold to get the binarised bone dataset, then feed to connectivity
% filter
  % Grey_boneThreshold = inputdlg('Thresholding value of bone?');
  % Grey_boneThreshold = str2num(Grey_boneThreshold{:})
  Grey_boneThreshold = 18500
  Binary_Unconnected = Grey_Sub > Grey_boneThreshold;

%Connectivity filter. To get rid of the elements which are not
%connected to do the major part of the bones.
%Connectivity rules : face to face, so 6.
  [Binary_islands, Num_islands] = bwlabeln(Binary_Unconnected,6);
  [freq,number] = max(histc(Binary_islands(:),1:Num_islands));
  Binary_Matrix_Bone = (Binary_islands == number);
  Binary_Matrix_Bone = double(Binary_Matrix_Bone);
% Clean memory
  clearvars -except Grey_Sub nCells Binary_Matrix_Bone...
                    Grey_boneThreshold ;
% Assign the cubic matrix with the bone element number with their position
% starting from 1.
  nBones = numel(find(Binary_Matrix_Bone))
  Bone_Number = Binary_Matrix_Bone(:);
  Bone_Number(find(Bone_Number)) = 1:nBones;
% Create the Bone_order plus corresponding grey value for later use
  Bone_Mask_Matrix = Grey_Sub .* Binary_Matrix_Bone;
  Bone_Mask_Vector = Bone_Mask_Matrix(:);
  Bone_Mask_Vector(Bone_Number == 0) = [];
  Bone_Number_Vector = (1:nBones)';
  Bone_Mask = [Bone_Number_Vector Bone_Mask_Vector];
% Clean memory
  clearvars -except Grey_Sub nCells nBones Bone_Number Bone_Mask...
                    Grey_boneThreshold
%%
% Medium elements
% Threshold to get the binarised medium dataset,then fed to the
% connectivity filter
% trace the peak value representing the backgroud

  Grey_marrowThreshold = 4500
  Binary_Unconnected = Grey_marrowThreshold <= Grey_Sub...
                     & Grey_Sub <= Grey_boneThreshold ;

% Connectivity filter. To get rid of the elements which are not
% connected to do the major part of the medium.
% Connectivity rules : face to face, so 6.
  [Binary_islands, Num_islands] = bwlabeln(Binary_Unconnected,6);
  [freq,number]=max(histc(Binary_islands(:),1:Num_islands));
  Binary_Matrix_Medium = (Binary_islands == number);
  Binary_Matrix_Medium = double(Binary_Matrix_Medium);

% Assign the Cubic matrix with the medium element number starting from
% nBones+1, ending with nBones+nMediums.

  nMediums = numel(find(Binary_Matrix_Medium))
  Medium_Number = Binary_Matrix_Medium(:);
  Medium_Number(find(Medium_Number)) = (nBones+1):(nBones+nMediums);
% Create the Mediun_order plus corresponding grey value for later use
  Medium_Mask_Matrix = Grey_Sub .* Binary_Matrix_Medium;
  Medium_Mask_Vector = Medium_Mask_Matrix(:);
  Medium_Mask_Vector(Medium_Number == 0) = [];
  Medium_Number_Vector = ((nBones+1):(nBones+nMediums))';
  Medium_Mask = [Medium_Number_Vector Medium_Mask_Vector];
% Clean memory
  clearvars -except Grey_Sub nCells nBones nMediums Bone_Number...
                    Medium_Number Bone_Mask Medium_Mask        ...
                    Grey_marrowThreshold;
 %%
% Marrow elements
% Find the Marrow_Number
% Assign the Cubic matrix with the marrow element number starting from
% nBones+nMediums+1, ending with nElements.
  Bone_Medium_Number = Bone_Number + Medium_Number;
  Marrow_Number = (Bone_Medium_Number == 0);
  Marrow_Number = double(Marrow_Number);
  nMarrows = numel(find(Marrow_Number))
  Marrow_Mask_Vector = Grey_Sub(:) .* Marrow_Number;
  Marrow_Mask_Vector(Marrow_Number == 0) = [];
  nElements = size(Grey_Sub,1)*size(Grey_Sub,2)*size(Grey_Sub,3)
  Marrow_Number(find(Marrow_Number)) = (nBones+nMediums+1):nElements;
% Create the Marrow_order plus corresponding grey value for later use
  Marrow_Number_Vector = ((nBones+nMediums+1):nElements)';
  Marrow_Mask = [Marrow_Number_Vector Marrow_Mask_Vector];
% Element order matrix consist of Bone_Number,Marrow_Number, Medium_Number;
  Element_Order = Bone_Number + Medium_Number + Marrow_Number;
%%
% Create Binary_Matrix for the whole cube
  Binary_Matrix = Grey_Sub >= 0;
  save('Subsample','Binary_Matrix','nCells','Element_Order')

% Clean memory
  clearvars -except nCells nBones nMarrows nMediums nElements Marrow_Mask Bone_Mask Medium_Mask 'Binary_Matrix' 'Element_Order' Grey_marrowThreshold;
