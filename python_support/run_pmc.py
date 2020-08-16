import numpy as np
import multiprocessing.managers
import time
# import meshlab
import mfs
import utils
# import csg_pmc
from Constants import *


########################################################################################################################
# This is the main program to construct an epsilon cover of a shape in parallel. There are a lot of details, and a lot
# of options may simply be commented out, such as drawing nice output, or using multiple systems side by side.
#
# To run, just compile and run the program after preparing the settings section
########################################################################################################################


def pmc(p, loc, arrs, objs):
    # print('starting point {0}'.format(p))
    [occ, scad, ply] = objs
    # tup = [oce.is_in(oce.gp.gp_Pnt(*tuple(p)), occ) if USE_OCC else 1, csg_pmc.pmc(scad, p) if USE_OPENSCAD else 1,
    #        meshlab.ply_pmc(ply, p, PMC_EPSILON)[0] if USE_MESHLAB else 1]
    tup = [oce.is_in(oce.gp.gp_Pnt(*tuple(p)), occ),1,1]
    arrs[0][loc] = tup[0]
    arrs[1][loc] = tup[1]
    arrs[2][loc] = tup[2]
    return


def make_cover():
    class MyManager(multiprocessing.managers.BaseManager):
        pass

    MyManager.register('np_zeros', np.zeros, multiprocessing.managers.ArrayProxy)
    MyManager.register('init_list', list, multiprocessing.managers.BaseListProxy)

    xh = (x_max - x_min) / DENSITY
    yh = (y_max - y_min) / DENSITY
    zh = (z_max - z_min) / DENSITY
    sys_e = EPSILON_OF_OCC_SYSTEM  # occ_e
    utils.EPS = EPSILON_OF_LOCAL_SYSTEM
    oce.BRepBuilderAPI.brepbuilderapi.Precision(sys_e)
    oce.EPS = PMC_EPSILON  # pmc_e
    # if not SET_PMC_MANUALLY:
    #     PMC_EPSILON = (max(xh, yh, zh) - sys_e) / 2  # pmc_e
    # csg_pmc.EPS = PMC_EPSILON  # scad_e
    # meshlab.EPS = PMC_EPSILON
    # meshlab.EPS = sys_e
    # csg_pmc.EPS = PMC_EPSILON
    occ = OCC_SHAPE
    # scad = SCAD_SHAPE
    # ply = MESHLAB_FILENAME
    # if USE_OCC:
    #     shape_to_return = occ
    # else:
    #     shape_to_return = scad if USE_OPENSCAD else ply
    shape_to_return = occ
    print('xh: {0}, yh: {1}, zh: {2}'.format(xh, yh, zh))
    mins = (x_min, y_min, z_min)
    maxs = (x_max, y_max, z_max)
    hs = (xh, yh, zh)
    if PARALLEL:
        m1 = MyManager()
        m1.start()
        arr1 = m1.np_zeros((DENSITY + 1, DENSITY + 1, DENSITY + 1))
        m2 = MyManager()
        m2.start()
        arr2 = m2.np_zeros((DENSITY + 1, DENSITY + 1, DENSITY + 1))
        m3 = MyManager()
        m3.start()
        arr3 = m3.np_zeros((DENSITY + 1, DENSITY + 1, DENSITY + 1))
        jobs = []
    else:
        arr1 = np.zeros((DENSITY + 1, DENSITY + 1, DENSITY + 1))
        arr2 = np.zeros((DENSITY + 1, DENSITY + 1, DENSITY + 1))
        arr3 = np.zeros((DENSITY + 1, DENSITY + 1, DENSITY + 1))
    # Uncomment this if you want the program to stop if a thread is lasting too long:
    # monitoring_thread = hanging_threads.start_monitoring(seconds_frozen=20)
    count = 0
    for a in range(DENSITY + 1):
        x = x_min + xh * a
        for b in range(DENSITY + 1):
            y = y_min + yh * b
            for c in range(DENSITY + 1):
                z = z_min + zh * c
                if count % 1000 == 0:
                    print('working on {0}'.format((x, y, z)))
                count += 1
                if PARALLEL:
                    # p = multiprocessing.Process(target=pmc, args=(
                    #     [x, y, z], (a, b, c), (arr1, arr2, arr3), [occ, scad, ply]))
                    p = multiprocessing.Process(target=pmc, args=(
                        [x, y, z], (a, b, c), (arr1, arr2, arr3), [occ, 0, 0]))
                    jobs.append(p)
                    p.start()
                else:
                    p = [x, y, z]
                    arrs = (arr1, arr2, arr3)
                    loc = (a, b, c)
                    # tup = [oce.is_in(oce.gp.gp_Pnt(*tuple(p)), occ) if USE_OCC else 1,
                    #        csg_pmc.pmc(scad, p) if USE_OPENSCAD else 1,
                    #        meshlab.ply_pmc(ply, p, PMC_EPSILON)[0] if USE_MESHLAB else 1]
                    tup = [oce.is_in(oce.gp.gp_Pnt(*tuple(p)), occ),1,1]
                    arrs[0][loc] = tup[0]
                    arrs[1][loc] = tup[1]
                    arrs[2][loc] = tup[2]
    if PARALLEL:
        for p in jobs:
            p.join(10)

    if USE_OCC:
        print("I am using OCC")
        arr1 = np.reshape(arr1, (DENSITY + 1, DENSITY + 1, DENSITY + 1))
    if USE_OPENSCAD:
        print("I am using OpenSCAD")
        arr2 = np.reshape(arr2, (DENSITY + 1, DENSITY + 1, DENSITY + 1))
    if USE_MESHLAB:
        print("I am using MESHLAB")
        arr3 = np.reshape(arr3, (DENSITY + 1, DENSITY + 1, DENSITY + 1))
    return arr1, arr2, arr3, DENSITY, mins, maxs, hs, sys_e, shape_to_return


