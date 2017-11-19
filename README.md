# microFE

## Matlab pipeline

In `m_files\` there is the code for generating FE models with cartesian mesh and homogeneous material properties. The original mesher code is in `/m_files/mesher.m`.

The following inputs are required:

- greyscale images (`.tiff`) of the sample; these are in `images/ConvergenceCube/`
- voxel size (`Image_Resolution`);
- threshold for defining bone tissue;

The `m_files/main.m` file executes the mesher.

The script in `m_files/compile.sh` compiles the matlab scripts with the matlab compiler. Compiled files can be run with the matlab runtime environment (available on ARCHER).

## Configuration file

The meshing process requires the definition of a number of paths and variables. These are defined in a `.ini` configuration file

```
[directories]
M_FILES = <folder containing the compiled matlab code>
FILE_FOLDER = <microCT images folder>
BINARY_FOLDER = <folder where to save binary images>
OUT_DIR = <output folder path>
PARAFEM_FILES_DIR = <ParaFEM input files directory>
LD_LIB_PATH = <matlab executable path, usually $LD_LIBRARY_PATH>

[images]
img_names = <microCT images wildcard>

[mesher_parameters]
threshold = <grayscale threshold, default=18500>
Image_Resolution = <voxel size, default=0.00996>
perc_displacement = <percentage z-wise displacement of uppermost nodes>

[job]
name = <job name>

[parafem_parameters]
nip = <number of interpolation points
limit = <number of preconditioned conjugate gradient (PCG) iterations>
tol = <convergence tolerance of PCG>
E = <Young's modulus>
vP = <Poisson's ratio>
nloadstep = <time increment per load step>
jump = <?>
tol2 = <convergence tolerance of the Newton-Raphson scheme>
```

## Usage

```bash
$ python microFE.py -c cfg_file.ini -r mesh
$ python microFE.py -c cfg_file.ini -r convert
```

## Outputs

After executing the mesher, the files needed to generate the FE model are stored as:

- `m_output/elementdata.txt`
- `m_output/nodedata.txt`

where `m_output` folder is specified in the configuration file.

## ARCHER deployment

In `$WORK`, there is a `microFE` folder organised as

```
microFE/
+-- m_files/
|   +-- main
|   +-- run_main.sh
+-- microFE.py
+-- microFE-archer.ini
+-- microFE_job.pbs
+-- images/
|   +-- ConvergenceCube/
|   |   +--- Scan1_****.tif
```

Launch the pipeline as

```bash
$ qsub microFE_job.pbs
```

## ParaFE instructions (from Francesc)

ParaFEM uses several input files to define the geometry, boundary conditions and parameters for the simulation. These are defined in the following files:

# <a name="materials"></a>
- [ ] To assign __personalised material properties__, it would be helpful if you are familiar with the `umat` format in ABAQUS or ANSYS. In brief, you need to provide the stress (Kirchhoff stress) update, separate the strains in case of an elastoplastic materials (elastic from plastic, logarithmic strains), and calculate the tangent operator (derivatives of Kirchhoff stresses vs logarithmic strains).

I chose this format because it can be integrated exactly as in small-strain cases, making the whole procedure a lot easier. An example is in `parafem_inputs/umat_EE_primal_CPPM.f90`. This is an isotropic linear elastic material (Hencky hyperelasticity in large strain) with an eccentric ellipsoid yield surface (it is usable for trabecular bone at the macroscopic level). The constants are defined in the beginning of the code, and are Young's modulus, Poisson's ratio, uniaxial tensile limit, uniaxial compressive limit, zeta defines the shape of the yield surface (it ranges from 0.5 where the surface is a cone, Drucker-Prager, to -1, where it looks like two parallel planes; do not use it with 0.5 as there is no "check for singularity" in this subroutine). The input data to this subroutine are logarithmic strains, and basically any associated operations to calculate stresses should give you Kirchhoff stresses. The first lines until "! Determine if there is yielding" perform the elastic trial stage of a predictor-corrector strategy for elastoplastic materials. If some measure of equivalent stress surpasses the yield limit, then a corrector procedure follows. The plastic return-mapping is performed with a Newton-Raphson coupled with a Line Search, which in this case, gives global convergence, no matter how large is your time step, this will always convergence (which does not mean that the global finite element Newton-Raphson is going to converge as well).

[...]

I imagine that, according to what you are saying, you want to use linear properties for all your materials (marrow, bone...), and that each of them has a different set of linear properties (Young's Modulus and Poisson's ratio). If this is the case, what we could do is just employ a single, linear, umat for all the different materials and change only the two parameters in the umat for each element. I did not implement "element-dependent properties" in the code, but it is super-straightforward to do it (it would take a few hours only).

- [x] XXXX.d, which contains the __geometry of the system__. The first line should read "\*THREE_DIMENSIONAL", followed by "\*NODES", then by the list of nodes. The list of nodes should be written such as "nnod x y z", where "nnod" is the node number, "x" is the x-coordinate, "y" is the y-coordinate and "z" is the z-coordinate. Then "\*ELEMENTS" followed by the list of elements. This list, in the case of linear hexahedra, should be written as "nel 3 8 1 e1 e2 e3 e4 e5 e6 e7 e8 1", where "nel" is the element number, and "e1-e8" is the connectivity of the element. The connectivity of linear hexahedra follows the same convention as ABAQUS (but just in case, please consult the attached example).

- [x] XXXX.bnd, which contains the list of __nodes which contain, at least, one constrained degree-of-freedom__ (DOF). Constrained DOFs are indicated with "1", while unconstrained are indicated with "0". It is important to note that nodes without contrained DOFs should not be listed in this file.

- [x] XXXX.fix, which contains the non-homogeneously contrained DOFs (i.e. __where displacements are prescribed to a non-zero value__) of the system. Each line should read as "nnod ndof val", where "nnod" is the number of node, "ndof" is the number of DOF (1 for x-coordinate, 2 for y-coordinate and 3 for z-coordinate).  If two DOFs of the same node have prescribed displacements, each DOF should be prescribed in a different line and in ascending order.

- [x] XXXX.lds, which contains the __prescribed loads__. Each loaded node should be indicated in a different line such as "nnod lx ly lz", where "nnod" is the node number, "lx" is the load in the x-coordinate, "ly" is the load in the y-coordinate, and "lz" is the load in the z-coordinate.

- [x] XXXX.dat, which contains the __parameters of the simulation__. The first line should read as "nel nnod nres nlnod nfixnod nip", the second line should read as "limit tol e v", the third line should read as "nodpel", the fourth line should read as "nloadstep, jump", and the fifth line should read as "tol2". These stand for, respectively, the number of elements in the mesh, the number of nodes in the mesh, the number of restrained nodes, the number of loaded nodes, the number of integration points, the number of preconditioned conjugate gradient (PCG) iterations, the convergence tolerance of PCG, Young's modulus, Poisson's ratio, the number of nodes per element, the number of load steps, the time increment per load step and the convergence tolerance of the Newton-Raphson scheme. At this moment, even though they need to be included, "e", "v", "nloadstep" and "jump" are place-holders as they are indicated elsewhere.

```
nel  nnod nres nlnod nfixnod nip
4800 5704 1151 184   184     8

limit tol      e (Young) v (Poisson)
1000  0.000001 1.000000  0.330000

nodpel
8

nloadstep jump
1         1

tol2
0.000001
```
