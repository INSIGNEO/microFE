# microFE

[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)

This code builds a homogeneous cartesian mesh from microCT images.

## Matlab mesher

In `m_files\` there is the code for generating FE models with cartesian mesh and homogeneous material properties. The original mesher code is in `/m_files/mesher.m`.

The following inputs are required:

- greyscale images (`.tiff` format);
- voxel size (`Image_Resolution`);
- threshold for defining bone tissue;

The `m_files/main.m` file executes the mesher.

The script in `m_files/compile.sh` compiles the matlab scripts with the matlab compiler. Compiled files can be run with the matlab runtime environment.

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
threshold = <bone tissue threshold in uCT images, e.g., 18500>
Image_Resolution = <voxel size in uCT images, e.g., 0.00996>
perc_displacement = <percentage displacemente along z-axis for uppermost nodes>

[job]
name = <job name>

[parafem_parameters]
nip = <number of interpolation points
limit = <number of preconditioned conjugate gradient (PCG) iterations>
tol = <convergence tolerance of PCG>
E = <Young's modulus>
vP = <Poisson's ratio>
nloadstep = <time increment per load step>
jump = <saving step>
tol2 = <convergence tolerance of the Newton-Raphson scheme>
```

## Usage

On \*nix compile matlab code (may require `chmod`) as

```bash
$ ./compile.sh
```

Run the mesher as
```bash
$ python microFE.py -c cfg_file.ini -r mesh
```

and convert to ParaFEM format with

```bash
$ python microFE.py -c cfg_file.ini -r convert
```

## Outputs

After executing the mesher, the files needed to generate the FE model are stored as:

- `OUT_DIR/elementdata.txt`
- `OUT_DIR/nodedata.txt`

where `OUT_DIR/` folder is specified in the configuration file.

The converted mesh files are in `PARAFEM_FILES_DIR/` which is defined in the configuration file as well.

## On ARCHER

A batch script to run the microFE model on ARCHER is provided, `microFE_batch_job.pbs`. This is launched as

```bash
$ qsub microFE_job.pbs
```

## ParaFEM xx15 program inputs

ParaFEM uses several input files to define the geometry, boundary conditions and parameters for the simulation. These are defined in the following files:

- `XXXX.d` contains the __geometry of the system__. The first line should read "\*THREE_DIMENSIONAL", followed by "\*NODES", then by the list of nodes. The list of nodes should be written such as "nnod x y z", where "nnod" is the node number, "x" is the x-coordinate, "y" is the y-coordinate and "z" is the z-coordinate. Then "\*ELEMENTS" followed by the list of elements. This list, in the case of linear hexahedra, should be written as "nel 3 8 1 e1 e2 e3 e4 e5 e6 e7 e8 1", where "nel" is the element number, and "e1-e8" is the connectivity of the element. The connectivity of linear hexahedra follows the same convention as ABAQUS (see [Hex8 element p.11-4](http://www.colorado.edu/engineering/CAS/courses.d/AFEM.d/AFEM.Ch11.d/AFEM.Ch11.pdf).)

- `XXXX.bnd`, contains the list of __nodes which contain, at least, one constrained degree-of-freedom__ (DOF). Constrained DOFs are indicated with "1", while unconstrained are indicated with "0". It is important to note that nodes without contrained DOFs should not be listed in this file.

- `XXXX.fix`, which contains the non-homogeneously contrained DOFs (i.e. __where displacements are prescribed to a non-zero value__) of the system. Each line should read as "nnod ndof val", where "nnod" is the number of node, "ndof" is the number of DOF (1 for x-coordinate, 2 for y-coordinate and 3 for z-coordinate). If two DOFs of the same node have prescribed displacements, each DOF should be prescribed in a different line and in ascending order.

- `XXXX.lds`, which contains the __prescribed loads__. Each loaded node should be indicated in a different line such as "nnod lx ly lz", where "nnod" is the node number, "lx" is the load in the x-coordinate, "ly" is the load in the y-coordinate, and "lz" is the load in the z-coordinate.

- `XXXX.dat`, which contains the __parameters of the simulation__. The first line should read as "nel nnod nres nlnod nfixnod nip", the second line should read as "limit tol e v", the third line should read as "nodpel", the fourth line should read as "nloadstep, jump", and the fifth line should read as "tol2". These stand for, respectively, the number of elements in the mesh, the number of nodes in the mesh, the number of restrained nodes, the number of loaded nodes, the number of integration points, the number of preconditioned conjugate gradient (PCG) iterations, the convergence tolerance of PCG, Young's modulus, Poisson's ratio, the number of nodes per element, the number of load steps, the time increment per load step and the convergence tolerance of the Newton-Raphson scheme. At this moment, even though they need to be included, "e", "v", "nloadstep" and "jump" are place-holders as they are indicated elsewhere.


## Citation

The Matlab code was developed by Y. Chen as part of his PhD project:

- _Chen Y, Pani M, Taddei F, Mazzà C, Li X, Viceconti M. [Large-scale finite element analysis of human cancellous bone tissue micro computer tomography data: a convergence study](http://biomechanical.asmedigitalcollection.asme.org/article.aspx?articleid=1892759). Journal of biomechanical engineering. 2014 Oct 1;136(10):101013._

- _Chen Y, Dall E, Sales E, Manda K, Wallace R, Pankaj P, Viceconti M. [Micro-CT based finite element models of cancellous bone predict accurately displacement once the boundary condition is well replicated: A validation study](http://www.sciencedirect.com/science/article/pii/S1751616116303204). Journal of the mechanical behavior of biomedical materials. 2017 Jan 31;65:644-51._

Program `xx15` for finite strain elasto-plastic analysis with Newton-Raphson was developed in [ParaFEM](http://parafem.org.uk/about/history) by F. Levrero-Florencio as part of his PhD project:

- _Levrero-Florencio F, Manda K, Margetts L, Pankaj P. [Effect of including damage at the tissue level in the nonlinear homogenisation of trabecular bone](https://link.springer.com/article/10.1007/s10237-017-0913-7). Biomechanics and Modeling in Mechanobiology. 2017 May 12:1-5._
