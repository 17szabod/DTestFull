from OCC.Core import gp
from OCC.Core import Precision
from OCC.Core import TopTools
from OCC.Core import GeomAbs
from OCC.Core import BOPAlgo
# from OCC.Core import BOPCol
from OCC.Core import Bnd
from OCC.Core import BRepBuilderAPI
from OCC.Core import BRepAlgoAPI
from OCC.Core import BRepExtrema
from OCC.Core import BRepPrimAPI
from OCC.Core import BRepOffsetAPI
from OCC.Core import TopExp
from OCC.Core import BRep
from OCC.Core import BRepBndLib
from OCC.Core import TopAbs
from OCC.Core import TopoDS
from OCC.Core import Extrema
from OCC.Core import BRepAdaptor
from OCC.Core import BRepClass3d
from OCC.Core import BRepGProp
from OCC.Core import GProp
import sys
# import oce_distance

global SYS_EPS
global EPS   # PMC epsilon
# EPS = Precision.precision_Confusion() * 4  # 4*10e-7

'''
A Few Notes on Precision:
First of all, everything is an approximation. oce uses either a form of Gradient Descent (default) or an AABB Tree
structure to compute Extrema, and then computes the distance between the two extrema. The default precisions used in OCC
can be found here: https://www.opencascade.com/doc/occt-6.9.1/refman/html/class_precision.html
'''


# Returns the distance between a point and the OCC shape, negative if inside
def dist(point, shape):
    # if oce_distance.debug:
    #     shape = oce_distance.ensure_correct(shape)
    vertex = BRepBuilderAPI.BRepBuilderAPI_MakeVertex(point)
    dist_s_s = BRepExtrema.BRepExtrema_DistShapeShape(shape, vertex.Shape())
    if is_in(point, shape) == 1:
        '''
        The scale is entirely arbitrary, it has to be greater than 1, but we want it to be as small as possible-- 
        unfortunately this function is very susceptible to faults with more complex shapes, 
        because of self intersections that may occur.
        '''
        INF = Precision.precision_Infinite()
        exp = TopExp.TopExp_Explorer(shape, TopAbs.TopAbs_FACE)
        min = INF
        point_to_ret = None
        while exp.More():
            face = TopoDS.topods_Face(exp.Current())
            surface = BRepAdaptor.BRepAdaptor_Surface(face)
            distance = Extrema.Extrema_ExtPS(point, surface, surface.UResolution(surface.Tolerance()),
                                             surface.VResolution(surface.Tolerance()), Extrema.Extrema_ExtFlag_MIN)
            if distance.IsDone():
                for i in range(distance.NbExt()):
                    if distance.SquareDistance(i) < min:
                        min = distance.SquareDistance()
                        point_to_ret = distance.Point(i).Value().Coord()
            corners = [surface.Value(surface.FirstUParameter(), surface.FirstVParameter()),
                       surface.Value(surface.FirstUParameter(), surface.LastVParameter()),
                       surface.Value(surface.LastUParameter(), surface.FirstVParameter()),
                       surface.Value(surface.LastUParameter(), surface.LastVParameter()),
                       ]
            for corner in corners:
                dist = corner.SquareDistance(point)
                if dist < min:
                    min = dist
                    point_to_ret = corner.Coord()
            exp.Next()
        return -min ** .5, point_to_ret
    else:
        return dist_s_s.Value(), dist_s_s.PointOnShape1(1).Coord()


# Returns whether point is in shape (-1 out, 0 on, 1 in)
def is_in(point, shape):
    explorer = BRepClass3d.BRepClass3d_SolidExplorer(shape)
    classifier = BRepClass3d.BRepClass3d_SClassifier(explorer, point, EPS)
    return -(classifier.State() % 2) if classifier.State() != 0 else 1  # switch from enum to my format


# Returns the volume of an OCC shape
def vol(shape):
    global_props = GProp.GProp_GProps()
    BRepGProp.brepgprop_VolumeProperties(shape, global_props)
    return global_props.Mass()


def centroid(shape):
    global_props = GProp.GProp_GProps()
    BRepGProp.brepgprop_VolumeProperties(shape, global_props)
    return global_props.CentreOfMass().Coord()


# Returns the area of an OCC shape
def area(shape):
    global_props = GProp.GProp_GProps()
    BRepGProp.brepgprop_SurfaceProperties(shape, global_props)
    return global_props.Mass()


# Returns the coordinates of the bounding box in the form xmin, ymin, zmin, xmax, ymax, zmax
def aabb(shape):
    B = Bnd.Bnd_Box()
    BRepBndLib.brepbndlib_Add(shape, B)
    top_corner = tuple(B.CornerMax().Coord())
    bottom_corner = tuple(B.CornerMin().Coord())
    return bottom_corner[0], bottom_corner[1], bottom_corner[2], top_corner[0], top_corner[1], top_corner[2]
