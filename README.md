# microFE

(from Sara)

In `m_files\` there is the code for generating FE models with heterogeneous
material properties. It is made of 6 steps (S1-S6) to be run in sequence,
while the other functions are called inside the code.

The following inputs are required:

- greyscale images of the sample
- voxel size
- threshold for defining bone tissue
- threshold for defining bone marrow
- images of the calibration phantom (750 mgHA/cc and 250 mgHA/cc)

Of course the procedure is based on some assumptions. The calibration curve for
converting grey levels into density should be adapted to the scanner. Also, the
law for converting bone density into elastic modulus can be adapted to the
sample/species.
