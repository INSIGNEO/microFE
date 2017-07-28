import os

if __name__ == "__main__":

    WORK = os.getenv('WORK')
    img_folder = "{0}microFE/images/ConvergenceCube".format(WORK)
    img_names = "Scan1_****"

    nCells = 1
    Grey_boneThreshold = 18500
    Grey_marrowThreshold = 4500
    Image_Resolution = 0.00996

    calibration_folder_1 = "{0}microFE/images/Ph250".format(WORK)
    calibration_folder_2 = "{0}microFE/images/Ph750".format(WORK)
    calibration_names = "Ph****"

    params = [img_folder, img_names, Grey_boneThreshold, nCells,
              Grey_marrowThreshold, Image_Resolution, calibration_folder_1,
              calibration_folder_2, calibration_names]

    sep = '" '
    pre = '"'

    microFE_file = "microFE_qsub.sh"

    f=open(microFE_file,"w")
    line="#!/bin/bash --login \n"
    line+="#PBS -N uFE \n"
    line+="#PBS -l select=serial=true:ncpus=1 \n"
    line+="#PBS -l walltime=01:00:00 \n"
    line+="#PBS -A d137-me1ame \n"
    line+="export PBS_O_WORKDIR=$(readlink -f $PBS_O_WORKDIR) \n"
    line+="cd $PBS_O_WORKDIR \n"
    line+="module load mcr/9.0 \n"

    command = "{0}microFE/m_files/run_main.sh $LD_LIBRARY_PATH ".format(WORK)
    for p in params:
        command += pre+str(p)+sep
    line += command

    f.write(line)
    f.close()

    os.system("qsub {0}".format(microFE_file))
