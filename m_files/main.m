tic;

disp(['S1 start']);
S1_meshPreparation;

disp(['S2 start']);
S2_AnsysMesheStreamout;

disp(['S3 start']);
S3_boneCalibration;

disp(['S4 start']);
S4_boneModulus;

disp(['S5 start']);
S5_marrowModulus;

disp(['S6 start']);
S6_mediumModulus_bilinear;

toc