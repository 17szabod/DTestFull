# Computes the minimum feature size of a shape
from OCC.Core import TopoDS
from OCC.Core import TopAbs
from OCC.Core import BRepLProp
from OCC.Core import BRepAdaptor
from OCC.Core import Precision
from OCC.Core import GeomAbs
from OCC.Core import Extrema
from OCC.Core import gp
from OCC.Core import Geom
from OCC.Core import Standard
from OCC.Core import BRepPrimAPI
from OCC.Core import BRepAlgoAPI
from OCC.Core import BRepFilletAPI
from OCC.Core import TopExp
from OCC.Core import GeomAdaptor
from OCC.Core import BRepCheck
from sortedcontainers import sortedlist
import sympy # Not actually required, as modules using sympy and mpmath are not functional
import utils
from sympy.utilities.lambdify import implemented_function
from mpmath import *
import multiprocessing

# This is the radius to fillet sharp corners to. With the presence of a sharp corner, mfs will return this value
DEFAULT_MIN_RADIUS = 10 ** -1


# Computes the shape representing the union of spheres
# NOT FULLY FUNCTIONAL
def union_of_spheres(point_set, pmc_e):
    init_obj = None
    spheres = list()
    for point in point_set:
        sphere = BRepPrimAPI.BRepPrimAPI_MakeSphere(gp.gp_Pnt(*point), pmc_e).Shape()
        spheres.append(sphere)
        if len(spheres) == 1:
            init_obj = sphere
        else:
            fuse = BRepAlgoAPI.BRepAlgoAPI_Fuse(init_obj, sphere)
            # fuse.SetFuzzyValue(.0005)
            print('warning: {0}'.format(fuse.WarningStatus()))
            fuse.Build()
            print('error: {0}'.format(fuse.ErrorStatus()))
            if fuse.ErrorStatus() != 0:
                print("SOMETHING WENT REALLY WRONG")
                continue
            exp1 = TopExp.TopExp_Explorer(init_obj, TopAbs.TopAbs_SOLID)
            solid_obj = TopoDS.topods_Solid(exp1.Current())
            if not BRepCheck.BRepCheck_Solid(solid_obj).Status().IsEmpty() and BRepCheck.BRepCheck_Solid(
                    solid_obj).Status().First() != 0:
                print('failure with code: {0}'.format(BRepCheck.BRepCheck_Solid(solid_obj).Status().First()))
                init_obj = sphere
                continue
            exp = TopExp.TopExp_Explorer(init_obj, TopAbs.TopAbs_FACE)
            count = 0
            while exp.More():
                count += 1
                exp.Next()
            print('Number of faces: {0}'.format(count))
            init_obj = fuse.Shape()
    print(init_obj)
    exp2 = TopExp.TopExp_Explorer(init_obj, TopAbs.TopAbs_SOLID)
    return init_obj
    init_obj = TopoDS.topods_Solid(exp2.Current())
    count = 0
    while exp2.More():
        count += 1
        exp2.Next()
    print('Number of objects is {0}, does {1}have more'.format(count, '' if exp2.More() else 'not '))


def hausdorff(A, B, rad_dict, use_a):
    if use_a:
        maximum = 0
        for a in A:  # Get all the minimums
            val = min([sqrt(a.SquareDistance(b)) - rad_dict[b.Coord()] for b in B])
            if val > maximum:
                maximum = val
        return maximum
    else:
        maximum = 0
        for b in B:  # Get all the minimums
            val = min([sqrt(a.SquareDistance(b)) + rad_dict[a.Coord()] for a in A])
            if val > maximum:
                maximum = val
        return maximum


