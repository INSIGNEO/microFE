# microFE

## Matlab pipeline

In `m_files\` there is the code for generating FE models with heterogeneous material properties. It is made of 6 steps (S1-S6) to be run in sequence, while the other functions are called inside the code.

The following inputs are required:

- greyscale images (`.tiff`) of the sample; these are in `images/ConvergenceCube/`
- voxel size; defined in `m_files/S2_AnsysMesheStreamout.m`
- threshold for defining bone tissue; defined in `m_files/S1_meshPreparation.m`
- threshold for defining bone marrow; defined in `m_files/S1_meshPreparation.m`
- images of the calibration phantom (750 mgHA/cc and 250 mgHA/cc); stored in `images/Ph250` and `images/Ph750`

Of course the procedure is based on some assumptions. The calibration curve for converting grey levels into density should be adapted to the scanner. Also, the law for converting bone density into elastic modulus can be adapted to the sample/species.

The `m_files/main.m` file executes the six steps in one go.

## Configuration file

The meshing process requires the definition of a number of paths and variables. These are defined in a `.ini` configuration file

```
[directories]
WORK = <working directory containing the project files>
M_FILES = <folder containing the compiled matlab code>
IMG = <microCT images folder>
CAL1 = <first set of calibration images>
CAL2 = <second set of calibration images>
LD_LIB_PATH = <matlab executable path, usually $LD_LIBRARY_PATH>
OUT_DIR = <output folder path>

[images]
img_names = <microCT images wildcard>
cal_names = <calibration images wildcard>

[mesher_parameters]
nCells = 1
Grey_boneThreshold = 18500
Grey_marrowThreshold = 4500
Image_Resolution = 0.00996

[job]
type = <HPC or WORKSTATION>
name = <job name (HPC only)>
walltime = <required time allocation (HPC only)>
budget_code = <budget code (HPC only)>

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

## Outputs

After executing steps S1 to S6, the following files are generated

- `m_output/boneChangeData.txt`
- `m_output/boneModulusData.txt`
- `m_output/elementdata.txt`
- `m_output/marrowChangeData.txt`
- `m_output/marrowModulusData.txt`
- `m_output/mediumChangeData.txt`
- `m_output/mediumModulusData.txt`
- `m_output/nodedata.txt`

These are used to build the FE model.

## ARCHER deployment

In `$WORK`, there is a `microFE` folder organised as

```bash
microFE/
|-- m_files/
|   |-- main
|   |-- run_main.sh
|-- microFE.py
|-- microFE.ini
|-- images/
|   |-- ConvergenceCube/
|   |   |--- Scan_****.tif
|   |-- Ph250/
|   |   |--- Ph****.tif
|   |-- Ph750/
|   |   |--- Ph****.tif

```

Launch the pipeline as

```bash
python microFE.py microFE.ini
```

where `microFE.ini` is a configuration file.

## ParaFE instructions from Francesc

ParaFEM uses several input files to define the geometry, boundary conditions and parameters for the simulation. These are defined in the following files:

- XXXX.bnd, which contains the list of nodes which contain, at least, one constrained degree-of-freedom (DOF). Constrained DOFs are indicated with "1", while unconstrained are indicated with "0". It is important to note that nodes without contrained DOFs should not be listed in this file.

- XXXX.d, which contains the geometry of the system. The first line should read "\*THREE_DIMENSIONAL", followed by "\*NODES", then by the list of nodes. The list of nodes should be written such as "nnod x y z", where "nnod" is the node number, "x" is the x-coordinate, "y" is the y-coordinate and "z" is the z-coordinate. Then "\*ELEMENTS" followed by the list of elements. This list, in the case of linear hexahedra, should be written as "nel 3 8 1 e1 e2 e3 e4 e5 e6 e7 e8 1", where "nel" is the element number, and "e1-e8" is the connectivity of the element. The connectivity of linear hexahedra follows the same convention as ABAQUS (but just in case, please consult the attached example).

- XXXX.dat, which contains the parameters of the simulation. The first line should read as "nel nnod nres nlnod nfixnod nip", the second line should read as "limit tol e v", the third line should read as "nodpel", the fourth line should read as "nloadstep, jump", and the fifth line should read as "tol2". These stand for, respectively, the number of elements in the mesh, the number of nodes in the mesh, the number of restrained nodes, the number of loaded nodes, the number of integration points, the number of preconditioned conjugate gradient (PCG) iterations, the convergence tolerance of PCG, Young's modulus, Poisson's ratio, the number of nodes per element, the number of load steps, the time increment per load step and the convergence tolerance of the Newton-Raphson scheme. At this moment, even though they need to be included, "e", "v", "nloadstep" and "jump" are place-holders as they are indicated elsewhere.

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

- XXXX.fix, which contains the non-homogeneously contrained DOFs (i.e. where displacements are prescribed to a non-zero value) of the system. Each line should read as "nnod ndof val", where "nnod" is the number of node, "ndof" is the number of DOF (1 for x-coordinate, 2 for y-coordinate and 3 for z-coordinate).  If two DOFs of the same node have prescribed displacements, each DOF should be prescribed in a different line and in ascending order.

- XXXX.lds, which contains the prescribed loads. Each loaded node should be indicated in a different line such as "nnod lx ly lz", where "nnod" is the node number, "lx" is the load in the x-coordinate, "ly" is the load in the y-coordinate, and "lz" is the load in the z-coordinate.

- To assign personalised material properties, it would be helpful if you are familiar with the `umat` format in ABAQUS or ANSYS. In brief, you need to provide the stress (Kirchhoff stress) update, separate the strains in case of an elastoplastic materials (elastic from plastic, logarithmic strains), and calculate the tangent operator (derivatives of Kirchhoff stresses vs logarithmic strains). I chose this format because it can be integrated exactly as in small-strain cases, making the whole procedure a lot easier. An example is attached. This is an isotropic linear elastic material (Hencky hyperelasticity in large strain) with an eccentric ellipsoid yield surface (it is usable for trabecular bone at the macroscopic level). The constants are defined in the beginning of the code, and are Young's modulus, Poisson's ratio, uniaxial tensile limit, uniaxial compressive limit, zeta defines the shape of the yield surface (it ranges from 0.5 where the surface is a cone, Drucker-Prager, to -1, where it looks like two parallel planes; do not use it with 0.5 as there is no "check for singularity" in this subroutine). The input data to this subroutine are logarithmic strains, and basically any associated operations to calculate stresses should give you Kirchhoff stresses. The first lines until "! Determine if there is yielding" perform the elastic trial stage of a predictor-corrector strategy for elastoplastic materials. If some measure of equivalent stress surpasses the yield limit, then a corrector procedure follows. The plastic return-mapping is performed with a Newton-Raphson coupled with a Line Search, which in this case, gives global convergence, no matter how large is your time step, this will always convergence (which does not mean that the global finite element Newton-Raphson is going to converge as well).
