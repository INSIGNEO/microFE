#!/bin/bash
#$ -M email@sheffield.ac.uk
#$ -m bea
#$ -l h_rt=24:00:00
#$ -l rmem=32G
#$ -N microFE

module load apps/matlab/2016a/binary
module load apps/ansys/17.2
module load apps/python/conda
source activate mFE

python microFE.py -c microFE.ini
