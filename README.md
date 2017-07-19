# microFE

*(from Sara)*

In `m_files\` there is the code for generating FE models with heterogeneous
material properties. It is made of 6 steps (S1-S6) to be run in sequence,
while the other functions are called inside the code.

The following inputs are required:

- greyscale images (`.tiff`) of the sample; these are in `images/ConvergenceCube/`
- voxel size; defined in `m_files/S2_AnsysMesheStreamout.m`
- threshold for defining bone tissue; defined in `m_files/S1_meshPreparation.m`
- threshold for defining bone marrow; defined in `m_files/S1_meshPreparation.m`
- images of the calibration phantom (750 mgHA/cc and 250 mgHA/cc); stored in `images/Ph250` and `images/Ph750`

Of course the procedure is based on some assumptions. The calibration curve for
converting grey levels into density should be adapted to the scanner. Also, the
law for converting bone density into elastic modulus can be adapted to the
sample/species.

The `m_files/main.m` file executes the six steps in one go.

## Outputs

After executing steps S1 to S6, the following files are generated

- `m_files/boneChangeData.txt`
- `m_files/boneModulusData.txt`
- `m_files/elementdata.txt`
- `m_files/marrowChangeData.txt`
- `m_files/marrowModulusData.txt`
- `m_files/mediumChangeData.txt`
- `m_files/mediumModulusData.txt`
- `m_files/nodedata.txt`

These are used to build the FE model in ANSYS.
