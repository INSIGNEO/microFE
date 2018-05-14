#!/usr/bin/python

'''
File: microFE.py
Author: A Melis
'''

__author__ = "Alessandro Melis"
__copyright__ = "Copyright 2017 INSIGNEO Institute for in silico Medicine"
__credits__ = ["A Melis", "Y. Chen"]
__version__ = "0.0.2"
__maintainer__ = "Alessandro Melis"
__email__ = "a.melis@sheffield.ac.uk"

import os
import sys
from argparse import ArgumentParser
from ConfigParser import SafeConfigParser


class microFE():
    '''
    microFE class definition.
    '''

    def __init__(self, cfg_file_name):
        '''
        Read .ini configuration file and create output directory

        Parameters
        ----------
        cfg_file_name : str
            Configuration file name.
        '''

        # parse .ini configuration file
        p = SafeConfigParser()
        p.read(cfg_file_name)

        # check
        self.check_configuration_file(p)

        # input CT images
        self.check_folders(p)

        # mesher parameters
        self.load_mesher_parameters(p)

        # batch job
        self.load_job_parameters(p)


    def load_mesher_parameters(self, p):
        self.threshold = p.get("mesher_parameters", "threshold")
        self.image_resolution = p.get("mesher_parameters", "image_resolution")
        self.perc_displacement = float(p.get("mesher_parameters", "perc_displacement"))
        self.mesher_params = [self.ct_images_folder, self.img_names, self.binary_folder,
            self.image_resolution, self.threshold, self.out_folder]


    def load_job_parameters(self, p):
        self.job_name = p.get("job", "name")
        self.rmem = p.get("job", "rmem")

        if not p.has_option("job", "mail"):
            print "WARNING: mail address not specified"
            self.mail = False
        else:
            self.mail = p.get("job", "mail")

        if not p.has_option("job", "walltime"):
            print "WARNING: walltime not specified: set default 96hrs"
            self.walltime = False
        else:
            self.walltime = p.get("job", "walltime")


    def check_configuration_file(self, p):
        options = [["ct_images_folder", "output_dir", "mesher_src", "ld_lib_path"],
                    ["img_names"], ["threshold", "image_resolution", "perc_displacement"],
                    ["name", "rmem"]]
        sections = ["directories", "images", "mesher_parameters", "job"]

        for section, opts in zip(sections, options):
            assert p.has_section(section), "{0} section not defined in configuration file".format(section)

            for option in opts:
                assert p.has_option(section, option), "{0} option not defined in configuration file".format(option)


    def check_folders(self, p):
        # input folder
        self.ct_images_folder = p.get("directories", "ct_images_folder")
        assert os.path.isdir(self.ct_images_folder), "CT_IMAGES_FOLDER does not exist!"
        self.img_names = p.get("images", "img_names")

        # output folder
        self.out_folder = p.get("directories", "output_dir")
        if not os.path.isdir(self.out_folder):
            os.mkdir(self.out_folder)
        elif (os.path.isfile("{0}/elementdata.txt".format(self.out_folder)) or
                os.path.isfile("{0}/nodedata.txt".format(self.out_folder))):
            answer = raw_input("WARNING: Mesh files already in OUTPUT_DIR = {0}, would you like to overwrite? y/[n] ".format(self.out_folder)) or "n"
            if answer != "y":
                print "Change OUTPUT_DIR in the configuration file and restart microFE.py"

        self.binary_folder = self.out_folder+"/Binary/"
        if not os.path.isdir(self.binary_folder):
            os.mkdir(self.binary_folder)

        # mesher directories
        self.MESHER_SRC = p.get("directories", "mesher_src")
        self.LD_LIB_PATH = p.get("directories", "ld_lib_path")
        assert os.path.isdir(self.MESHER_SRC), "MESHER_SRC does not exist!"
        assert os.path.isdir(self.LD_LIB_PATH), "LD_LIB_PATH does not exist!"


    def matlab_mesher_cmd(self):
        '''
        Return the matlab mesher.
        '''

        sep = '" '
        pre = '"'

        command = "{0}run_main.sh {1} ".format(self.MESHER_SRC, self.LD_LIB_PATH)
        for p in self.mesher_params:
            command += pre+str(p)+sep
        return command


    def write_ansys_model(self):
        with open("fe_model-1.txt", 'w') as f:
            f.write("/prep7\n")
            f.write("ET,1,SOLID185\n")
            f.write("MP,EX,1,17000\n")
            f.write("MP,PRXY,1,0.3\n")
            f.write("/nopr\n")
            f.write("/INPUT,'{0}/nodedata','txt'\n".format(self.out_folder))
            f.write("/INPUT,'{0}/elementdata','txt'\n".format(self.out_folder))
            f.write("/gopr\n")
            f.write("nsel,s,loc,z,0\n")
            f.write("D,all, , , , , ,ALL, , , , ,\n")

        with open("fe_model-2.txt", 'w') as f:
            f.write("allsel\n")
            f.write("/Solu\n")
            f.write("Antype,0\n")
            f.write("eqslv,pcg\n")
            f.write("solve\n")
            f.write("SAVE,'{0}','db'\n".format(self.job_name))
            f.write("/exit,nosave")


    def write_batch_file(self):
        with open("job.sh", 'w') as f:
            f.write("#!/bin/bash\n")

            if self.mail != False:
                f.write("#$ -M {0}\n".format(self.mail))
                f.write("#$ -m bea\n")

            if self.walltime != False:
                f.write("#$ -l h_rt={0}\n".format(self.walltime))

            f.write("#$ -l rmem={0}G\n".format(self.rmem))

            f.write("#$ -N {0}\n".format(self.job_name))
            f.write("\n")

            f.write("module load apps/matlab/2016a/binary\n")
            f.write("module load apps/ansys/16.1\n")
            f.write("\n")

            mesh_command = self.matlab_mesher_cmd()
            f.write("{0}\n".format(mesh_command))
            f.write("\n")

            f.write("A=$(tail -n 1 {0}/nodedata.txt) | ".format(self.out_folder))
            f.write("B=$(cut -d',' -f5 <<< $A)\n")
            f.write('echo "nsel,s,loc,z,$B" >> fe_model-1.txt\n')
            f.write('echo "nsel,s,loc,z,$B" >> fe_model-1.txt\n')
            f.write('C=$(python -c "import sys; print ')
            f.write('float(sys.argv[1])/100.0*float(sys.argv[1])" $B {0})'.format(self.perc_displacement))
            f.write('echo "D,all,UZ,-$C" >> fe_model-1.txt\n')
            f.write('cat fe_model-1.txt fe_model-2.txt > fe_model.txt\n')

            ansys_command = "ansys172 -p aa_r -dir {0} ".format(self.out_folder)
            ansys_command += "-j {0} -s read -l en-us -b ".format(self.job_name)
            ansys_command += "-i fe_model.txt "
            ansys_command += "-o {0}/output.out\n".format(self.out_folder)
            f.write("{0}".format(ansys_command))

if __name__ == "__main__":

    parser = ArgumentParser()

    parser.add_argument("-c", "--config_file", help=".ini file name", dest="cfg_file")
    # parser.add_argument("-r", "--runcmd", help="run 'mesh' or 'convert'", dest="cmd")

    args = parser.parse_args()

    mFE = microFE(args.cfg_file)

    mFE.write_ansys_model()

    mFE.write_batch_file()
    os.system("qsub job.sh")

    # A=$(tail -n 1 outputs/nodedata.txt) | B=$(cut -d',' -f5 <<< $A) | echo "$B"
