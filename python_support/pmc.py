import argparse
# import meshlab
# import oce_distance
import oce
import mfs
# import csg_pmc
import os
import xml.etree.ElementTree as ET
# from solid import *
import utils
import numpy as np
import gudhi


########################################################################################################################
# This is the main file of the library, and it can be used as a command line tool. It differs from run_pmc.py by only
# focusing on one point, and not being intended to run in parallel to approximate a shape via a cover. It is, however,
# easy to use and very good for testing.
#
# Usage: Type any of
# pmc.py -h
# pmc.py --help
# man pmc.py
# for help on usage
#
# Supports OCC, OpenSCAD, and Meshlab shape, potentially simultaneously
########################################################################################################################

# Finds the volume of the union of spheres of arbitrary radii defined by rad_dict using the sbl library
# https://sbl.inria.fr/doc/index.html.
# Note that this creates multiple files locally, and therefore may need some permissions
def volume(rad_dict):
    out_name = 'temp_spheres'
    with open(out_name + '.txt', 'w') as outfile:
        for key, value in rad_dict.items():
            outfile.writelines(['{0} {1} {2} {3}\n'.format(*key, value)])
    os.system('sbl-vorlume-txt.exe -f {0} -l --exact --boundary-viewer vmd'.format(out_name + '.txt'))  # modify this if necessary to add
    # extra arguments/ call the executable from a different location
    log_file_name = 'sbl-vorlume-txt__surface_volumes.xml'
    tree = ET.parse(log_file_name)
    volume = tree.getroot()[3].text
    area = tree.getroot()[4].text
    return volume, area


# computes the persistence information
# Returns: Betti numbers and persistence intervals for bottleneck distance calculation
def persistence(rad_dict):
    points = list([list(p) for p in rad_dict.keys()])  # convert from tuples to lists
    rips_complex = gudhi.RipsComplex(points=points,
                                     max_edge_length=60.0)
    simplex_tree = rips_complex.create_simplex_tree(max_dimension=3)
    return simplex_tree.betti_numbers(), simplex_tree.persistence_intervals_in_dimension(1)


# Computes the bottleneck distance between two given persistence arrays
def bottleneck(persistence1, persistence2):
    return gudhi.bottleneck_distance(persistence1, persistence2, 0.1)


# Finds the volume centroid of the union of balls defined by rad_dict - requires uniform radii
def centroid(rad_dict):
    x_sum, y_sum, z_sum = 0, 0, 0
    points = rad_dict.keys()
    n = len(points)
    for key in points:
        x_sum += key[0]
        y_sum += key[1]
        z_sum += key[2]
    return x_sum/n, y_sum/n, z_sum/n


# Construct shape here: (see https://github.com/SolidCode/SolidPython)
# def OpenSCAD_setup():
#     # include(filepath)
#     # return make_shape();
#     # return cube(size=[2, 2, 2], center=True)
#     return sphere(1)
#     # return intersection()(cube(size=[2, 2, 2], center=True),
#     #                       rotate(a=[0, 0, 1 / 200])(cube(size=[2, 2, 2], center=True)))
#     # return difference()(cube(size=[2, 2, 2], center=True), translate(v=[1, 1, 0])(cylinder(h=2, r1=10 ** -7, r2=0, center=True)))
#     # return difference()(translate([.05, .05, .05])(cube([.9, .9, .9])), polyhedron(points, faces))
#     # return rotate(a=60)(cube(size=[1, 1, 1], center=False))


# Documentation on how to construct shapes:
# https://www.opencascade.com/doc/occt-6.9.1/refman/html/class_b_rep_builder_a_p_i___make_shape.html
def OCC_setup(name):
    # oce.BRepBuilderAPI.brepbuilderapi.Precision(sys_e)

    ###############################################################################
    # If you would like to build your own custom shape rather than reading a file,
    # do so here.
    ###############################################################################

    ###############################################################################
    # Use this code to read from a file (note that the name should be changed)
    #
    if name == "404":
        return 0
    import OCC.Core.IFSelect as IFSelect
    from OCC.Core import Interface
    from OCC.Core import Precision
    # Precision.precision.Confusion = sys_e
    Interface.Interface_Static.SetIVal("read.precision.mode", 0)
    # Interface.Interface_Static.SetRVal("read.precision.val", sys_e)

    if name.lower().endswith('stp') or name.lower().endswith('step'):
        import OCC.Core.STEPControl as STEPControl

        reader = STEPControl.STEPControl_Reader()
        status = reader.ReadFile(name)
        if status > 1:
            print("Error: could not read {0}, failed with status code {1}, will not perform OCC check".format(
                name, status))
        ok = reader.TransferRoot(1)
    elif name.lower().endswith('igs'):
        import OCC.Core.IGESControl as IGESControl

        reader = IGESControl.IGESControl_Reader()
        status = reader.ReadFile(name)
        reader.TransferRoots()
        reader.PrintTransferInfo(False, 1)
    else:
        print('Error: file format of {0} not recognized, exiting'.format(args.occ.name))
        exit()
    if status == IFSelect.IFSelect_RetDone:  # check status
        failsonly = True
        reader.PrintCheckLoad(failsonly, 1)
        reader.PrintCheckTransfer(failsonly, 1)
        reader.PrintStatsTransfer(5)
        return reader.OneShape()
    else:
        print("Error: could not read {0}, failed with status code {1}, will not perform OCC check".format(
            name, status))
    return None
    ###############################################################################


