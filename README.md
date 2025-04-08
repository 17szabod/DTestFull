# DTestFull
### Description:
DTest is an algorithmic framework to test for the interoperability of two distinct CAD systems based on the interchangeability of their models with respect to a specified shape comparison criterion. It allows for indirect comparisons of models via their abstract proxies and the interpretation of models via queries. 

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
5. Install the CAD software (e.g. OpenCascade) with all of its dependencies. 


## Usage

There are two levels of automation available. Some CAD software, such as Rhino, needs the template file (which contains the query outputs, among other things) to be generated within the software itself- this may be automated within the given system itself. The other systems, such as OpenCASCADE, Inventor, Solidworks, and OpenSCAD, can be run directly in an automated sense, but this is only available in the WindowsVersion branch. 

The main executable is DTest.c. After compilation, use the following command to run the semiautomated version:

`Usage: ./DTest <TemplateFile1> <TemplateFile2> <TestName> <Tolerance>`

For the automated version, compile from branch WindowsVersion, and run DTest as follows:

`Usage: ./DTest <System1> <System2> <Model1> <Model2> <TestName> <Cover Parameter> <Algorithm Precision>`

Here System1 and System2 are expected as integers according to `Rhino = 0, OpenCasCade = 1, OpenSCAD = 2, MeshLab = 3, SolidWorks = 4, Inventor = 5`, Model1 and Model2 are the filenames of the two models, TestName is the name of the output file that will be created, Cover Parameter is the radius required when computing the union of balls, and Algorithm Precision is the global precision for any computations DTest makes.

## References

https://arxiv.org/abs/2001.10585

https://doi.org/10.1016/j.cad.2019.05.004
