import os
import sys
from argparse import ArgumentParser
from configparser import SafeConfigParser
import pydicom
from PIL import Image
from textwrap import dedent


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
        self.check_configuration_file(p)

        self.load_folders(p)
        self.check_folders()

        # mesher parameters
        self.load_mesher_parameters(p)

        # fem parameters
        self.load_fem_parameters(p)
        self.check_fem_parameters()

        # batch job
        self.load_job_parameters(p)

        # convert DICOM to tiff format
        self.dcm2tiff()


    def check_configuration_file(self, p):
        """
        Check if the `.ini` configuration file contains all the required information.
        """
        sections = ["directories", "images", "mesher", "fem", "job"]

        options = [["ct_image_folder", "output_dir", "mesher_src", "ld_lib_path"],
                   ["img_name"],
                   ["threshold", "resolution"],
                   ["boundary_condition", "units", "sign", "amount", "direction",
                    "constrain"],
                   ["name"]]

        for section, opts in zip(sections, options):
            assert p.has_section(section), "{0} section not defined in configuration file".format(section)

            for option in opts:
                assert p.has_option(section, option), "{0} option not defined in configuration file".format(option)


    def load_folders(self, p):
        """
        Import folder paths from configuration file.
        """
        self.ct_img_folder = p.get("directories", "ct_image_folder")
        self.out_folder = p.get("directories", "output_dir")
        self.mesher_src = p.get("directories", "mesher_src")
        self.LD_LIB_PATH = p.get("directories", "ld_lib_path")

        self.binary_folder = self.out_folder+"/Binary/"
        self.tiff_folder = self.out_folder+"/tiff/"

        self.img_name = p.get("images", "img_name")


    def check_folders(self):
        """
        Check if all the required folders exist. Create output folders.
        """
        assert os.path.isdir(self.ct_img_folder), "CT_IMAGES_FOLDER does not exist!"
        assert os.path.isdir(self.mesher_src), "MESHER_SRC does not exist!"
        assert os.path.isdir(self.LD_LIB_PATH), "LD_LIB_PATH does not exist!"

        # output folders
        # TODO: if a folder already exist, ask before overwriting previous results.

        if not os.path.isdir(self.out_folder):
            os.mkdir(self.out_folder)

        if not os.path.isdir(self.binary_folder):
            os.mkdir(self.binary_folder)

        if not os.path.isdir(self.tiff_folder):
            os.mkdir(self.tiff_folder)


    def load_mesher_parameters(self, p):
        """
        Import mesher parameters.
        Convert image resolution from micron to meters.
        """
        self.threshold = p.get("mesher", "threshold")
        self.resolution = float(p.get("mesher", "resolution"))*1e-6


    def load_fem_parameters(self, p):
        """
        Import finite element model parameters from configuration file.
        """
        self.boundary_condition = p.get("fem", "boundary_condition")
        self.units = p.get("fem", "units")
        self.sign = p.get("fem", "sign")
        self.amount = float(p.get("fem", "amount"))
        self.direction = p.get("fem", "direction")
        self.constrain = p.get("fem", "constrain")


    def check_fem_parameters(self):
        """
        Check if FEM parameters are correctly set.
        """
        assert self.boundary_condition in ["displacement", "load"], "'boundary_condition' can be either 'displacement' or 'load'."

        assert self.units in ["mm", "percent", "N"], "Boundary condition 'units' can be either 'mm' or '%' for 'displacement' or 'N' in case of 'load'."

        if self.boundary_condition == "displacement":
            assert self.units in ["mm", "percent"], "'units' for 'displacement' boundary condition can be either 'mm' or 'percent'."
        elif self.boundary_condition == "load":
            assert self.units == "N", "'units' for 'load' boundary condition can only be 'N'."

        assert self.sign in ["positive", "negative"], "Boundary condition 'sign' can be either 'positive' or 'negative'."

        assert self.direction in ["x", "y", "z"], "Boundary condition 'direction' can be either 'x', 'y', or 'z'."

        assert self.constrain in ["full", "free"], "Boundary condition 'constrain' can be either 'full' or 'free'."


    def load_job_parameters(self, p):
        self.job_name = p.get("job", "name")


    def dcm2tiff(self):
        """
        Convert DICOM image to a series of tiff images.
        """
        d_img = pydicom.read_file("{0}/{1}".format(self.ct_img_folder, self.img_name))
        self.tiff_name = self.img_name.split('.')[0]

        for z in range(d_img.pixel_array.shape[0]):
            z_img = d_img.pixel_array[z,:,:]
            t_img = Image.fromarray(z_img)
            t_img.save("{0}/{1}_{2:04d}.tif".format(self.tiff_folder, self.tiff_name, z))

        self.width = z_img.shape[0]*self.resolution
        self.lenght = z_img.shape[1]*self.resolution
        self.height = d_img.pixel_array.shape[0]*self.resolution

        self.tiff_wildcard = self.img_name.split('.')[0] + "_****.tif"


    def run_matlab_mesher(self):
        '''
        Run the matlab mesher.
        '''

        sep = '" '
        pre = '"'

        mesher_params = [self.tiff_folder, self.tiff_wildcard, self.binary_folder,
                        self.resolution, self.threshold, self.out_folder]

        command = "{0}run_main.sh {1} ".format(self.mesher_src, self.LD_LIB_PATH)
        for p in mesher_params:
            command += pre+str(p)+sep

        os.system(command)


    def setup_fem_bcs(self):
        """
        Set FEM boundary conditions.
        """
        if self.direction == "z":
            self.top_layer = self.height
            self.du = "UZ"
        elif self.direction == "x":
            self.top_layer = self.width
            self.du = "UX"
        elif self.direction == "y":
            self.top_layer = self.lenght
            self.du = "UY"

        if self.boundary_condition == "displacement":
            self.load = 0.0

            if self.units == "percent":
                self.displacement = self.top_layer*self.amount/100.0
            elif self.units == "mm":
                self.displacement = self.amount*1e-3

        # TODO: "load" BC

        if self.sign == "negative":
            self.displacement *= -1.0
            self.load *= -1.0


    def write_ansys_model(self):
        """
        Write ANSYS script to `fe_model.txt` file.
        """
        with open("{0}fe_model.txt".format(self.out_folder), 'w') as f:
            opts = {"out_folder": self.out_folder, "job_name": self.job_name,
                    "direction": self.direction, "top_layer": self.top_layer,
                    "DU": self.du, "displacement": self.displacement}

            # TODO:
            # - load BC
            # - free/full constrain

            f.write(dedent("""\
            /prep7
            ET,1,SOLID185
            MP,EX,1,17000
            MP,PRXY,1,0.3
            /nopr
            /INPUT,'{out_folder}nodedata','txt'
            /INPUT,'{out_folder}elementdata','txt'
            /gopr
            nsel,s,loc,{direction},0
            D,all, , , , , ,ALL, , , , ,
            nsel,s,loc,{direction},{top_layer:15.15f}
            D,all,{DU},{displacement:15.15f}
            allsel

            /Solu
            Antype,0
            eqslv,pcg
            solve
            SAVE,'{job_name}','db'

            /POST1
            SET,Last
            *get,nNodes,NODE,0,count
            *DIM,Nodal_strain,ARRAY,nNodes,4
            N = 0
            *do,i,1,nNodes
            *GET,Nodal_strain(i,1),NODE,N,NXTH
            N = Nodal_strain(i,1)
            *GET,Nodal_strain(i,2),NODE,Nodal_strain(i,1),U,X
            *GET,Nodal_strain(i,3),NODE,Nodal_strain(i,1),U,Y
            *GET,Nodal_strain(i,4),NODE,Nodal_strain(i,1),U,Z
            *enddo
            *cfopen,'NodalDisplacements',txt
            *vwrite,Nodal_strain(1,1),Nodal_strain(1,2),Nodal_strain(1,3),Nodal_strain(1,4)
            (F10.0,TL1,' ','  'F15.10,'  ',F15.10'  ',F15.10)
            *cfclose
            FINISH
            /exit,nosave
            """.format(**opts)))

    #
    # def compute_height_and_displacement(self):
    #     max_node_z = 0.0
    #     with open("{0}/nodedata.txt".format(self.out_folder), 'r') as f:
    #         for line in f:
    #             z = float(line.strip().split(',')[-1])
    #             if z > max_node_z:
    #                 max_node_z = z
    #     self.height = max_node_z
    #     self.displacement = self.height*self.perc_displacement/100.0
    #
    #
    # def compute_lenght_width_height(self):
    #     max_node_x = 0.0
    #     max_node_y = 0.0
    #     max_node_z = 0.0
    #
    #     with open("{0}/nodedata.txt".format(self.out_folder), 'r') as f:
    #         for line in f:
    #             x = float(line.strip().split(',')[2])
    #             y = float(line.strip().split(',')[3])
    #             z = float(line.strip().split(',')[4])
    #
    #             if x > max_node_x:
    #                 max_node_x = x
    #
    #             if y > max_node_y:
    #                 max_node_y = y
    #
    #             if z > max_node_z:
    #                 max_node_z = z
    #
    #     self.lenght = max_node_x
    #     self.width = max_node_y
    #     self.height = max_node_z
    #
    #
    # def simple_BC(self):
    #     slices = len(os.listdir(self.binary_folder))
    #
    #     self.displacement = self.height*self.perc_displacement/100.0


    def run_ansys_model(self):
        """
        Execute Ansys on ShARC.
        """
        command = "ansys172 -i fe_model.txt -j {1}".format(self.out_folder, self.job_name)
        os.chdir("{0}".format(self.out_folder))
        os.system(command)


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("-c", "--config_file", help=".ini file name", dest="cfg_file")
    args = parser.parse_args()

    mFE = microFE(args.cfg_file)
    # mFE.run_matlab_mesher()

    mFE.setup_fem_bcs()
    mFE.write_ansys_model()
    # mFE.run_ansys_model()
