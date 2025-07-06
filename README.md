# DTestFull

## Installation
### Required Packages:

pip packages: numpy, scipy, sympy, argparse, sortedcontainers

Conda packages: pythonocc (https://github.com/tpaviot/pythonocc-core)

External Libraries: Structural Bioinformatics Library (https://sbl.inria.fr/)

### To install:

1. Checkout from git
2. Create virtual Conda environment:
  
   - `conda create --name py37 python=3.7`
   - `conda activate py37`
  
3. Install required python packages into Conda environment

   - `pip install numpy scipy sympy argparse sortedcontainers`
   <!-- - `conda install -c dlr-sc pythonocc-core=7.4.0`  -->

4. Get pythonocc-core via the following conda installer:

   - `conda install conda-forge::pythonocc-core=7.4.0` 
   
5. Change paths in CMakeLists.txt and DTest.c to your venv's python installation

   - You will need to link to the Python library and executables, as well as adding these directories to the search path.
   - In CMakeLists.txt:<br>
   ![alt text](Examples/readme_screenshots/screenshot_cmake.png)
   - In DTest.c:
   ![alt text](Examples/readme_screenshots/screenshot_dtest.png)
   - In DTest.c:
   ![If you do not have a separate OCC installation, there is no need to include that](Examples/readme_screenshots/image-4.png)
   - Add the location of python37.dll (in anaconda3/envs/py37) to your system path. You may need to restart your shell afterwards for the changes to take effect!
   - If it still fails to load required DLLs after running import gp, you may need to copy them manually from {\$conda_root}/envs/py37/Library/bin into {\$conda_root}/envs/py37/Lib/site-packages/OCC/Core.

6. On Windows, POSIX compatible C compiler is needed. One such compiler is MinGW on MSYS2.

7. For Solidworks and Inventor compatibility you will also need a installation of these two, and compile the executables corresponding to each. 
They are stored as Visual Studio solutions in Inventor_PMC and Solidworks_PMC, and also contain hardcoded paths that will need to be updated. First, there is one in py_interface.py:
![alt text](Examples/readme_screenshots/image-2.png)
Then there is one for Inventor in Program.cs:
![alt text](Examples/readme_screenshots/image-1.png)
And one for SolidWorks in Console_PMC.cs:
![alt text](Examples/readme_screenshots/image-3.png)
The filename here is where the PMQ output is stored, and should match the names in py_interface.py.
Certain aspects of this code have not been optimized yet, for example there are recently introduced policies on how to link Python to C, or ways to streamline the connection to Solidworks and Inventor.

1. To install SBL, a UNIX OS is currently required. This makes installation on Windows difficult, but can be worked around either by setting up a remote connection to a UNIX compatible machine, or setting up a local VM that can run SBL. In either case, changes will need to be made to pmc.volume to be able to access whatever sbl installation you use. For the ssh solution, enter the details in the volume method of python_support/pmc.py:
   ![alt text](Examples/readme_screenshots/image.png)

### Example usage

Once installed, we need simply need to run DTest.exe. Usage:
`./DTest <System1> <System2> <Model1> <Model2> <TestName> <Cover Parameter> <Algorithm Precision>`
For systems, use Rhino = 0, OpenCascade = 1, OpenSCAD = 2, MeshLab = 3, SolidWorks = 4, Inventor = 5 (Rhino, OpenSCAD and MeshLab are WIPs for Windows), and algorithm precision should be in mm. The cover parameter is allowed to be entered manually, but a first run with whatever cover parameter will give a suggestion as to what cover parameter to use for the model.
### Stanford Bunny Test

## References

https://arxiv.org/abs/2001.10585

https://doi.org/10.1016/j.cad.2019.05.004
