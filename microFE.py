#!/usr/bin/python

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
from argparse import ArgumentParser
from ConfigParser import SafeConfigParser

class microFE():
    def __init__(self, file_name):
        '''
        Read .ini configuration file and create output directory
        '''

        # parse .ini configuration file
        p = SafeConfigParser()
        p.read(file_name)

        # CT images
        self.file_folder = p.get("directories", "file_folder")
        self.binary_folder = p.get("directories", "binary_folder")
        self.out_folder = p.get("directories", "out_dir")
        self.img_names = p.get("images", "img_names")

        assert os.path.isdir(self.file_folder), "IMG folder does not exist"

        # mesher
        self.threshold = p.get("mesher_parameters", "threshold")
        self.Image_Resolution = p.get("mesher_parameters", "Image_Resolution")
        self.M_FILES = p.get("directories", "m_files")
        self.LD_LIB_PATH = p.get("directories", "ld_lib_path")

        assert os.path.isdir(self.M_FILES), "M_FILES folder does not exist"

        self.job_name = p.get("job", "name")

        self.mesher_params = [self.file_folder, self.img_names, self.binary_folder,
            self.Image_Resolution, self.threshold, self.out_folder]

        # ParaFEM
        self.nip = p.get("parafem_parameters", "nip")
        self.limit = p.get("parafem_parameters", "limit")
        self.tol = p.get("parafem_parameters", "tol")
        self.E = p.get("parafem_parameters", "E")
        self.vP = p.get("parafem_parameters", "vP")
        self.nloadstep = p.get("parafem_parameters", "nloadstep")
        self.jump = p.get("parafem_parameters", "jump")
        self.tol2 = p.get("parafem_parameters", "tol2")

        # create output folder
        if not os.path.isdir(self.out_folder):
            os.mkdir(self.out_folder)

        if not os.path.isdir(self.binary_folder):
            os.mkdir(self.binary_folder)

        return


    def launchMatlabMesher(self):
        '''
        Launch the matlab mesher.
        '''

        sep = '" '
        pre = '"'

        command = "{0}run_main.sh {1} ".format(self.M_FILES, self.LD_LIB_PATH)
        for p in self.mesher_params:
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
        self.nfixnod = 0

        lds_file = open("{0}/{1}.lds".format("parafem_inputs", self.job_name), 'w')
        lds_file.close() # we do not prescribe loads...right?
        self.nlnod = 0 # number of loaded nodes

        d_file.write("*THREE_DIMENSIONAL\n")
        d_file.write("*NODES\n")

        with open("{0}/nodedata.txt".format(self.out_folder), 'r') as nodes:
            self.nnod = 0 # number of nodes
            self.nres = 0 # number of constrained nodes
            for node in nodes:
                n = node.split(',')

                ni = n[1]
                nx = float(n[2])
                ny = float(n[3])
                nz = float(n[4])

                if nz == 0:
                    b = "{0} 1 1 1\n".format(ni)
                    bnd_file.write(b)

                    self.nres += 1

                d = "{0} {1} {2} {3}\n".format(ni, nx, ny, nz)
                d_file.write(d)

                if nz == height: # displacement only along z-axis
                    f = "{0} 3 {1}\n".format(ni, displacement)
                    fix_file.write(f)

                    self.nfixnod += 1

                self.nnod += 1

        d_file.write("*ELEMENTS\n")
        self.nodpel = 8 # number of nodes per element; Hex8 element p.11-4
        # http://www.colorado.edu/engineering/CAS/courses.d/AFEM.d/AFEM.Ch11.d/AFEM.Ch11.pdf

        with open("{0}/elementdata.txt".format(self.out_folder), 'r') as elems:
            self.nel = 0 # number of elements
            for element in elems:
                self.nel += 1

                e = element.split(',')

                ei = self.nel # element index

                # element nodes indices
                e1 = e[0]
                e2 = e[1]
                e3 = e[2]
                e4 = e[3]
                e5 = e[4]
                e6 = e[5]
                e7 = e[6]
                e8 = e[7]

                #    8=======7
                #   /|      /|
                #  / |     / |
                # 5=======6--3
                # | /     | /
                # |/      |/
                # 1=======2

                d = "{0} 3 8 1 {1} {2} {3} {4} {5} {6} {7} {8} 1\n".format(ei,
                                                        e1, e2, e3, e4, e5, e6, e7, e8)
                d_file.write(d)

        bnd_file.close()
        d_file.close()
        fix_file.close()


    def writeDat(self):
        with open("{0}/{1}.dat".format("parafem_inputs", self.job_name), 'w') as dat:
            line = "{0} {1} {2} {3} {4} {5}\n".format(self.nel, self.nnod, self.nres,
                                                      self.nlnod, self.nfixnod, self.nip)
            dat.write(line)

            line = "{0} {1} {2} {3}\n".format(self.limit, self.tol, self.E, self.vP)
            dat.write(line)

            dat.write("{}\n".format(self.nodpel))
            dat.write("{0} {1}\n".format(self.nloadstep, self.jump))
            dat.write("{}".format(self.tol2))


if __name__ == "__main__":

    parser = ArgumentParser()

    parser.add_argument("-c", "--cfgfile", help="configuration file name", dest="cfgfile")
    parser.add_argument("-r", "--runcmd", help="run command 'mesh' or 'convert'",
                        dest="cmd")
    args = parser.parse_args()

    print "Parse configuration file"
    mFE = microFE(args.cfgfile)

    if args.cmd == "mesh":
        print "Run mesher"
        mFE.launchMatlabMesher()

    elif args.cmd == "convert":

        # TODO: find highest node z-coordinate
        # TODO: get displacement from DVC
        height = 0.02988
        displacement = 1e-3

        print "Convert mesh to ParaFEM format"
        mFE.convertMesh(height, displacement)
        mFE.writeDat()