# Computes, in parallel, the Hausdorff distance between two point sets (in O(n/k) time with k cores)
#  @param use_a: use_a := A \subset B
def parallel_hausdorff(A, B, rad_dict, use_a):
    # If A \subset B
    def parallel_min_finder_a(a, B):
        out_queue.put(min([sqrt(a.SquareDistance(b)) - rad_dict[a.Coord()] for b in B]))
        return

    # If B \subset A
    def parallel_min_finder_b(b, A):
        out_queue.put(min([sqrt(a.SquareDistance(b)) + rad_dict[a.Coord()] for a in A]))
        return

    jobs = list()
    out_queue = multiprocessing.Queue()  # a queue to hold the minimums
    if use_a:
        for a in A:  # Get all the minimums in parallel
            p = multiprocessing.Process(target=parallel_min_finder_a, args=(a, B))
            jobs.append(p)
            p.start()
        maximum = 0
        while not out_queue.empty():  # Find the maximum of the minimums
            val = out_queue.get()
            if val > maximum:
                maximum = val
        return maximum
    else:
        for b in B:
            p = multiprocessing.Process(target=parallel_min_finder_b, args=(b, A))
            jobs.append(p)
            p.start()
        maximum = 0
        while not out_queue.empty():
            val = out_queue.get()
            if val > maximum:
                maximum = val
        return maximum


# Computes the Hausdorff distance between the union of spheres defined by rad_dict and the OCC shape
#  @param ins: the test points inside the shape, cannot be null
#  @param ons: the test points on the boundary of the shape, MAY BE NULL if only checking the points strictly inside
def dist_points_shape(ins, ons, shape, rad_dict):
    point_set = ins
    point_set.extend(ons)
    is_subset = len(ons) == 0
    ext_set = list()
    no_rep_checker = sortedlist.SortedList()
    point_set = [gp.gp_Pnt(*tuple(p)) for p in point_set]
    # print('number of in points is {0}'.format(len(point_set)))
    exp = TopExp.TopExp_Explorer(shape, TopAbs.TopAbs_FACE)
    sum = 0
    # For each face, find all extreme points relative to each point in point_set, and add them to ext_set
    while exp.More():
        face = TopoDS.topods_Face(exp.Current())
        surface = BRepAdaptor.BRepAdaptor_Surface(face)
        for p in point_set:
            extps = Extrema.Extrema_ExtPS(p, surface, surface.UResolution(surface.Tolerance()),
                                          surface.VResolution(surface.Tolerance()))
            if not extps.IsDone():
                continue
            sum += extps.NbExt()
            for i in range(extps.NbExt()):
                point = extps.Point(i + 1).Value().Coord()
                no_rep_checker.add(point)
                index = no_rep_checker.bisect_left(point)
                if len(no_rep_checker) > 0 and (
                        (index > 0 and utils.compare(utils.d(no_rep_checker[(index - 1)], point), 0) == 0) or
                        (index < len(no_rep_checker) - 1 and utils.compare(utils.d(no_rep_checker[(index + 1)], point),
                                                                           0) == 0)):
                    del no_rep_checker[index]
        # If there are no extreme points, just add the parametric corners of the shape
        corners = [surface.Value(surface.FirstUParameter(), surface.FirstVParameter()),
                   surface.Value(surface.FirstUParameter(), surface.LastVParameter()),
                   surface.Value(surface.LastUParameter(), surface.FirstVParameter()),
                   surface.Value(surface.LastUParameter(), surface.LastVParameter())]
        for corner in corners:
            corner = corner.Coord()
            no_rep_checker.add(corner)
            index = no_rep_checker.bisect_left(corner)
            if len(no_rep_checker) > 0 and (
                    (index > 0 and utils.compare(utils.d(no_rep_checker[(index - 1)], corner), 0) == 0) or
                    (index < len(no_rep_checker) - 1 and utils.compare(utils.d(no_rep_checker[(index + 1)], corner),
                                                                       0) == 0)):
                del no_rep_checker[index]
        exp.Next()
    for p in no_rep_checker:
        ext_set.append(gp.gp_Pnt(*tuple(p)))
    if is_subset:
        # ext_set.extend(point_set) <-- Technically this would be more correct, but by specifying that point_set is a
        # subset of the shape, we can speed things up by only looking in one direction for Hausdorff Distance
        return hausdorff(ext_set, point_set, rad_dict, is_subset)
    else:
        # ons.extend(ext_set) <-- Similar to above, knowledge that the shape is a subset of the union of balls can speed
        # up computation
        return hausdorff([gp.gp_Pnt(*tuple(p)) for p in ons], ext_set, rad_dict, is_subset)


