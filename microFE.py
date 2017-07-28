import os

img_folder = "/home/ale/postdoc/microFE/images/ConvergenceCube"
img_names = "Scan1_****"

Grey_boneThreshold = 18500
Grey_marrowThreshold = 4500
Image_Resolution = 0.00996

calibration_folder_1 = "/home/ale/postdoc/microFE/images/Ph250"
calibration_folder_2 = "/home/ale/postdoc/microFE/images/Ph750"
calibration_names = "Ph****"

params = [img_folder, img_names, Grey_boneThreshold, Grey_marrowThreshold,
          Image_Resolution, calibration_folder_1, calibration_folder_2,
          calibration_names]
params1 = [img_names, Grey_boneThreshold]

sep = '" '
pre = '"'
if __name__ == "__main__":
    command = 'm_files/run_main.sh /usr/local/MATLAB/MATLAB_Runtime/v90 '
    for p in params:
        command += pre+str(p)+sep

    os.system(command)
    # print command

    # command = 'm_files/run_S1.sh /usr/local/MATLAB/MATLAB_Runtime/v90 '
    # for p in params1:
    #     command += pre+str(p)+sep
    #
    # os.system(command)
    # # print command