def parse_cover(arr):
    the_point_set = np.array(
        np.meshgrid(np.linspace(x_min, x_max, DENSITY + 1), np.linspace(y_min, y_max, DENSITY + 1),
                    np.linspace(z_min, z_max, DENSITY + 1)))
    the_point_set = [thing.flatten() for thing in the_point_set]
    tps = list()
    for i in range(len(the_point_set[0])):
        tps.append((the_point_set[0][i], the_point_set[1][i], the_point_set[2][i]))
    tps = np.array(tps)
    ins = list(tps[np.where(arr.flatten() == 1)])
    ons = list() if USE_INS_ONLY else list(tps[np.where(arr.flatten() == 0)])
    rad_dict = dict()
    for point in ins:
        rad_dict[tuple(point)] = oce.EPS if AUTO_SET_RADIUS else CONSTANT_DEFAULT_RADIUS  # set radius
    for point in ons:  # CHANGE THIS TO HAVE THE ON POINTS HAVE SMALLER RADII
        rad_dict[tuple(point)] = oce.EPS if AUTO_SET_RADIUS else CONSTANT_DEFAULT_RADIUS  # set radius
    return rad_dict, ins, ons


if __name__ == '__main__':
    for dens in range(RANGE_MIN, RANGE_MAX_PLUS_ONE) if IS_IT_A_RANGE else range(DENSITY_VALUE, DENSITY_VALUE + 1):
        DENSITY = dens

        arr1, arr2, arr3, DENSITY, mins, maxs, hs, sys_e, occ = make_cover()

        if WRITE_OUTPUT_TO_TXT_FILE:
            shared_filename = TXT_FILENAME
            with open(shared_filename, 'w') as outfile:
                for i, val in np.ndenumerate(arr1):
                    ind = tuple(mins[dim] + hs[dim] * i[dim] for dim in [0, 1, 2])
                    outfile.writelines(['{0}${1}~'.format(ind, val)])
        if DRAW_PICTURE:
            # from mpl_toolkits.mplot3d import Axes3D
            import matplotlib.pyplot as plt

            if USE_OPENSCAD and USE_OCC and USE_MESHLAB:
                figsize = (12, 8)
            elif (USE_MESHLAB and USE_OCC) or (USE_OPENSCAD and USE_OCC) or (USE_MESHLAB and USE_OPENSCAD):
                figsize = (8, 8)
            else:
                figsize = (4, 8)
            fig = plt.figure(figsize=figsize)

            colors = ['y', 'r', 'b']
            markers = ['.', '+', 'o']
            if USE_OCC:
                # OCC Top view
                ax1 = fig.add_subplot(121, projection='3d')
                ax1.set_title('OCC')
                xs = [list(), list(), list()]
                ys = [list(), list(), list()]
                zs = [list(), list(), list()]
                for index, val in np.ndenumerate(arr1):
                    if index[0] + 1 <= DENSITY / 2 or index[2] + 1 <= DENSITY / 2 or index[1] + 1 >= DENSITY / 2:
                        xs[int(val) + 1].append(index[0])
                        ys[int(val) + 1].append(index[1])
                        zs[int(val) + 1].append(index[2])
                for i in [0, 1, 2]:
                    ax1.scatter(xs[i], ys[i], zs[i], c=colors[i], marker=markers[i])

                # OCC Bottom view
                arr1 = np.flip(arr1, 0)
                arr1 = np.flip(arr1, 1)
                arr1 = np.flip(arr1, 2)
                ax1 = fig.add_subplot(122, projection='3d')
                xs = [list(), list(), list()]
                ys = [list(), list(), list()]
                zs = [list(), list(), list()]
                for index, val in np.ndenumerate(arr1):
                    if index[0] <= DENSITY / 2 or index[2] <= DENSITY / 2 or index[1] >= DENSITY / 2:
                        xs[int(val) + 1].append(index[0])
                        ys[int(val) + 1].append(index[1])
                        zs[int(val) + 1].append(index[2])
                for i in [0, 1, 2]:
                    ax1.scatter(xs[i], ys[i], zs[i], c=colors[i], marker=markers[i])
            if USE_OPENSCAD:
                # OpenSCAD Top view
                ax2 = fig.add_subplot(222, projection='3d')
                ax2.set_title('OpenSCAD')
                xs = [list(), list(), list()]
                ys = [list(), list(), list()]
                zs = [list(), list(), list()]
                for index, val in np.ndenumerate(arr2):
                    if index[0] <= DENSITY / 2 or index[2] <= DENSITY / 2 or index[1] >= DENSITY / 2:
                        xs[int(val) + 1].append(index[0])
                        ys[int(val) + 1].append(index[1])
                        zs[int(val) + 1].append(index[2])
                for i in [0, 1, 2]:
                    ax2.scatter(xs[i], ys[i], zs[i], c=colors[i], marker=markers[i])

                # # OpenSCAD Bottom view
                arr2 = np.flip(arr2, 0)
                arr2 = np.flip(arr2, 1)
                arr2 = np.flip(arr2, 2)
                ax2 = fig.add_subplot(224, projection='3d')
                xs = [list(), list(), list()]
                ys = [list(), list(), list()]
                zs = [list(), list(), list()]
                for index, val in np.ndenumerate(arr2):
                    if index[0] <= DENSITY / 2 or index[2] <= DENSITY / 2 or index[1] >= DENSITY / 2:
                        xs[int(val) + 1].append(index[0])
                        ys[int(val) + 1].append(index[1])
                        zs[int(val) + 1].append(index[2])
                for i in [0, 1, 2]:
                    ax2.scatter(xs[i], ys[i], zs[i], c=colors[i], marker=markers[i])
            if USE_MESHLAB:
                # PLY Top view
                print(arr3)
                ax3 = fig.add_subplot(323, projection='3d')
                ax3.set_title('PLY')
                xs = [list(), list(), list()]
                ys = [list(), list(), list()]
                zs = [list(), list(), list()]
                for index, val in np.ndenumerate(arr3):
                    if index[0] <= DENSITY / 2 or index[2] <= DENSITY / 2 or index[1] >= DENSITY / 2:
                        xs[int(val) + 1].append(index[0])
                        ys[int(val) + 1].append(index[1])
                        zs[int(val) + 1].append(index[2])
                for i in [0, 1, 2]:
                    ax3.scatter(xs[i], ys[i], zs[i], c=colors[i], marker=markers[i])
                # PLY Bottom view
                arr3 = np.flip(arr3, 0)
                arr3 = np.flip(arr3, 1)
                arr3 = np.flip(arr3, 2)
                ax3 = fig.add_subplot(326, projection='3d')
                xs = [list(), list(), list()]
                ys = [list(), list(), list()]
                zs = [list(), list(), list()]
                for index, val in np.ndenumerate(arr3):
                    if index[0] <= DENSITY / 2 or index[2] <= DENSITY / 2 or index[1] >= DENSITY / 2:
                        xs[int(val) + 1].append(index[0])
                        ys[int(val) + 1].append(index[1])
                        zs[int(val) + 1].append(index[2])
                for i in [0, 1, 2]:
                    ax3.scatter(xs[i], ys[i], zs[i], c=colors[i], marker=markers[i])
            plt.suptitle('PMC precision: {0}, Local system precision: {1} OCC system precision: {2}'
                         .format(oce.EPS, utils.EPS, sys_e), y=.995)
            plt.show()
            fig.savefig(IMAGE_FILE_FOLDER + '{0}.png'.format(time.time()), format='png')

        rad_dict, ins, ons = parse_cover(arr1 if USE_OCC else arr2)

        if WRITE_OUTPUT_TO_CSV:
            with open(CSV_FILENAME, 'a') as outfile:
                if USE_OCC:
                    outfile.writelines([
                        'Density: {0}, Proxy Volume: {1}, Proxy Surface Area: {2}, Proxy Centroid: {3}, True Volume: {4}, True Surface Area: {5}, True Centroid: {6}, {7}\n'
                            .format(dens, *setup.volume(rad_dict), setup.centroid(rad_dict), oce.vol(occ),
                                    oce.area(occ), oce.centroid(occ),
                                    mfs.dist_points_shape(ins, ons if not USE_INS_ONLY else list(), occ,
                                                          rad_dict) if FIND_HAUSDORFF else "")])
                elif USE_OPENSCAD:
                    outfile.writelines(['{0},{1},{2}\n'.format(dens, *setup.volume(rad_dict))])
        if WRITE_STEP_OUTPUT:
            setup.write_STEP(occ, STEP_FILENAME)
    print('''
    ---------------------------
    Finished process full range
    ---------------------------
    ''')