# Goes through a shape and 'smooths' it by filleting each edge.
# NOTE: This algorithm fails incredibly often. Because of this, on failure, the algorithm only fillets a single edge,
#   which will make the mfs computation still work, as the other algorithm ignores sharp edges, and will only notice the
#   single smooth edge as the minimum
def smooth(shape):
    fillet = BRepFilletAPI.BRepFilletAPI_MakeFillet(shape)
    face_explorer = TopExp.TopExp_Explorer()
    face_explorer.Init(shape, TopAbs.TopAbs_EDGE)
    while face_explorer.More():
        this_edge = face_explorer.Current()
        this_edge = TopoDS.topods_Edge(this_edge)
        fillet.Add(DEFAULT_MIN_RADIUS, this_edge)
        face_explorer.Next()
    if fillet.NbContours() != 0:
        try:
            return fillet.Shape()
        except BaseException:  # Failed to make shape, technically it could be some other exception, can check if needed
            print('failed to make full fillet, only trying one edge')
            fillet2 = BRepFilletAPI.BRepFilletAPI_MakeFillet(shape)
            f_exp = TopExp.TopExp_Explorer()
            f_exp.Init(shape, TopAbs.TopAbs_EDGE)
            fillet2.Add(DEFAULT_MIN_RADIUS, TopoDS.topods_Edge(f_exp.Current()))
            return fillet2.Shape()
    else:
        return shape


# Checks the distance between each pair of faces in O(n^2)
#  @param tol: should be system tolerance, which is the tolerance of the surfaces, but can be set manually
def check_surface_distances(surfaces, curr_mfs, tol):
    big_min_dists = list([curr_mfs])
    for face1 in surfaces:
        surfaces.remove(face1)
        surface1 = BRepAdaptor.BRepAdaptor_Surface(face1)
        min_dists1 = list([curr_mfs])
        for face2 in surfaces:
            surface2 = BRepAdaptor.BRepAdaptor_Surface(face2)
            min_dists2 = list([curr_mfs])
            # Finds all the extreme points between the pair of surfaces
            ext = Extrema.Extrema_ExtSS(surface1, surface2, surface1.FirstUParameter(),
                                        surface1.LastUParameter(), surface1.FirstVParameter(),
                                        surface1.LastVParameter(), surface2.FirstUParameter(),
                                        surface2.LastUParameter(), surface2.FirstVParameter(),
                                        surface2.LastVParameter(), tol, tol)
            p1 = Extrema.Extrema_POnSurf()
            p2 = Extrema.Extrema_POnSurf()
            for i in range(1, ext.NbExt() + 1):
                try:
                    ext.Points(i, p1, p2)
                except BaseException:
                    # If there are no extrema, we try some defaults where we know there would be no extrema
                    # (parallel surfaces), and if even that fails just work on corners
                    if ext.IsParallel():
                        if surface1.GetType() == GeomAbs.GeomAbs_Plane:
                            dist = surface1.Plane().SquareDistance(surface2.Plane())
                        elif surface1.GetType() == GeomAbs.GeomAbs_Sphere:
                            dist = abs(surface1.Sphere().Radius() - surface2.Sphere().Radius()) ** 2
                        else:
                            print('I should add checking for parallel surfaces of type {0}'.format(surface1.GetType()))
                    else:
                        dist = surface1.Value(surface1.FirstUParameter(), surface1.FirstVParameter()).SquareDistance(
                            surface1.Value(surface1.FirstUParameter(), surface1.FirstVParameter()))
                    if dist ** .5 >= tol:  # If it were less, this point would be on an edge, so we should skip it
                        min_dists2.append(dist ** .5)
                    continue
                # Often the point would be at a distance 0 from both surface, because the faces were adjacent and
                # therefore the point was on an edge. To solve this, check whether the point p2 on surface2 is also on
                # surface1.
                # Check if p2 is on surface1
                extPS = Extrema.Extrema_ExtPS(p2.Value(), surface1, surface1.FirstUParameter(),
                                              surface1.LastUParameter(), surface1.FirstVParameter(),
                                              surface1.LastVParameter(), tol, tol)
                if not extPS.IsDone():
                    # If extrema failed, just do corner points
                    PUfVf, PUfVl, PUlVf, PUlVl = gp.gp_Pnt(), gp.gp_Pnt(), gp.gp_Pnt(), gp.gp_Pnt()
                    dist = min(extPS.TrimmedSquareDistances(PUfVf, PUfVl, PUlVf, PUlVl))
                    if dist ** .5 >= tol:
                        min_dists2.append(ext.SquareDistance(i) ** .5)
                    continue
                if extPS.NbExt() == 0:
                    dist = p1.Value().SquareDistance(p2.Value())
                else:
                    dists = list()
                    for j in range(1, extPS.NbExt() + 1):
                        this_d = extPS.SquareDistance(j)
                        dists.append(this_d)
                    dist = min(dists)
                if dist >= tol:
                    min_dists2.append(ext.SquareDistance(i) ** .5)
            min_dists1.append(min(min_dists2))
        big_min_dists.append(min(min_dists1))
    return min(big_min_dists)


