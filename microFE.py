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

    def __init__(self, cfg_file_name, check=True):
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

        self.load_folders(p)

        if check:
            self.check_configuration_file(p)
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


    def check_configuration_file(self, p):
        options = [["ct_images_folder", "output_dir", "mesher_src", "ld_lib_path"],
                    ["img_names"], ["threshold", "image_resolution", "perc_displacement"],
                    ["name"]]
        sections = ["directories", "images", "mesher_parameters", "job"]

        for section, opts in zip(sections, options):
            assert p.has_section(section), "{0} section not defined in configuration file".format(section)

            for option in opts:
                assert p.has_option(section, option), "{0} option not defined in configuration file".format(option)

    def load_folders(self, p):
        self.ct_images_folder = p.get("directories", "ct_images_folder")
        self.img_names = p.get("images", "img_names")
        self.out_folder = p.get("directories", "output_dir")
        self.binary_folder = self.out_folder+"/Binary/"
        self.MESHER_SRC = p.get("directories", "mesher_src")
        self.LD_LIB_PATH = p.get("directories", "ld_lib_path")

    def check_folders(self, p):
        # input folder
        assert os.path.isdir(self.ct_images_folder), "CT_IMAGES_FOLDER does not exist!"

        # output folder
        if not os.path.isdir(self.out_folder):
            os.mkdir(self.out_folder)
        elif (os.path.isfile("{0}/elementdata.txt".format(self.out_folder)) or
                os.path.isfile("{0}/nodedata.txt".format(self.out_folder))):
            answer = raw_input("WARNING: Mesh files already in OUTPUT_DIR = {0}, would you like to overwrite? y/[n] ".format(self.out_folder))
            assert(answer == "y"), "Change OUTPUT_DIR in the configuration file and restart microFE.py"

        if not os.path.isdir(self.binary_folder):
            os.mkdir(self.binary_folder)

        # mesher directories
        assert os.path.isdir(self.MESHER_SRC), "MESHER_SRC does not exist!"
        assert os.path.isdir(self.LD_LIB_PATH), "LD_LIB_PATH does not exist!"


    def run_matlab_mesher(self):
        '''
        Return the matlab mesher.
        '''

        sep = '" '
        pre = '"'

        command = "{0}run_main.sh {1} ".format(self.MESHER_SRC, self.LD_LIB_PATH)
        for p in self.mesher_params:
            command += pre+str(p)+sep
        os.system(command)


    def write_ansys_model(self):
        with open("fe_model.txt", 'w') as f:
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
            f.write("nsel,s,loc,z,{0}\n".format(self.height))
            f.write("D,all,UZ,-{0}\n".format(self.displacement))
            f.write("allsel\n")
            f.write("/Solu\n")
            f.write("Antype,0\n")
            f.write("eqslv,pcg\n")
            f.write("solve\n")
            f.write("SAVE,'{0}','db'\n".format(self.job_name))
            f.write("/exit,nosave")


    def compute_height_and_displacement(self):
        max_node_z = 0.0
        with open("{0}/nodedata.txt".format(self.out_folder), 'r') as f:
            for line in f:
                z = float(line.strip().split(',')[-1])
                if z > max_node_z:
                    max_node_z = z
        self.height = max_node_z
        self.displacement = self.height*self.perc_displacement/100.0

    def run_ansys_model(self):
        command = "ansys172 -p aa_r -dir {0}".format(self.out_folder)
        command += " -j {0}".format(self.job_name)
        command += " -s read -l en-us -b -i fe_model.txt"
        command += " -o {0}output.out".format(self.out_folder)
        os.system(command)
        # print command

if __name__ == "__main__":

    parser = ArgumentParser()

    parser.add_argument("-c", "--config_file", help=".ini file name", dest="cfg_file")
    parser.add_argument("-r", "--run_cmd", help="'mesh' or 'fem'", dest="cmd")

    args = parser.parse_args()

    if args.cmd == "mesh":
        mFE = microFE(args.cfg_file)
        mFE.run_matlab_mesher()

    else:
        mFE = microFE(args.cfg_file, check=False)
        mFE.compute_height_and_displacement()
        mFE.write_ansys_model()
        mFE.run_ansys_model()
