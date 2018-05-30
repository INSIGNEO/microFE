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
        self.image_resolution = float(p.get("mesher_parameters", "image_resolution"))*1e-6
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
            opts = {"out_folder": self.out_folder,
                    "height": self.height,
                    "displacement": self.displacement,
                    "job_name": self.job_name
                    }

            f.write(dedent("""\
            /prep7
            ET,1,SOLID185
            MP,EX,1,17000
            MP,PRXY,1,0.3
            /nopr
            /INPUT,'{out_folder}nodedata','txt'
            /INPUT,'{out_folder}elementdata','txt'
            /gopr
            nsel,s,loc,z,0
            D,all, , , , , ,ALL, , , , ,
            nsel,s,loc,z,{height:15.15f}
            D,all,UZ,{displacement:15.15f}
            allsel

            /Solu
            Antype,0
            eqslv,pcg
            solve
            SAVE,'{job_name}','db'
            /exit,nosave

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


    def compute_height_and_displacement(self):
        max_node_z = 0.0
        with open("{0}/nodedata.txt".format(self.out_folder), 'r') as f:
            for line in f:
                z = float(line.strip().split(',')[-1])
                if z > max_node_z:
                    max_node_z = z
        self.height = max_node_z
        self.displacement = self.height*self.perc_displacement/100.0


    def compute_lenght_width_height(self):
        max_node_x = 0.0
        max_node_y = 0.0
        max_node_z = 0.0

        with open("{0}/nodedata.txt".format(self.out_folder), 'r') as f:
            for line in f:
                x = float(line.strip().split(',')[2])
                y = float(line.strip().split(',')[3])
                z = float(line.strip().split(',')[4])

                if x > max_node_x:
                    max_node_x = x

                if y > max_node_y:
                    max_node_y = y

                if z > max_node_z:
                    max_node_z = z

        self.lenght = max_node_x
        self.width = max_node_y
        self.height = max_node_z


    def compute_displacement(self):
        self.displacement

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
