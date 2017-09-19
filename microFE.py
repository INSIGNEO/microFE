'''
File: microFE.py
Author: A Melis
'''

__author__ = "Alessandro Melis"
__copyright__ = "Copyright 2017"
__credits__ = ["A Melis", "Y. Chen"]
__version__ = "0.0.1"
__maintainer__ = "Alessandro Melis"
__email__ = "a.melis@sheffield.ac.uk"
__status__ = "Prototype"

import os
import sys
from ConfigParser import SafeConfigParser

class microFE():
    def __init__(self, file_name):
        '''
        Read .ini configuration file and create output directory
        '''

        # parse .ini configuration file
        p = SafeConfigParser()
        p.read(sys.argv[1])

        self.WORK = p.get("directories", "work")
        self.IMG = p.get("directories", "img")
        self.img_folder = "{0}{1}".format(self.WORK, self.IMG)
        self.img_names = p.get("images", "img_names")
        self.out_folder = p.get("directories", "out_dir")

        self.nCells = p.get("parameters", "nCells")
        self.Grey_boneThreshold = p.get("parameters", "Grey_boneThreshold")
        self.Grey_marrowThreshold = p.get("parameters", "Grey_marrowThreshold")
        self.Image_Resolution = p.get("parameters", "Image_Resolution")

        self.CAL1 = p.get("directories", "cal1")
        self.CAL2 = p.get("directories", "cal2")
        self.calibration_folder_1 = "{0}{1}".format(self.WORK, self.CAL1)
        self.calibration_folder_2 = "{0}{1}".format(self.WORK, self.CAL2)
        self.calibration_names = p.get("images", "cal_names")

        self.M_FILES = p.get("directories", "m_files")
        self.LD_LIB_PATH = p.get("directories", "ld_lib_path")

        self.job_name = p.get("job", "name")

        self.params = [self.img_folder, self.img_names, self.Grey_boneThreshold,
            self.nCells, self.Grey_marrowThreshold, self.Image_Resolution,
            self.calibration_folder_1, self.calibration_folder_2,
            self.calibration_names, self.out_folder]

        self.job_type = p.get("job", "type")

        if self.job_type == "HPC":
            self.walltime = p.get("job", "walltime")
            self.budget_code = p.get("job", "budget_code")

        # create output folder
        if not os.path.isdir(self.out_folder):
            os.mkdir(self.out_folder)

        return


    def launchMatlabMesher(self):
        '''
        Launch the matlab mesher. If in HPC environment, prepare and submit a batch job.
        '''

        sep = '" '
        pre = '"'

        # write batch script for ARCHER
        if self.job_type == "HPC":
            microFE_file = "microFE_{0}.sh".format(self.job_name)

            line="#!/bin/bash --login \n"
            line+="#PBS -N {0} \n".format(self.job_name)
            line+="#PBS -l select=serial=true:ncpus=1 \n"
            line+="#PBS -l walltime=01:00:00 \n".format(self.walltime)
            line+="#PBS -A d137-me1ame \n".format(self.budget_code)
            line+="export PBS_O_WORKDIR=$(readlink -f $PBS_O_WORKDIR) \n"
            line+="cd $PBS_O_WORKDIR \n"
            line+="module load mcr/9.0 \n"

            command = "{0}{1}run_main.sh {2} ".format(self.WORK, self.M_FILES,
                                                        self.LD_LIB_PATH)
            for p in self.params:
                command += pre+str(p)+sep
            line += command

            with open(microFE_file,"w") as f:
                f.write(line)

            os.system("qsub {0}".format(microFE_file))

        # launch mesher on workstation
        else:
            command = "{0}{1}run_main.sh {2} ".format(self.WORK, self.M_FILES,
                                                        self.LD_LIB_PATH)
            for p in self.params:
                command += pre+str(p)+sep

            print command
            os.system(command)


    def convertMesh(self, height, displacement):
        '''
        Use matlab output files to create ParaFEM input files.

        Requires
        --------
        height : float
            Z-coordinate of the displaced nodes.
        displacement : float
            Displacement assigned to all the mesh upper nodes.
        '''

        bnd_file = open("{0}/{1}.bnd".format("parafem_inputs", self.job_name), 'w')
        d_file = open("{0}/{1}.d".format("parafem_inputs", self.job_name), 'w')
        fix_file = open("{0}/{1}.fix".format("parafem_inputs", self.job_name), 'w')

        lds_file = open("{0}/{1}.lds".format("parafem_inputs", self.job_name), 'w')
        lds_file.close() # we do not prescribe loads...right?
        nlnod = 0 # number of loaded nodes

        d_file.write("*THREE_DIMENSIONAL\n")
        d_file.write("*NODES\n")

        with open("{0}/nodedata.txt".format(self.out_folder), 'r') as nodes:
            nnod = 0 # number of nodes
            nres = 0 # number of constrained nodes
            for node in nodes:
                n = node.split(',')

                ni = n[1]
                nx = float(n[2])
                ny = float(n[3])
                nz = float(n[4])

                if nz == 0:
                    b = "{0} 1 1 1\n".format(ni)
                    bnd_file.write(b)

                    nres += 1

                d = "{0} {1} {2} {3}\n".format(ni, nx, ny, nz)
                d_file.write(d)

                # TODO: find highest node z-coordinate
                if nz == height: # displacement along z-axis
                    f = "{0} 3 {1}\n".format(ni, displacement)
                    fix_file.write(f)

                nnod += 1

        d_file.write("*ELEMENTS\n")

        with open("{0}/elementdata.txt".format(self.out_folder), 'r') as elems:
            nel = 0 # number of elements
            for element in elems:

                e = element.split(',')

                ei = e[1]
                e1 = e[2]
                e2 = e[3]
                e3 = e[4]
                e4 = e[5]
                e5 = e[6]
                e6 = e[7]
                e7 = e[8]
                e8 = e[9]

                # http://www.colorado.edu/engineering/CAS/courses.d/AFEM.d/AFEM.Ch11.d/AFEM.Ch11.pdf
                # Hex8 element p11-4
                d = "{0} 3 8 1 {1} {2} {3} {4} {5} {6} {7} {8} 1\n".format(ei,
                                                        e1, e2, e3, e4, e5, e6, e7, e8)
                d_file.write(d)

                nel += 1

        bnd_file.close()
        d_file.close()
        fix_file.close()

        # TODO: write file.dat


if __name__ == "__main__":

    print "Parse configuration file"
    mFE = microFE(sys.argv[1])

    print "Run mesher"
    # mFE.launchMatlabMesher()

    # TODO: get displacement from DVC?
    height = 0.02988
    displacement = 1e-3

    print "Convert mesh to ParaFEM format"
    mFE.convertMesh(height, displacement)
