import os
import sys
from argparse import ArgumentParser
from configparser import SafeConfigParser
import pydicom
from PIL import Image


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

        self.dcm2tiff()

        # mesher parameters
        self.load_mesher_parameters(p)

        # batch job
        self.load_job_parameters(p)


    def dcm2tiff(self):
        d_img = pydicom.read_file("{0}/{1}".format(self.ct_img_folder, self.img_name))
        self.tiff_name = self.img_name.split('.')[0]
        for z in range(d_img.pixel_array.shape[0]):
            z_img = d_img.pixel_array[z,:,:]
            t_img = Image.fromarray(z_img)
            t_img.save("{0}/{1}_{2:04d}.tif".format(self.tiff_folder, self.tiff_name, z))
        self.tiff_wildcard = self.img_name.split('.')[0] + "_****.tif"


    def load_mesher_parameters(self, p):
        self.threshold = p.get("mesher_parameters", "threshold")
        self.image_resolution = p.get("mesher_parameters", "image_resolution")
        self.perc_displacement = float(p.get("mesher_parameters", "perc_displacement"))
        self.mesher_params = [self.tiff_folder, self.tiff_wildcard, self.binary_folder,
                                self.image_resolution, self.threshold, self.out_folder]


    def load_job_parameters(self, p):
        self.job_name = p.get("job", "name")


    def check_configuration_file(self, p):
        options = [["ct_images_folder", "output_dir", "mesher_src", "ld_lib_path"],
                    ["img_name"], ["threshold", "image_resolution", "perc_displacement"],
                    ["name"]]
        sections = ["directories", "images", "mesher_parameters", "job"]

        for section, opts in zip(sections, options):
            assert p.has_section(section), "{0} section not defined in configuration file".format(section)

            for option in opts:
                assert p.has_option(section, option), "{0} option not defined in configuration file".format(option)


    def load_folders(self, p):
        self.ct_img_folder = p.get("directories", "ct_images_folder")
        self.img_name = p.get("images", "img_name")
        self.out_folder = p.get("directories", "output_dir")
        self.binary_folder = self.out_folder+"/Binary/"
        self.tiff_folder = self.out_folder+"/tiff/"
        self.mesher_src = p.get("directories", "mesher_src")
        self.LD_LIB_PATH = p.get("directories", "ld_lib_path")


    def check_folders(self, p):
        # input folder
        assert os.path.isdir(self.ct_img_folder), "CT_IMAGES_FOLDER does not exist!"

        # output folders
        if not os.path.isdir(self.out_folder):
            os.mkdir(self.out_folder)

        if not os.path.isdir(self.binary_folder):
            os.mkdir(self.binary_folder)

        if not os.path.isdir(self.tiff_folder):
            os.mkdir(self.tiff_folder)

        # mesher directories
        assert os.path.isdir(self.mesher_src), "MESHER_SRC does not exist!"
        assert os.path.isdir(self.LD_LIB_PATH), "LD_LIB_PATH does not exist!"


    def run_matlab_mesher(self):
        '''
        Return the matlab mesher.
        '''

        sep = '" '
        pre = '"'

        command = "{0}run_main.sh {1} ".format(self.mesher_src, self.LD_LIB_PATH)
        for p in self.mesher_params:
            command += pre+str(p)+sep
        os.system(command)


    def write_ansys_model(self):
        with open("{0}fe_model.txt".format(self.out_folder), 'w') as f:
            f.write("/prep7\n")
            f.write("ET,1,SOLID185\n")
            f.write("MP,EX,1,17000\n")
            f.write("MP,PRXY,1,0.3\n")
            f.write("/nopr\n")
            f.write("/INPUT,'{0}nodedata','txt'\n".format(self.out_folder))
            f.write("/INPUT,'{0}elementdata','txt'\n".format(self.out_folder))
            f.write("/gopr\n")
            f.write("nsel,s,loc,z,0\n")
            f.write("D,all, , , , , ,ALL, , , , ,\n")
            f.write("nsel,s,loc,z,{0}\n".format(self.height))
            f.write("D,all,UZ,{0}\n".format(self.displacement))
            f.write("allsel\n")
            f.write("/Solu\n")
            f.write("Antype,0\n")
            f.write("eqslv,pcg\n")
            f.write("solve\n")
            f.write("SAVE,'{0}','db'\n".format(self.job_name))

            f.write("*CFOPEN,displacements,txt\n")
            f.write("*GET,num_nodes_,NODE,0,COUNT !Get the number of nodes\n")
            f.write("*GET,node_,NODE,0,NUM,MIN !Get label of the first node\n")
            f.write("*DO,i,1,num_nodes_,1\n")
            f.write("  ! Define some parameters\n")
            f.write("  *GET,nx_,NODE,node_,LOC,X\n")
            f.write("  *GET,ny_,NODE,node_,LOC,Y\n")
            f.write("  *GET,nz_,NODE,node_,LOC,Z\n")
            f.write("  ! Write line\n")
            f.write("  *VWRITE,node_,nx_,ny_,nz_\n")
            f.write("  (F8.0,',',E10.3,',',E10.3,',',E10.3)\n")
            f.write("  ! select the next node\n")
            f.write("  *GET,node_,NODE,node_,NXTH\n")
            f.write("*ENDDO\n")
            f.write("*CFCLOSE\n")
            f.write("/exit\n")


    def compute_height_and_displacement(self):
        max_node_z = 0.0
        with open("{0}/nodedata.txt".format(self.out_folder), 'r') as f:
            for line in f:
                z = float(line.strip().split(',')[-1])
                if z > max_node_z:
                    max_node_z = z
        self.height = max_node_z
        self.displacement = self.height*self.perc_displacement/100.0


    def simple_BC(self):
        slices = len(os.listdir(self.binary_folder))
        self.height = slices*float(self.image_resolution)
        self.displacement = self.height*self.perc_displacement/100.0


    def run_ansys_model(self):
        command = "ansys172 -i fe_model.txt -j {1}".format(self.out_folder, self.job_name)
        os.chdir("{0}".format(self.out_folder))
        os.system(command)


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("-c", "--config_file", help=".ini file name", dest="cfg_file")
    args = parser.parse_args()

    mFE = microFE(args.cfg_file)
    mFE.run_matlab_mesher()

    mFE.simple_BC()
    mFE.write_ansys_model()
    mFE.run_ansys_model()
