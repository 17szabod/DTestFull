# import mfs
import pmc
import os
# import meshlab


def occ_configure(alg_tol, model):
    sys_tol = pmc.get_OCC_Precision()
    import Constants
    Constants.OCC_SHAPE = pmc.OCC_setup(model)
    Constants.EPSILON_OF_OCC_SYSTEM = sys_tol
    Constants.USE_OCC = True
    Constants.USE_MESHLAB = False
    Constants.USE_OPENSCAD = False
    Constants.OCC_FILENAME = model
    Constants.SET_PMC_MANUALLY = True
    Constants.PMC_EPSILON = alg_tol
    Constants.CONSTANT_DEFAULT_RADIUS = alg_tol
    Constants.DENSITY = Constants.DENSITY_VALUE
    Constants.SET_BOUNDS_MANUALLY = False
    Constants.x_min, Constants.y_min, Constants.z_min, Constants.x_max, Constants.y_max, Constants.z_max = pmc.oce.aabb(Constants.OCC_SHAPE)
    print("Bounding box: {0}".format(pmc.oce.aabb(Constants.OCC_SHAPE)))
    # Constants.x_min = xmin
    # Constants.y_min = ymin
    # Constants.z_min = zmin
    # Constants.x_max = xmax
    # Constants.y_max = ymax
    # Constants.z_max = zmax
    Constants.x_min -= alg_tol
    Constants.y_min -= alg_tol
    Constants.z_min -= alg_tol
    Constants.x_max += alg_tol
    Constants.y_max += alg_tol
    Constants.z_max += alg_tol
    import run_pmc
    arr1, arr2, arr3, DENSITY, mins, maxs, hs, sys_e, occ = run_pmc.make_cover()
    rad_dict, ins, ons = run_pmc.parse_cover(arr1)
    volume, surface_area = pmc.volume(rad_dict)
    # print(rad_dict)
    return float(surface_area), float(volume), rad_dict, ins


def rhino_configure(sys_tol, alg_tol, point_file):
    rad_dict, ins, ons = read_shared_cover(point_file, alg_tol)
    import run_pmc
    # print(rad_dict)
    volume, surface_area = run_pmc.setup.volume(rad_dict)
    return float(surface_area), float(volume), rad_dict, ins


def sw_configure(alg_tol, model):
    import Constants
    print("Beginning SolidWorks configure with arguments {0} {1} {2}.".format(model, Constants.DENSITY, alg_tol if alg_tol != -1 else ""))
    os.system('\"C:\\Users\\danis\\Coding\\DTestFull\\SolidWorks_support\\ConsoleApplication1\\ConsoleApplication1\\bin\\Debug\\SW_PMC_Grid.exe\" {0} {1} {2}'.format(model, Constants.DENSITY, alg_tol if alg_tol != -1 else ""))
    point_file = "C:\\Users\\danis\\Coding\\DTestFull\\temp_SW_spheres.txt"
    print("Successful point cloud generation from Solidworks!")
    rad_dict, ins, ons = read_shared_cover(point_file, alg_tol)
    import run_pmc
    # print(rad_dict)
    volume, surface_area = run_pmc.setup.volume(rad_dict)
    return float(surface_area), float(volume), rad_dict, ins


def inv_configure(alg_tol, model):
    import Constants
    print("Beginning Inventor configure.")
    os.system('\"C:\\Users\\danis\\Coding\\DTestFull\\Inventor_support\\Inventor_PMC\\Inventor_PMC\\bin\\Debug\\Inventor_PMC.exe\" {0} {1} {2}'.format(model, Constants.DENSITY, alg_tol if alg_tol != -1 else ""))
    point_file = "C:\\Users\\danis\\Coding\\DTestFull\\temp_Inv_spheres.txt"
    rad_dict, ins, ons = read_shared_cover(point_file, alg_tol)
    import run_pmc
    # print(rad_dict)
    volume, surface_area = run_pmc.setup.volume(rad_dict)
    return float(surface_area), float(volume), rad_dict, ins


def read_shared_cover(filename, rad):
    rad_dict = {}
    ins, ons = [], []
    with open(filename, 'r') as infile:
        body = infile.read()
        elements = body.split('~')
        for element in elements:
            [pmc, point] = element.split('$')
            if int(pmc) == 1:
                p = tuple(eval(point))
                rad_dict[p] = rad
                ins.append(p)
            elif int(pmc) == 0:
                p = tuple(eval(point))
                # rad_dict[p] = rad  # Toggle this to have shared files include ON points
                ons.append(p)
    return rad_dict, ins, ons


def occ_configure_direct(model, sys_e):
    pmc.oce.EPS = sys_e
    shape = pmc.OCC_setup(sys_e, model)
    return pmc.oce.vol(shape), pmc.oce.area(shape), pmc.oce.centroid(shape)