# Part of an incomplete attempt to find the minimum feature size in a much more elegant and efficient way, through the
# method described in Musuvathy's dissertation on the MAT of a region bounded by B-Splines.
# The method itself returns a number of variables related to the point at u, v on surface
def get_setup(u, v, surface):
    if type(u) is sympy.Symbol or type(v) is sympy.Symbol:
        return range(0, 14)
    if type(u) is not int and type(u) is not float:
        u = u._value
    if type(v) is not int and type(v) is not float:
        v = v._value
    S_u, S_v, S_u_u, S_v_v, S_u_v = gp.gp_Vec(), gp.gp_Vec(), gp.gp_Vec(), gp.gp_Vec(), gp.gp_Vec()
    surface.D2(u, v, gp.gp_Pnt(), S_u, S_v, S_u_u, S_v_v, S_u_v)
    n = S_u.Crossed(S_v)
    n.Normalize()
    [[E, F], [F, G]] = [[S_u.Dot(S_u), S_u.Dot(S_v)], [S_u.Dot(S_v), S_v.Dot(S_v)]]
    I = sympy.Matrix([[E, F], [F, G]])
    [[L, M], [M, N]] = [[S_u_u.Dot(n), S_u_v.Dot(n)], [S_u_v.Dot(n), S_v_v.Dot(n)]]
    II = sympy.Matrix([[L, M], [M, N]])
    A = float(I.det())
    B = 2 * F * M - G * L - E * N
    C = float(II.det())
    L_hat = L * sympy.sqrt(A)
    M_hat = M * sympy.sqrt(A)
    N_hat = N * sympy.sqrt(A)
    B_hat = B * sympy.sqrt(A)
    C_hat = C * A
    return A, B, C, E, F, G, L, M, N, n, B_hat, C_hat, L_hat, M_hat, N_hat


