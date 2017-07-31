import os
import sys
from ConfigParser import SafeConfigParser
if __name__ == "__main__":

    # parse .ini configuration file
    p = SafeConfigParser()
    p.read(sys.argv[1])

    WORK = p.get("directories", "work")
    IMG = p.get("directories", "img")
    img_folder = "{0}{1}".format(WORK, IMG)
    img_names = p.get("images", "img_names")

    nCells = p.get("parameters", "nCells")
    Grey_boneThreshold = p.get("parameters", "Grey_boneThreshold")
    Grey_marrowThreshold = p.get("parameters", "Grey_marrowThreshold")
    Image_Resolution = p.get("parameters", "Image_Resolution")

    CAL1 = p.get("directories", "cal1")
    CAL2 = p.get("directories", "cal2")
    calibration_folder_1 = "{0}{1}".format(WORK, CAL1)
    calibration_folder_2 = "{0}{1}".format(WORK, CAL2)
    calibration_names = p.get("images", "cal_names")

    M_FILES = p.get("directories", "m_files")
    LD_LIB_PATH = p.get("directories", "ld_lib_path")

    job_name = p.get("job", "name")

    params = [img_folder, img_names, Grey_boneThreshold, nCells,
              Grey_marrowThreshold, Image_Resolution, calibration_folder_1,
              calibration_folder_2, calibration_names]

    sep = '" '
    pre = '"'

    if p.get("job", "type") == "HPC":
        microFE_file = "microFE_{0}.sh".format(job_name)

        f=open(microFE_file,"w")
        line="#!/bin/bash --login \n"
        line+="#PBS -N {0} \n".format(job_name)
        line+="#PBS -l select=serial=true:ncpus=1 \n"

        walltime = p.get("job", "walltime")
        line+="#PBS -l walltime=01:00:00 \n".format(walltime)

        budget_code = p.get("job", "budget_code")
        line+="#PBS -A d137-me1ame \n".format(budget_code)

        line+="export PBS_O_WORKDIR=$(readlink -f $PBS_O_WORKDIR) \n"
        line+="cd $PBS_O_WORKDIR \n"
        line+="module load mcr/9.0 \n"

        command = "{0}{1}run_main.sh {2} ".format(WORK, M_FILES, LD_LIB_PATH)
        for p in params:
            command += pre+str(p)+sep
        line += command

        f.write(line)
        f.close()

        os.system("qsub {0}".format(microFE_file))

    else:
        command = "{0}{1}run_main.sh {2} ".format(WORK, M_FILES, LD_LIB_PATH)
        for p in params:
            command += pre+str(p)+sep

        print command