# def meshlab_configure_cover(sys_tol, alg_tol, model, xmin, ymin, zmin, xmax, ymax, zmax):
#     import Constants
#     Constants.EPSILON_OF_OCC_SYSTEM = sys_tol
#     Constants.USE_OCC = False
#     Constants.USE_SCAD = False
#     Constants.USE_MESHLAB = True
#     Constants.MESHLAB_FILENAME = model
#     Constants.SET_PMC_MANUALLY = True
#     Constants.PMC_EPSILON = alg_tol
#     Constants.CONSTANT_DEFAULT_RADIUS = alg_tol
#     Constants.DENSITY = Constants.DENSITY_VALUE
#     Constants.SET_BOUNDS_MANUALLY = False
#     Constants.x_min = xmin
#     Constants.y_min = ymin
#     Constants.z_min = zmin
#     Constants.x_max = xmax
#     Constants.y_max = ymax
#     Constants.z_max = zmax
#     import run_pmc
#     arr1, arr2, arr3, DENSITY, mins, maxs, hs, sys_e, ply = run_pmc.make_cover()
#     print(arr3)
#     rad_dict, ins, ons = run_pmc.parse_cover(arr3)
#     # print(rad_dict)
#     volume, surface_area = run_pmc.setup.volume(rad_dict)
#     return float(surface_area), float(volume), rad_dict


def simple_hausdorff(A, B):
    maximum1 = 0
    maximum2 = 0
    for a in A:  # Get all the minimums
        val = min([pmc.utils.d(a, b) for b in B])
        if val > maximum1:
            maximum1 = val
    for b in B:  # Get all the minimums
        val = min([pmc.utils.d(a, b) for a in A])
        if val > maximum2:
            maximum2 = val
    return max(maximum1, maximum2)


# def meshlab_configure_direct(sys_tol, model):
#     meshlab.EPS = sys_tol
#     return meshlab.volume_area(model)


# def scad_configure(sys_tol, alg_tol, model, xmin, ymin, zmin, xmax, ymax, zmax):
#     import Constants
#     Constants.EPSILON_OF_LOCAL_SYSTEM = sys_tol
#     Constants.USE_OCC = False
#     Constants.USE_MESHLAB = False
#     Constants.USE_OPENSCAD = True
#     Constants.SCAD_SHAPE = eval(model)
#     Constants.SET_PMC_MANUALLY = True
#     Constants.PMC_EPSILON = alg_tol
#     Constants.CONSTANT_DEFAULT_RADIUS = alg_tol
#     Constants.DENSITY = Constants.DENSITY_VALUE
#     Constants.x_min = xmin
#     Constants.y_min = ymin
#     Constants.z_min = zmin
#     Constants.x_max = xmax
#     Constants.y_max = ymax
#     Constants.z_max = zmax
#     import run_pmc
#     arr1, arr2, arr3, DENSITY, mins, maxs, hs, sys_e, ply = run_pmc.make_cover()
#     print(arr2)
#     rad_dict, ins, ons = run_pmc.parse_cover(arr2)
#     volume, surface_area = run_pmc.setup.volume(rad_dict)
#     return float(surface_area), float(volume), rad_dict


# ######################Compute M^2######################################
# rad_dict2, ins2, ons = read_shared_cover('data/tube_point_cloud.txt', .3)
#########################################################################

# ######################Compute MFS######################################
# print(pmc.mfs.mfs(shape))
#########################################################################

# ######################Compute M^1######################################
# surface_area, volume, rad_dict1, ins1 = occ_configure(.3, 'tube.stp')
#########################################################################

# ######################Properties of M^1################################
# print('M^1 Volume and Surface Area: {0}, Centroid: {1}'.format(pmc.volume(rad_dict1), pmc.centroid(rad_dict1)))
#########################################################################

# ######################Properties of M^2################################
# print('M^2 Volume and Surface Area: {0}, Centroid: {1}'.format(pmc.volume(rad_dict2), pmc.centroid(rad_dict2)))
#########################################################################

# ######################D_H(M_1, M^2)####################################
# print('D_H(M_1, M^2): ', pmc.mfs.dist_points_shape(ins2, ons, shape, rad_dict2))
#########################################################################

# ######################D_H(M^1, M^2)####################################
# print('D_H(M^1, M^2): ', simple_hausdorff(rad_dict1.keys(), rad_dict2.keys()))
#########################################################################

# ######################Properties of Model##############################
# surface_area, volume, centroid = occ_configure_direct('tube.stp', 1e-5)
# print('Volume: {0}, Surface Area: {1}, Centroid: {2}'.format(surface_area, volume, centroid))
#########################################################################