# Similar to above, this intends to, using sympy, more efficiently find points of maximum and minimum curvature
# NOTE: Not functional
def find_surface_min(surface):
    u, v = sympy.symbols('u,v')

    def A_func(u, v):
        return get_setup(u, v, surface)[0]

    def B_hat_func(u, v):
        return get_setup(u, v, surface)[10]

    def C_hat_func(u, v):
        return get_setup(u, v, surface)[11]

    # g = sympy.Function('g')
    # funcs = {"g": f}
    import autograd
    A_u = autograd.grad(A_func, argnum=0)
    print(A_u(.5, .9))
    A = implemented_function('A', A_func)
    A = sympy.lambdify((u, v), A(u, v))
    A_u = sympy.diff(A_func(u, v), u, evaluate=False)
    A_v = sympy.diff(A(u, v), v, v, evaluate=False)
    B_hat = implemented_function('B_hat', B_hat_func)
    # B_hat = sympy.lambdify((u, v), get_setup(u, v, surface)[10])
    B_hat_u = sympy.diff(B_hat, u, u, evaluate=False)
    B_hat_v = sympy.diff(B_hat, v, v, evaluate=False)
    C_hat = implemented_function('C_hat', C_hat_func)
    # C_hat = sympy.lambdify((u, v), get_setup(u, v, surface)[11])
    C_hat_u = sympy.diff(C_hat, u, u, evaluate=False)
    C_hat_v = sympy.diff(C_hat, v, v, evaluate=False)
    Q = implemented_function('Q', lambda u, v: B_hat(u, v) * B_hat(u, v) - 4 * A(u, v) * C_hat(u, v))
    P_u = implemented_function('P_u', lambda u, v: .5 * (
            -A(u, v) ** (-3 / 2) * B_hat_u(u, v) + (3 / 2) * A(u, v) ** (-5 / 2) * A_u(u, v) * B_hat(u, v)))
    P_v = implemented_function('P_v', lambda u, v: .5 * (
            -A(u, v) ** (-3 / 2) * B_hat_v(u, v) + (3 / 2) * A(u, v) ** (-5 / 2) * A_v(u, v) * B_hat(u, v)))
    R_u = implemented_function('R_u',
                               lambda u, v: .5 * (A(u, v) ** (-3 / 2) * B_hat_u(u, v) * B_hat(u, v) - 2 * A(u, v) **
                                                  (-1 / 2) * C_hat_u(u, v) + 4 * A(u, v) ** (-3 / 2) * A_u(u,
                                                                                                           v) * C_hat(u,
                                                                                                                      v) - (
                                                          3 / 2) * A(u, v) ** (-5 / 2)
                                                  * A_u(u, v) * B_hat(u, v) ** 2))
    R_v = implemented_function('R_v', lambda u, v: .5 * (A(u, v) ** (-3 / 2) * B_hat_v(u, v) * B_hat(u, v) - 2 * A(u, v)
                                                         ** (-1 / 2) * C_hat_v(u, v) + 4 * A(u, v) ** (-3 / 2) * A_v(u,
                                                                                                                     v) * C_hat(
                u, v) - (3 / 2) * A(u, v) **
                                                         (-5 / 2) * A_v(u, v) * B_hat(u, v) ** 2))
    sols = sympy.solve([Q * P_u ** 2 - R_u ** 2, Q * P_v ** 2 - R_v ** 2], u, v)
    return 1 / min(lambda tup: BRepLProp.BRepLProp_SLProps(surface, *tup, 1, 1e-6).MaxCurvature() for tup in sols)


