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

    #
    # def convertMesh(self):
    #     '''
    #     Convert matlab output files to ParaFEM input files.
    #     '''
    #
    #     # system geometry
    #     d_file = open("{0}/{1}.d".format(self.parafem_dir, self.job_name), 'w')
    #     d_file.write("*THREE_DIMENSIONAL\n")
    #     d_file.write("*NODES\n")
    #     self.nnod = 0 # nodes counter
    #     self.nel = 0 # elements counter
    #     self.nodpel = 8 # number of nodes per element
    #
    #     # constrained DOFs
    #     bnd_file = open("{0}/{1}.bnd".format(self.parafem_dir, self.job_name), 'w')
    #     self.nres = 0 # constrained nodes counter
    #
    #     # prescribed displacements != 0
    #     fix_file = open("{0}/{1}.fix".format(self.parafem_dir, self.job_name), 'w')
    #     self.nfixnod = 0 # fixed nodes counter
    #     height = 0.0
    #
    #     # prescribed loads
    #     lds_file = open("{0}/{1}.lds".format(self.parafem_dir, self.job_name), 'w')
    #     self.nlnod = 0 # loaded nodes counter
    #
    #     #---------------------------------------------------------------------------------
    #
    #     # Write lds and bnd file
    #     # Loops through nodedata.txt and finds the max z-coordinate
    #     # this will be used to assign displacement to uppermost nodes.
    #     # Nodes with nz=0 are constrained, a zero load along x, y, and z is also assigned.
    #
    #     # TODO: find highest node directly in matlab rather than here
    #
    #     with open("{0}/nodedata.txt".format(self.out_folder), 'r') as nodes:
    #         for node in nodes:
    #             n = node.strip().split(',')
    #
    #             ni = n[1]
    #             nx = float(n[2])
    #             ny = float(n[3])
    #             nz = float(n[4])
    #
    #             # add node to nodes list
    #             d = "{0} {1} {2} {3}\n".format(ni, nx, ny, nz)
    #             d_file.write(d)
    #             self.nnod += 1
    #
    #             # find highest (z-wise) nodes
    #             if nz > height:
    #                 height = nz
    #
    #
    #
    #             # constrain bottom nodes
    #             if nz == 0.0:
    #                 b = "{0} 1 1 1\n".format(ni)
    #                 bnd_file.write(b)
    #                 self.nres += 1
    #
    #             # assign zero load
    #             l = "{0} 0.0 0.0 0.0\n".format(ni)
    #             lds_file.write(l)
    #             self.nlnod += 1
    #
    #     bnd_file.close()
    #     lds_file.close()
    #
    #     # Compute upper face displacement as percentage of model height
    #     # perc_displacement is user-assigned in the configuration file
    #     displacement = height * self.perc_displacement / 100.0
    #
    #     #---------------------------------------------------------------------------------
    #
    #     # Assign displacement while iterating again over nodedata
    #     with open("{0}/nodedata.txt".format(self.out_folder), 'r') as nodes:
    #         for node in nodes:
    #             n = node.strip().split(',')
    #
    #             ni = n[1]
    #             nz = float(n[4])
    #
    #             # assign displacement to upper nodes
    #             if nz == height: # displacement only along z-axis
    #                 f = "{0} 3 {1}\n".format(ni, displacement)
    #                 fix_file.write(f)
    #                 self.nfixnod += 1
    #     fix_file.close()
    #
    #     #---------------------------------------------------------------------------------
    #
    #     # Write elements in d file
    #
    #     d_file.write("*ELEMENTS\n")
    #     with open("{0}/elementdata.txt".format(self.out_folder), 'r') as elems:
    #         for element in elems:
    #             self.nel += 1
    #
    #             e = element.strip().split(',')
    #
    #             ei = self.nel # element index
    #
    #             # element nodes indices
    #             e1 = e[1]
    #             e2 = e[2]
    #             e3 = e[3]
    #             e4 = e[4]
    #             e5 = e[5]
    #             e6 = e[6]
    #             e7 = e[7]
    #             e8 = e[8]
    #
    #             #    8-------7
    #             #   /|      /|
    #             #  / |     / |
    #             # 5-------6  |
    #             # |  4----|--3
    #             # | /     | /
    #             # |/      |/
    #             # 1-------2
    #
    #             d = "{0} 3 8 1 {1} {2} {3} {4} {5} {6} {7} {8} 1\n".format(ei, e1, e2, e3,
    #                                                                     e4, e5, e6, e7, e8)
    #             d_file.write(d)
    #     d_file.close()
    #
    #
    # def writeDat(self):
    #     '''
    #     Write .dat file with the following structure
    #
    #     nel  nnod nres nlnod nfixnod nip
    #     limit tol e (Young) v (Poisson)
    #     nodpel
    #     nloadstep jump
    #     tol2
    #     '''
    #     with open("{0}/{1}.dat".format(self.parafem_dir, self.job_name), 'w') as dat:
    #         line = "{0} {1} {2} {3} {4} {5}\n".format(self.nel, self.nnod, self.nres,
    #                                                   self.nlnod, self.nfixnod, self.nip)
    #         dat.write(line)
    #
    #         line = "{0} {1} {2} {3}\n".format(self.limit, self.tol, self.E, self.vP)
    #         dat.write(line)
    #
    #         dat.write("{0}\n".format(self.nodpel))
    #         dat.write("{0} {1}\n".format(self.nloadstep, self.jump))
    #         dat.write("{0}\n".format(self.tol2))


    def write_batch_file(self):
        with open("job.sh", 'w') as f:
            f.write("#!/bin/bash\n")

            if self.mail != False:
                f.write("#$ -M {0}\n".format(self.mail))
                f.write("#$ -m bea\n")

            if self.walltime != False:
                f.write("#$ -l h_rt={0}\n".format(self.walltime))

            f.write("#$ -l rmem={0}G\n".format(self.rmem))

            f.write("#$ -N {0}\n\n".format(self.job_name))

            f.write("module load apps/matlab/2016a/binary\n")

            command = self.matlab_mesher_cmd()
            f.write("{0}\n".format(command))


if __name__ == "__main__":

    parser = ArgumentParser()

    parser.add_argument("-c", "--config_file", help=".ini file name", dest="cfg_file")
    # parser.add_argument("-r", "--runcmd", help="run 'mesh' or 'convert'", dest="cmd")

    args = parser.parse_args()

    print "Parse configuration file"
    mFE = microFE(args.cfg_file)

    mFE.write_batch_file()

    os.system("qsub job.sh")

    # submit batch job
    #
    # if args.cmd == "mesh":
    #     print "Run mesher"
    #     mFE.write_batch_file()
    #     # mFE.launchMatlabMesher()
    #
    # elif args.cmd == "convert":
    #
    #     # TODO: get displacement from DVC
    #
    #     print "Convert mesh to ParaFEM format"
    #     mFE.convertMesh()
    #     mFE.writeDat()
