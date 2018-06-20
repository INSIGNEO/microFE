import os
import sys
from argparse import ArgumentParser
from configparser import SafeConfigParser
import pydicom
from PIL import Image
from textwrap import dedent
import logging
import re
from datetime import datetime
import shutil


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

        self.start_logger()


        self.logger.info("Read .ini configuration file")
        p = SafeConfigParser()
        p.read(cfg_file_name)

        self.check_configuration_file(p)

        self.load_folders(p)
        self.check_folders()

        self.load_job_parameters(p)


        self.load_mesher_parameters(p)

        # fem parameters
        self.load_fem_parameters(p)
        self.check_fem_parameters()

        # batch job


        # convert DICOM to tiff format
        self.dcm2tiff()


    def start_logger(self):
        self.pwd = os.getcwd()

        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        self.log_name = ''.join(re.split('-|:| ',str(datetime.utcnow()).split('.')[0]))
        handler = logging.FileHandler("microFE-{0}.log".format(self.log_name))
        self.logger.addHandler(handler)
        self.logger.info(dedent("""
        ***********
        * microFE *
        ***********
        """))


    def check_configuration_file(self, p):
        """
        Check if the `.ini` configuration file contains all the required information.
        """
        self.logger.info("Check configuration file definition")

        sections = ["directories", "images", "mesher", "fem", "job"]

        options = [["ct_image_folder", "output_dir", "mesher_src", "ld_lib_path"],
                   ["img_name"],
                   ["threshold", "resolution"],
                   ["boundary_condition", "units", "sign", "amount", "direction",
                    "constrain", "E"],
                   ["name", "np"]]

        for section, opts in zip(sections, options):
            try:
                assert p.has_section(section)
            except:
                self.logger.error("\nERROR: {0} section not defined in configuration file".format(section))
                raise

            for option in opts:
                try:
                    assert p.has_option(section, option)
                except:
                    self.logger.error("\nERROR: {0} option not defined in configuration file".format(option))
                    raise

        # check plasticity definition
        if p.has_option("fem", "yield_stress") and p.has_option("fem", "Et"):
            self.yield_stress = p.get("fem", "yield_stress")
            self.Et = p.get("fem", "Et")
            self.plasticity = True
            self.logger.info("Bilinear elastic-plastic model definition detected")

        elif ((p.has_option("fem", "yield_stress") and not p.has_option("fem", "Et")) or \
                (not p.has_option("fem", "yield_stress") and p.has_option("fem", "Et"))):
            self.logger.error("\nERROR: elastic-plastic model requires yield_stress and Et")
            raise

        else:
            self.logger.info("! Elastic model definition detected")
            self.plasticity = False


    def load_folders(self, p):
        """
        Import folder paths from configuration file.
        """
        self.logger.info("Read paths from configuration file")

        self.ct_img_folder = p.get("directories", "ct_image_folder")
        self.out_folder = p.get("directories", "output_dir")
        self.mesher_src = p.get("directories", "mesher_src")
        self.LD_LIB_PATH = p.get("directories", "ld_lib_path")

        self.binary_folder = self.out_folder+"Binary/"
        self.tiff_folder = self.out_folder+"tiff/"

        self.img_name = p.get("images", "img_name")


    def check_folders(self):
        """
        Check if all the required folders exist. Create output folders.
        """
        self.logger.info("- Check paths")

        for folder in [self.ct_img_folder, self.mesher_src, self.LD_LIB_PATH]:
            try:
                assert os.path.isdir(self.ct_img_folder), "CT_IMAGES_FOLDER does not exist!"
            except:
                self.logger.error("\nERROR: {0} does not exist".format(folder))
                raise

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
        self.logger.info("Read mesher parameters from configuration file")

        self.threshold = p.get("mesher", "threshold")
        self.resolution = float(p.get("mesher", "resolution"))*1e-6


    def load_fem_parameters(self, p):
        """
        Import finite element model parameters from configuration file.
        """
        self.logger.info("Read FEM parameters from configuration file")

        self.young = p.get("fem", "E")
        self.boundary_condition = p.get("fem", "boundary_condition")
        self.units = p.get("fem", "units")
        self.sign = p.get("fem", "sign")
        self.amount = float(p.get("fem", "amount"))
        self.direction = p.get("fem", "direction")
        self.constrain = p.get("fem", "constrain")

        if self.plasticity:
            self.Et = p.get("fem", "Et")
            self.yield_stress = p.get("fem", "yield_stress")

    def check_fem_parameters(self):
        """
        Check if FEM parameters are correctly set.
        """
        self.logger.info("- Check FEM parameters")

        options = [self.boundary_condition, self.units, self.sign, self.direction,
                   self.constrain]
        values = [["displacement", "load"], ["mm", "percent", "N"],
                  ["positive", "negative"], ["x", "y", "z"], ["full", "free"]]
        messages = ["'boundary_condition' can be either 'displacement' or 'load'",
                    "Boundary condition 'units' can be either 'mm' or 'percent' for 'displacement' or 'N' in case of 'load'",
                    "Boundary condition 'sign' can be either 'positive' or 'negative'",
                    "Boundary condition 'direction' can be either 'x', 'y', or 'z'",
                    "Boundary condition 'constrain' can be either 'full' or 'free'"]

        for opt, vals, msg in zip(options, values, messages):
            try:
                assert opt in vals
            except:
                self.logger.error("\nERROR: {0}, not '{1}'".format(msg, opt))
                raise

        if self.boundary_condition == "displacement":
            try:
                assert self.units in ["mm", "percent"]
            except:
                self.logger.error("\nERROR: 'units' for 'displacement' boundary condition can be either 'mm' or 'percent', not '{0}'".format(self.units))
                raise

        elif self.boundary_condition == "load":
            try:
                assert self.units == "N"
            except:
                self.logger.error("\nERROR: 'units' for 'load' boundary condition can only be 'N', not '{0}'".format(self.units))
                raise


    def load_job_parameters(self, p):
        self.job_name = p.get("job", "name")
        self.np = p.get("job", "np")


    def dcm2tiff(self):
        """
        Convert DICOM image to a series of tiff images.
        """
        self.logger.info("Convert microCT image from DICOM to TIFF")

        try:
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
        except:
            self.logger.error("\nERROR: DICOM to TIFF conversion failed", exc_info=True)
            raise


    def run_matlab_mesher(self):
        '''
        Run the matlab mesher.
        '''
        sep = '" '
        pre = '"'

        mesher_params = [self.tiff_folder, self.tiff_wildcard, self.binary_folder,
                        self.resolution, self.threshold, self.out_folder]

        self.logger.info(dedent("""
        Run matlab mesher
        -----------------
        microCT image: {0}{3}
        resolution: {1}
        threshold: {2}
        """.format(self.ct_img_folder, self.resolution, self.threshold, self.img_name)))

        command = "{0}run_main.sh {1} ".format(self.mesher_src, self.LD_LIB_PATH)
        for p in mesher_params:
            command += pre+str(p)+sep

        self.logger.info(command)
        os.system(command)


    def setup_fem_bcs(self):
        """
        Set FEM boundary conditions.
        """
        if self.sign == "negative":
            self.amount *= -1.0

        if self.direction == "z":
            self.top_layer = self.height
            self.du = "UZ"
            self.fu = "FZ"
        elif self.direction == "x":
            self.top_layer = self.width
            self.du = "UX"
            self.fu = "FX"
        elif self.direction == "y":
            self.top_layer = self.lenght
            self.du = "UY"
            self.fu = "FY"

        if self.boundary_condition == "displacement":
            if self.units == "percent":
                self.displacement = self.top_layer*self.amount/100.0
            elif self.units == "mm":
                self.displacement = self.amount*1e-3

            self.apdl_bc = "D,all,{0},{1:15.15f}".format(self.du, self.displacement)

        elif self.boundary_condition == "load":
            self.load = self.amount
            self.apdl_bc = dedent("""Newton = {0}
            *GET,NoNodes,NODE,0,COUNT
            NewtonPerNode = Newton/NoNodes
            F,ALL,{1},NewtonPerNode
            """.format(self.load, self.fu))

        if self.constrain == "free":
            self.displacement_constrain = "D,ALL,{0},0".format(self.du)
        else:
            self.displacement_constrain = "D,all, , , , , ,ALL, , , , ,"

        self.logger.info(dedent("""
        Setup FEM
        ---------
        BC: {0}
         amount: {1} {2}
         direction: {3}
         constrain: {4}
        """.format(self.boundary_condition, self.amount, self.units, self.direction,
                   self.constrain)))

        if self.plasticity:
            self.logger.info(dedent("""
            Elastic-plastic model:
             Young's modulus: {0} Pa
             Yield stress {1} Pa
             Tangent modulus: {2} Pa
            """.format(self.young, self.yield_stress, self.Et)))

            self.plasticity_material = dedent("""TB,BISO,1
            TBDATA,1,{0},{1}
            """.format(self.yield_stress, self.Et))

            self.plasticity_solver = dedent("""NLGEOM,ON
            NSUBST,20,1000,1
            OUTRES,ALL,All
            AUTOTS,ON
            LNSRCH,ON
            NEQUIT,1000
            """)
        else:
            self.logger.info(dedent("""
            Elastic model:
             Young's modulus: {0} Pa
            """.format(self.young)))

            self.plasticity_material = " "
            self.plasticity_solver = " "


    def write_ansys_model(self):
        """
        Write ANSYS script to `fe_model.txt` file.
        """
        self.logger.info("Write Ansys apdl script")

        with open("{0}fe_model.txt".format(self.out_folder), 'w') as f:
            opts = {"out_folder": self.out_folder, "job_name": self.job_name,
                    "direction": self.direction, "top_layer": self.top_layer,
                    "DU": self.du, "apdl_bc": self.apdl_bc,
                    "constrain": self.displacement_constrain,
                    "young": self.young, "plasticity_material": self.plasticity_material,
                    "plasticity_solver": self.plasticity_solver}

            f.write(dedent("""\
            /prep7
            ET,1,SOLID185
            MP,EX,1,{young}
            MP,PRXY,1,0.3
            {plasticity_material}
            /nopr
            /INPUT,'{out_folder}nodedata','txt'
            /INPUT,'{out_folder}elementdata','txt'
            /gopr
            nsel,s,loc,{direction},0
            {constrain}
            nsel,s,loc,{direction},{top_layer:15.15f}
            {apdl_bc}
            allsel

            /Solu
            {plasticity_solver}
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


    def run_ansys_model(self):
        """
        Execute Ansys on ShARC.
        """
        self.logger.info("Run FEM")
        os.chdir(self.out_folder)

        command = "ansys172 -dis -i fe_model.txt -j {0} ".format(self.job_name)
        command+= "-mpi=intelmpi -rsh -sgepe mpi-rsh -np {0}".format(self.np)

        self.logger.info(command)
        os.system(command)


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("-c", "--config_file", help=".ini file name", dest="cfg_file")
    args = parser.parse_args()

    mFE = microFE(args.cfg_file)
    mFE.run_matlab_mesher()

    mFE.setup_fem_bcs()
    mFE.write_ansys_model()
    mFE.run_ansys_model()

    shutil.move("{0}/microFE-{1}.log".format(mFE.pwd, mFE.log_name),
                "{0}microFE.py.log".format(mFE.out_folder))
