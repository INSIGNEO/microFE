function main(img_folder, img_names, Grey_boneThreshold, nCells, Grey_marrowThreshold, Image_Resolution, calibration_folder_1, calibration_folder_2, calibration_names, out_folder)
  %tic;

  disp(['Step 1']);
  % S1_meshPreparation;
  S1;%(img_folder, img_names, Grey_boneThreshold, nCells, Grey_marrowThreshold);

  disp(['Step 2']);
  % S2_AnsysMesheStreamout;
  S2;%(Image_Resolution);

  disp(['Step 3']);
  % S3_boneCalibration;
  S3;

  disp(['Step 4']);
  % S4_boneModulus;
  S4;

  disp(['Step 5']);
  % S5_marrowModulus;
  S5;

  disp(['Step 6']);
  % S6_mediumModulus_bilinear;
  S6;

  %toc
end