# Gets OCC System Precision (Precision::Confusion())
def get_OCC_Precision():
    import OCC.Core.Precision as Precision
    return Precision.precision.Confusion()


# Writes shape, in STEP format, to a file called name
def write_STEP(shape, name):
    from OCC.Core import STEPControl
    writer = STEPControl.STEPControl_Writer()
    writer.Transfer(shape, STEPControl.STEPControl_AsIs)
    writer.Write(name)


def occ_Convex_Hull(rad_dict):
    ch = utils.ball_conv_hull(rad_dict)
    faces_ind = np.array(ch.simplices)
    points = np.array(ch.points[ch.vertices])
    faces = points[faces_ind]
    # count = 0
    face_list = oce.TopTools.TopTools_ListOfShape()
    for face in faces:
        # count += 1
        v1 = np.subtract(face[0], face[1])
        v2 = np.subtract(face[2], face[1])
        normal = np.cross(v2, v1)
        normal = np.array(normal, dtype=float)
        index = np.where(normal == 0)
        u_min = min(face, key=lambda x: x[(index + 1) % 3])[(index + 1) % 3]
        v_min = min(face, key=lambda x: x[(index + 2) % 3])[(index + 2) % 3]
        u_max = max(face, key=lambda x: x[(index + 1) % 3])[(index + 1) % 3]
        v_max = max(face, key=lambda x: x[(index + 2) % 3])[(index + 2) % 3]
        p = tuple(np.array(face[0], dtype=float))
        oce_face = oce.BRepBuilderAPI.BRepBuilderAPI_MakeFace(
            oce.gp.gp_Pln(oce.gp.gp_Pnt(*p), oce.gp.gp_Dir(*tuple(normal))),
            u_min, u_max, v_min, v_max).Face()
        face_list.Append(oce_face)
        # curr = BRepPrimAPI.BRepPrimAPI_MakeHalfSpace(oce_face.Face(), gp.gp_Pnt(*tuple(np.add(face[0], normal))))
        # if debug:
        #     solid_fixer = ShapeFix.ShapeFix_Solid(curr.Solid())
        #     print('HalfSpace fixer performance: {0}'.format(solid_fixer.Perform()))
        #     curr = ensure_correct(solid_fixer.Shape())
        # else:
        #     curr = curr.Shape()
        # if count == 1:
        #     poly = curr
        # else:
        #     poly = BRepAlgoAPI.BRepAlgoAPI_Common(poly, curr).Shape()
    builder = oce.BOPAlgo.BOPAlgo_BuilderSolid()
    builder.SetShapes(face_list)
    builder.Perform()
    return builder.Areas().First()
    # if debug:
    #     poly = ensure_correct(poly)
    # return poly