# The main method of the file, finds the minimum feature size of the OCC shape shape
def mfs(shape):
    iterator = TopoDS.TopoDS_Iterator()
    iterator.Initialize(shape)
    glo_max = -1
    surfaces = list()
    while iterator.More():
        shape = iterator.Value()
        # shape = BRepBuilderAPI.BRepBuilderAPI_NurbsConvert(shape).Shape() <-- Potentially convert this surface to a
        # NURBS representation, slowing down calculations and causing potential errors (would not recommend)
        # shape = smooth(shape) <-- Calls the smooth method to fillet every edge, or just one edge if unable to do so
        explorer = TopExp.TopExp_Explorer()
        explorer.Init(shape, TopAbs.TopAbs_FACE)
        while explorer.More():
            this_face = TopoDS.topods_Face(explorer.Current())
            adaptor = BRepAdaptor.BRepAdaptor_Surface(this_face)
            surfaces.append(this_face)
            curvature = 0
            # Occasionally a surface will not have appropriate parametric continuity, in which case the smoothing
            # algorithm could not help. The lines below would cath this, and make the mfs very small
            # print('Surface u continuity is: {0}'.format(adaptor.UContinuity()))
            # print('Surface v continuity is: {0}'.format(adaptor.VContinuity()))
            ###################################################################
            # Should I keep this? It does show up due to imperfections in the other algorithms, but it changes MFS
            # significantly.
            # if adaptor.UContinuity() < GeomAbs.GeomAbs_C1 or adaptor.VContinuity() < GeomAbs.GeomAbs_C1:
            #     curvature = Precision.precision_Infinite()
            ###################################################################

            # Check each default shape, to speed up computations for trivial cases
            if adaptor.GetType() == GeomAbs.GeomAbs_Plane:
                surface = adaptor.Plane()
                curvature = 1 / Precision.precision_Infinite()
            elif adaptor.GetType() == GeomAbs.GeomAbs_Cylinder:
                surface = adaptor.Cylinder()
                curvature = 1 / surface.Radius()
            elif adaptor.GetType() == GeomAbs.GeomAbs_Sphere:
                surface = adaptor.Sphere()
                curvature = 1 / surface.Radius()
            elif adaptor.GetType() == GeomAbs.GeomAbs_Torus:
                surface = adaptor.Torus()
                curvature = max(1 / surface.MajorRadius(), 1 / (surface.MajorRadius() - surface.MinorRadius()),
                                1 / surface.MinorRadius())
            elif adaptor.GetType() == GeomAbs.GeomAbs_BezierSurface or adaptor.GetType() == GeomAbs.GeomAbs_BSplineSurface:
                # Finds the extreme points of curvature on the parameterized surface by finding geometric extrema
                # between the surface and a similarly oriented plane.
                # Note that this may miss some things, depending on how the surface was constructed
                plane = Geom.Geom_Plane(gp.gp_Pln())
                plane.Transform(adaptor.Trsf())
                plane = GeomAdaptor.GeomAdaptor_Surface(Geom.Handle_Geom_Plane(plane))
                ext = Extrema.Extrema_ExtSS(adaptor, plane, adaptor.FirstUParameter(), adaptor.LastUParameter(),
                                            adaptor.FirstVParameter(), adaptor.LastVParameter(),
                                            adaptor.FirstUParameter(), adaptor.LastUParameter(),
                                            adaptor.FirstVParameter(), adaptor.LastVParameter(),
                                            adaptor.Tolerance(), adaptor.Tolerance())
                p1 = Extrema.Extrema_POnSurf()
                p2 = Extrema.Extrema_POnSurf()
                res = min(adaptor.UResolution(Precision.precision_PIntersection()),
                          adaptor.VResolution(Precision.precision_PIntersection()))
                curvatures = list()
                for N in range(1, ext.NbExt() + 1):
                    try:
                        ext.Points(N, p1, p2)
                    except BaseException:
                        curvatures.append(
                            BRepLProp.BRepLProp_SLProps(adaptor, adaptor.FirstUParameter(), adaptor.FirstVParameter(),
                                                        1, res).MaxCurvature())
                        print('something broke, I\'m making curvatures to be {0}'.format(curvatures))
                        continue
                    u = Standard.Standard_Float()
                    v = Standard.Standard_Float()
                    p1.Parameter(u, v)
                    this_curvature = abs(BRepLProp.BRepLProp_SLProps(adaptor, u, v, 1, res).MaxCurvature())
                    curvatures.append(this_curvature)
                if ext.NbExt() == 0:  # On failure, find curvatures at the corners
                    curvatures = [abs(BRepLProp.BRepLProp_SLProps(adaptor, adaptor.FirstUParameter(),
                                                                  adaptor.FirstVParameter(), 1, res).MaxCurvature()),
                                  abs(BRepLProp.BRepLProp_SLProps(adaptor, adaptor.FirstUParameter(),
                                                                  adaptor.LastVParameter(), 1, res).MaxCurvature()),
                                  abs(BRepLProp.BRepLProp_SLProps(adaptor, adaptor.LastUParameter(),
                                                                  adaptor.FirstVParameter(), 1, res).MaxCurvature()),
                                  abs(BRepLProp.BRepLProp_SLProps(adaptor, adaptor.LastUParameter(),
                                                                  adaptor.LastVParameter(), 1, res).MaxCurvature()),
                                  abs(BRepLProp.BRepLProp_SLProps(adaptor, adaptor.FirstUParameter(),
                                                                  adaptor.FirstVParameter(), 1, res).MinCurvature()),
                                  abs(BRepLProp.BRepLProp_SLProps(adaptor, adaptor.FirstUParameter(),
                                                                  adaptor.LastVParameter(), 1, res).MinCurvature()),
                                  abs(BRepLProp.BRepLProp_SLProps(adaptor, adaptor.LastUParameter(),
                                                                  adaptor.FirstVParameter(), 1, res).MinCurvature()),
                                  abs(BRepLProp.BRepLProp_SLProps(adaptor, adaptor.LastUParameter(),
                                                                  adaptor.LastVParameter(), 1, res).MinCurvature()),
                                  ]
                    print('curvatures at the corners are {0}'.format(curvatures))
                curvature = max(curvatures)
            elif adaptor.GetType() == GeomAbs.GeomAbs_Cone:
                # We know the tip isn't included, since the surface has a continuous first derivative
                res = min(adaptor.UResolution(Precision.precision_PIntersection()),
                          adaptor.VResolution(Precision.precision_PIntersection()))
                curvatures = [abs(BRepLProp.BRepLProp_SLProps(adaptor, adaptor.FirstUParameter(),
                                                              adaptor.FirstVParameter(), 1, res).MaxCurvature()),
                              abs(BRepLProp.BRepLProp_SLProps(adaptor, adaptor.FirstUParameter(),
                                                              adaptor.LastVParameter(), 1, res).MaxCurvature()),
                              abs(BRepLProp.BRepLProp_SLProps(adaptor, adaptor.LastUParameter(),
                                                              adaptor.FirstVParameter(), 1, res).MaxCurvature()),
                              abs(BRepLProp.BRepLProp_SLProps(adaptor, adaptor.LastUParameter(),
                                                              adaptor.LastVParameter(), 1, res).MaxCurvature()),
                              abs(BRepLProp.BRepLProp_SLProps(adaptor, adaptor.FirstUParameter(),
                                                              adaptor.FirstVParameter(), 1, res).MinCurvature()),
                              abs(BRepLProp.BRepLProp_SLProps(adaptor, adaptor.FirstUParameter(),
                                                              adaptor.LastVParameter(), 1, res).MinCurvature()),
                              abs(BRepLProp.BRepLProp_SLProps(adaptor, adaptor.LastUParameter(),
                                                              adaptor.FirstVParameter(), 1, res).MinCurvature()),
                              abs(BRepLProp.BRepLProp_SLProps(adaptor, adaptor.LastUParameter(),
                                                              adaptor.LastVParameter(), 1, res).MinCurvature()),
                              ]
                curvature = max(curvatures)
            else:
                print('Unrecognized surface of type {0}'.format(adaptor.GetType()))
                explorer.Next()
                continue
            if curvature > glo_max:
                glo_max = curvature
            explorer.Next()
        iterator.Next()
    return min(1 / glo_max, check_surface_distances(surfaces, 1 / glo_max, 1e-7))
