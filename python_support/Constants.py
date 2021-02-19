import pmc as setup
import oce
# These imports should be improved. Ideally, the constants file should not be importing anything, as it is a risk of
# cyclic imports that waste a lot of time.

# global x_max, y_max, z_max, x_min, y_min, z_min, IS_IT_A_RANGE, RANGE_MIN, RANGE_MAX_PLUS_ONE, DENSITY_VALUE, \
#     EPSILON_OF_OCC_SYSTEM, EPSILON_OF_LOCAL_SYSTEM, SET_PMC_MANUALLY, PMC_EPSILON, USE_OCC, OCC_FILENAME, \
#     OCC_SHAPE, USE_OPENSCAD, SCAD_SHAPE, USE_MESHLAB, MESHLAB_FILENAME, DRAW_PICTURE, IMAGE_FILE_FOLDER, \
#     WRITE_OUTPUT_TO_TXT_FILE, TXT_FILENAME, WRITE_OUTPUT_TO_CSV, CSV_FILENAME, WRITE_STEP_OUTPUT, STEP_FILENAME, \
#     USE_INS_ONLY, AUTO_SET_RADIUS, CONSTANT_DEFAULT_RADIUS
########################################################################################################################
# SETTINGS:
# Bounds may be set manually:
SET_BOUNDS_MANUALLY = False
if SET_BOUNDS_MANUALLY:
    # Manual default bounds:
    x_max, y_max, z_max = 8.34, 8.38, 21.34
    x_min, y_min, z_min = -8.34, -8.38, -3


# Should the program run in parallel?
PARALLEL = False

# Density may be either a range, or a single value:
IS_IT_A_RANGE = False
# If so,
RANGE_MIN, RANGE_MAX_PLUS_ONE = 10, 21
# Otherwise,
DENSITY_VALUE = 14
DENSITY = 10

# System Epsilons:
EPSILON_OF_OCC_SYSTEM = 10 ** -7
EPSILON_OF_LOCAL_SYSTEM = 10 ** -7  # this can be considered sys_e of meshlab and OpenSCAD
# PMC Epsilons:
# PMC Epsilons, for a range of densities, may be set dynamically so each pmc_e~h, where h is the distance between any
# two sample points. Or, it could be set manually.
SET_PMC_MANUALLY = False
PMC_EPSILON = .3

# Shapes:
# OCC:
USE_OCC = True  # Should this run include an OCC Shape?
OCC_FILENAME = "404"
OCC_SHAPE = setup.OCC_setup(OCC_FILENAME)
if not SET_BOUNDS_MANUALLY and OCC_SHAPE != 0:
    # If OCC, can infer bounds (once shape is defined):
    x_min, y_min, z_min, x_max, y_max, z_max = oce.aabb(OCC_SHAPE)
# OpenSCAD:
USE_OPENSCAD = False  # Should this run include an OpenSCAD Shape?
# SCAD_SHAPE = setup.OpenSCAD_setup()
# MeshLab:
USE_MESHLAB = False  # Should this run include a MeshLab Mesh?
MESHLAB_FILENAME = '/home/daniel/CLionProjects/DTest/data/cube.ply'

# Output:
DRAW_PICTURE = False  # Should it use matplotlib to draw output?
IMAGE_FILE_FOLDER = '/data/pics/'
# You may specify a text file to output every point and its result to:
WRITE_OUTPUT_TO_TXT_FILE = True
TXT_FILENAME = 'xbox_big_copy.txt'
# You may specify a CSV file to output minimum information of every density to. This is recommended for any range of
# densities, it outputs the Density, Volume, Area, Hausdorff distance on each line
WRITE_OUTPUT_TO_CSV = True
CSV_FILENAME = 'xbox_self_compare.csv'
# Can output an OCC shape as a STEP File for future use, or visualization
WRITE_STEP_OUTPUT = False
STEP_FILENAME = 'xbox_copy.stp'
# Should the program calculate the Hausdorff distance between the model and the proxy?
FIND_HAUSDORFF = False


# Cover:
USE_INS_ONLY = True  # Only build the cover from points that returned 'in'
# Can choose to dynamically set the radius of each ball to a constant value, or have one global constant radius
AUTO_SET_RADIUS = False
CONSTANT_DEFAULT_RADIUS = .3

# Feel free to ask me any questions!
# Daniel

########################################################################################################################