###################################################################################################
# print(occ_Convex_Hull({(0,0,0):1, (0,1,0):1, (1,0,0):1, (1,1,0):1, (0,0,1):1, (0,1,1):1, (1,0,1):1, (1,1,1):1}))
# exit(0)
###################################################################################################
# write_STEP(OCC_setup(.0001, ""), "sphere.stp")
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Perform pmc on some file types.\n Note: OpenSCAD files are not '
                                                 'accepted, please enter the code and modify OpenSCAD_Setup')
    parser.add_argument('-t', '--types', nargs='+', default=['OCC', 'OpenSCAD', 'MeshLab'], type=str,
                        choices=['OCC', 'OpenSCAD', 'MeshLab'], help='The types of files to run on', dest='types')
    parser.add_argument('-p', '--point', nargs=3, type=float, default=[0, 0, 0],
                        help='A list of coordinates in the form x y z that represent the query point',
                        dest='point')
    init_args = parser.parse_known_args()[0]
    parser.add_argument('-sys', '--system', nargs=1, type=float, default=10 ^ -7, dest='sys_e')
    files = parser.add_argument_group('files', 'The optional files to include')
    files.add_argument('-f1', '--occ', nargs='?', type=argparse.FileType('r'), help='The .stl file for OpenCasCade',
                       required='OCC' in init_args.types)
    # files.add_argument('-f2', '--scad', nargs='?', type=argparse.FileType('r'), help='The .scad file for OpenSCAD',
    #                    required='OpenSCAD' in init_args.types)
    files.add_argument('-f3', '--ply', nargs='?', type=argparse.FileType('r'), help='The .ply file for MeshLab',
                       required='MeshLab' in init_args.types)
    epsilons = parser.add_argument_group('epsilons', 'The corresponding epsilon values to use')
    epsilons.add_argument('-e1', '--occ_e', nargs='?', type=float, help='The epsilon value to use for OpenCasCade',
                          required=False, default=10 ** -7)
    epsilons.add_argument('-e2', '--scad_e', nargs='?', type=float, help='The epsilon value to use for OpenSCAD',
                          required=False, default=10 ** -7)
    epsilons.add_argument('-e3', '--ply_e', nargs='?', type=float, help='The epsilon value to use for MeshLab',
                          required=False, default=10 ** -7)
    args = parser.parse_args()
    print(args)
    point = args.point

    if 'OCC' in args.types:
        oce.BRepBuilderAPI.brepbuilderapi.Precision(args.sys_e[0])
        gp_point = oce.gp.gp_Pnt(*tuple(point))
        oce.EPS = args.occ_e  # OCC
        utils.EPS = args.occ_e
        import OCC.IFSelect as IFSelect

        if args.occ.name.lower().endswith('stp') or args.occ.name.lower().endswith('step'):
            import OCC.STEPControl as STEPControl

            reader = STEPControl.STEPControl_Reader()
            status = reader.ReadFile(args.occ.name)
            ok = reader.TransferRoot(1)
        elif args.occ.name.lower().endswith('igs'):
            import OCC.IGESControl as IGESControl

            reader = IGESControl.IGESControl_Reader()
            status = reader.ReadFile(args.occ.name)
            reader.TransferRoots()
            reader.PrintTransferInfo(False, 1)
        else:
            print('Error: file format of {0} not recognized, exiting'.format(args.occ.name))
            exit()
        if status == IFSelect.IFSelect_RetDone:  # check status
            failsonly = True
            reader.PrintCheckLoad(failsonly, 1)
            reader.PrintCheckTransfer(failsonly, 1)
            OCC_obj = reader.OneShape()
            # OCC_obj = OCC_setup(10**-5)
            print('OCC      point membership on point {0} returned {1}'.format(point, oce.is_in(gp_point, OCC_obj)))
            dist, p = oce.dist(gp_point, OCC_obj)
            print('OCC      distance is: {0} and the nearest point is: {1}'.format(dist, p))
            print('Minimum Feature Size is {0}'.format(mfs.mfs(OCC_obj)))
        else:
            print("Error: could not read {0}, failed with status code {1}, will not perform OCC check".format(
                args.occ.name, status))

    # if 'OpenSCAD' in args.types:
    #     csg_pmc.EPS = args.scad_e  # OpenSCAD
    #     utils.EPS = args.scad_e
    #     # OpenSCADObject = scad_parser(args.scad.name)
    #     OpenSCAD_obj = OpenSCAD_setup()
    #     # To get the openSCAD Version of the shape run this:
    #     print('This OpenSCAD module transferred as Start: {0} :End'.format(scad_render(OpenSCAD_obj)))
    #     print('OpenSCAD point membership on point {0} returned {1}'.format(point, csg_pmc.pmc(OpenSCAD_obj, point)))
    #     dist, p = oce_distance.d_p_s(point, OpenSCAD_obj)
    #     print('OpenSCAD distance is: {0} and the nearest point is: {1}'.format(dist, p.Coord()))

    # if 'MeshLab' in args.types:
    #     meshlab.EPS = args.ply_e  # MeshLab (*.ply)
    #     utils.EPS = args.ply_e
    #     inside, ply_distance = meshlab.ply_pmc(args.ply.name, point)
    #     print('MeshLab  point membership on point {0} returned {1}'.format(point, inside))
    #     dist, p = ply_distance
    #     print('MeshLab  distance is: {0} and the nearest point is: {1}'.format(dist, p))
