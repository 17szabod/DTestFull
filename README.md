# DTestFull

## Installation
### Required Packages:

pip packages: numpy, scipy, sympy, xml, argparse, multiprocessing, gudhi

Conda packages: pythonocc (https://github.com/tpaviot/pythonocc-core)- *pythonocc is only available as a conda package, and requires an opencascade installation*

External Libraries: Structural Bioinformatics Library (https://sbl.inria.fr/)- *As of 09-24-22, SBL is only available on unix systems*

### To install:

1. Checkout from git
2. Create virtual Conda environment:
  
   - `conda create --name py37 python=3.7`
   - `conda activate py37`
  
3. Install required packages into Conda environment

   - `pip install numpy scipy sympy argparse gudhi`
   - `conda install -c conda-forge pythonocc-core=7.6.2`
   
4. Change paths in CMakeLists.txt and DTest.c to your venv's python installation


## References

https://arxiv.org/abs/2001.10585

https://doi.org/10.1016/j.cad.2019.05.004
