addpath(img_folder);
fileFolder = fullfile(img_folder);
dirOutput = dir(fullfile(fileFolder,img_names));
fileNames = {dirOutput.name}';
numFrames = numel(fileNames);
I = imread(fileNames{1});

Grey_Rec = zeros([size(I) numFrames],class(I));
Grey_Rec(:,:,1) = I;

for p = 2:numFrames
  Grey_Rec(:,:,p) = imread(fileNames{p});
  Grey_Rec  = double(Grey_Rec);
end
rmpath(img_folder);

nCells = 1;

Grey_Sub = subSampling(Grey_Rec, nCells);

clearvars -except Grey_Sub nCells Grey_boneThreshold Grey_marrowThreshold Image_Resolution calibration_folder_1 calibration_folder_2 calibration_names;

Binary_Unconnected = Grey_Sub > Grey_boneThreshold;

[Binary_islands, Num_islands] = bwlabeln(Binary_Unconnected,6);
[freq,number] = max(histc(Binary_islands(:),1:Num_islands));
Binary_Matrix_Bone = (Binary_islands == number);
Binary_Matrix_Bone = double(Binary_Matrix_Bone);

clearvars -except Grey_Sub nCells Binary_Matrix_Bone Grey_boneThreshold Grey_marrowThreshold Image_Resolution calibration_folder_1 calibration_folder_2 calibration_names;

nBones = numel(find(Binary_Matrix_Bone))
Bone_Number = Binary_Matrix_Bone(:);
Bone_Number(find(Bone_Number)) = 1:nBones;

Bone_Mask_Matrix = Grey_Sub .* Binary_Matrix_Bone;
Bone_Mask_Vector = Bone_Mask_Matrix(:);
Bone_Mask_Vector(Bone_Number == 0) = [];
Bone_Number_Vector = (1:nBones)';
Bone_Mask = [Bone_Number_Vector Bone_Mask_Vector];

clearvars -except Grey_Sub nCells nBones Bone_Number Bone_Mask Grey_boneThreshold Grey_marrowThreshold Image_Resolution calibration_folder_1 calibration_folder_2 calibration_names;

Binary_Unconnected = Grey_marrowThreshold <= Grey_Sub & Grey_Sub <= Grey_boneThreshold ;

[Binary_islands, Num_islands] = bwlabeln(Binary_Unconnected,6);
[freq,number]=max(histc(Binary_islands(:),1:Num_islands));
Binary_Matrix_Medium = (Binary_islands == number);
Binary_Matrix_Medium = double(Binary_Matrix_Medium);

nMediums = numel(find(Binary_Matrix_Medium))
Medium_Number = Binary_Matrix_Medium(:);
Medium_Number(find(Medium_Number)) = (nBones+1):(nBones+nMediums);

Medium_Mask_Matrix = Grey_Sub .* Binary_Matrix_Medium;
Medium_Mask_Vector = Medium_Mask_Matrix(:);
Medium_Mask_Vector(Medium_Number == 0) = [];
Medium_Number_Vector = ((nBones+1):(nBones+nMediums))';
Medium_Mask = [Medium_Number_Vector Medium_Mask_Vector];

clearvars -except Grey_Sub nCells nBones nMediums Bone_Number Medium_Number Bone_Mask Medium_Mask Grey_marrowThreshold Image_Resolution calibration_folder_1 calibration_folder_2 calibration_names;

Bone_Medium_Number = Bone_Number + Medium_Number;
Marrow_Number = (Bone_Medium_Number == 0);
Marrow_Number = double(Marrow_Number);
nMarrows = numel(find(Marrow_Number))
Marrow_Mask_Vector = Grey_Sub(:) .* Marrow_Number;
Marrow_Mask_Vector(Marrow_Number == 0) = [];
nElements = size(Grey_Sub,1)*size(Grey_Sub,2)*size(Grey_Sub,3)
Marrow_Number(find(Marrow_Number)) = (nBones+nMediums+1):nElements;

Marrow_Number_Vector = ((nBones+nMediums+1):nElements)';
Marrow_Mask = [Marrow_Number_Vector Marrow_Mask_Vector];

Element_Order = Bone_Number + Medium_Number + Marrow_Number;

Binary_Matrix = Grey_Sub >= 0;
save('Subsample','Binary_Matrix','nCells','Element_Order')

clearvars -except nCells nBones nMarrows nMediums nElements Marrow_Mask Bone_Mask Medium_Mask 'Binary_Matrix' 'Element_Order' Grey_marrowThreshold Image_Resolution calibration_folder_1 calibration_folder_2 calibration_names;
