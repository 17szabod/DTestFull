import sys
import numpy as np
import numpy.linalg as la
import sympy
from scipy.spatial.qhull import Voronoi, Delaunay, ConvexHull, QhullError

# import tess
# from tess import Container

########################################################################################################################
# This is a generic utilities file, most other programs reference it, and it implements some of the elementary
# algorithms. What it lacks in speed it makes up for in robustness, and breadth. There is a LOT of good code here, but
# much of it is unfinished. I strongly recommend any further files to reference this as well, as it implements so many
# useful algorithms
#
# Whenever finding the distance between two points or comparing two numbers, it is a good idea to use the d and compare
# methods, respectively, as this will make life easier in the future, if you ever want to change the definition of
# distance.
#
# @author: Daniel Szabo
########################################################################################################################

# A local system epsilon. Be sure to set this in whatever is calling utils!
global EPS


# distance between point a and b in the L^2 norm
def d(a, b):
    return la.norm(np.subtract(b, a))


# Returns 1 if x > y, 0 if x = y, -1 if x < y with precision checking
def compare(x, y):
    if x - y > EPS:
        return 1
    elif abs(x - y) <= EPS:
        return 0
    else:
        return -1


# computes whether p is on the left of v1
def on_left(p, line):
    v1 = np.subtract(p, line[0])
    v2 = np.subtract(line[1], line[0])
    if len(p) == 2:
        area = np.cross(v1, v2)
    else:
        area = la.det([[1, 1, 1], v1, v2])
    return compare(area, 0)


# computes the signed are of a triangle (very similar to above,just accepts a different kind of input, and returns area)
def signed_tri_area(tri):
    v1 = np.subtract(tri[0], tri[1])
    v2 = np.subtract(tri[0], tri[2])
    if len(tri[0]) == 2:
        area = np.cross(v1, v2)
    else:
        area = la.norm(np.cross(v1, v2))
        # area = la.det([v1, v2, [1, 1, 1]])
    return area / 2


# An unused method to add a point to a list, without repetitions. Avoids repetitions by inefficiently checking every
# other element
def add_to_set(to_add, col, prec):
    if type(to_add) is not list and type(to_add) is not np.ndarray and type(to_add) is not tuple:
        contains = False
        for point in col:
            if to_add.IsEqual(point, prec):
                contains = True
                break
        if not contains:
            col.append(to_add)
        return col
    else:
        contains = False
        for point in col:
            if compare(d(to_add, point), 0) == 0:
                contains = True
                break
        if not contains:
            try:
                col.append(to_add)
            except AttributeError:
                col = np.append(col, to_add, axis=0)
        return col


# Returns whether p is above the clockwise oriented planar face (ie sign(p,Face)).
# This method is used primarily by pmc for polyhedra
def is_above(face, p):
    m = [[face[0][0], face[0][1], face[0][2], 1],
         [face[1][0], face[1][1], face[1][2], 1],
         [face[2][0], face[2][1], face[2][2], 1],
         [p[0], p[1], p[2], 1]]
    # Need only check 3 points if all are planar
    val = la.det(m)
    if compare(val, 0) == 0:
        return 0
    return 1 if la.det(m) < 0 else -1


# distance between a point and a 2D line segment
def d_p_l(p, line):
    if len(p) == 2:
        v = np.subtract(line[1], line[0])
        if compare(la.norm(v), 0) == 0:  # Line is a point
            return la.norm(np.subtract(line[0], p))
        if 0 <= np.dot(v, np.subtract(p, line[0])) / la.norm(v) ** 2 <= 1:
            a = la.det([
                [line[0][0], line[0][1], 1],
                [line[1][0], line[1][1], 1],
                [p[0], p[1], 1]
            ])
            return abs(a / la.norm(np.subtract(line[1], line[0])))
        else:
            return min(d(line[0], p), d(line[1], p))
    else:
        v = np.subtract(line[1], line[0])
        if 0 <= np.dot(v, np.subtract(p, line[0])) / la.norm(v) ** 2 <= 1:
            a = la.norm(np.cross(np.subtract(line[0], p), np.subtract(line[1], p)))
            return a / d(line[0], line[1])
        else:
            return min(d(line[0], p), d(line[1], p))


# returns whether p is on the 3D line
def is_on_line(p, line):
    v1 = np.subtract(line[1], line[0])
    v2 = np.subtract(p, line[0])
    if compare(la.norm(v1), 0) == 0:
        return compare(d(p, line[0]), 0) == 0 or compare(d(p, line[1]), 0) == 0
    dist = la.norm(np.cross(v1, v2)) / la.norm(v1)
    return compare(dist, 0) == 0


# returns whether p is in 2D/3D triangle tri
def is_in_tri(tri, p):
    if len(p) == 3:
        # 3d, need rotate the triangle so that it can be projected onto a plane without any loss of information
        if is_above(tri, p) != 0:  # not even on the plane
            return -1
        n = np.cross(np.subtract(tri[1], tri[0]), np.subtract(tri[2], tri[0]))
        n = sympy.Matrix(n)
        if compare(n.norm(), 0) == 0:  # tri is a line
            return 0 if is_on_line(p, [tri[0], tri[1]]) or is_on_line(p, [tri[2], tri[1]]) or \
                        is_on_line(p, [tri[0], tri[2]]) else -1
        n = n.normalized()
        phi = sympy.acos(n[2])
        v = n.cross(sympy.Matrix([0, 0, 1]))
        if compare(v.norm(), 0) != 0:
            v = v.normalized()
            v_cross = sympy.Matrix(np.array([0, -v[2], v[1], v[2], 0, -v[0], -v[1], v[0], 0]).reshape(3, 3))
            M = (sympy.eye(3) * sympy.cos(phi)) + (v_cross * sympy.sin(phi)) + (
                    sympy.Matrix(3, 3, sympy.tensorproduct(v, v)) * (1 - sympy.cos(phi)))
            tri = np.array([M * sympy.Matrix(x) for x in tri])
            p = M * sympy.Matrix(p)
        tri = np.delete(tri, 2, axis=1)
        p = np.array(np.delete(p, 2, axis=0), dtype=float)
    # 2d, I used old code here, it actually computes the barycentric coords of p in tri,
    # when really I could have just done 3 is_left queries
    matrix = np.array([
        [tri[0][0], tri[1][0], tri[2][0]],
        [tri[0][1], tri[1][1], tri[2][1]],
        [1, 1, 1]
    ], dtype=float)
    if compare(la.det(matrix), 0) == 0:  # tri is not a triangle, but a line, just return whether it is on the line
        return 0 if min([compare(d_p_l(p, [tri[0], tri[2]]), 0), compare(d_p_l(p, [tri[1], tri[2]]), 0),
                         compare(d_p_l(p, [tri[0], tri[1]]), 0)]) == 0 else -1
    bary = np.matmul(la.inv(matrix), [p[0], p[1], 1])
    if all(compare(alpha, 0) == 1 for alpha in bary):
        return 1
    elif any(compare(alpha, 0) == -1 for alpha in bary):
        return -1
    else:
        return 0


# Tests whether p is inside the simple 2D polygon face
def in_poly(face, p, origin):
    if all(p[x] == origin[x] for x in [0, 1]):  # special case where p=origin
        return 0
    # using the feito-torres-PMC-polygon-1995 algorithm
    sum = 0
    for i in range(len(face)):
        edge = [face[i], face[(i + 1) % len(face)]]
        orient = la.norm(np.cross(np.subtract(edge[1], edge[0]), np.subtract(origin, edge[0])))
        sign = 1 if orient <= 0 else -1
        edge = np.array(edge)
        origin = np.array(origin)
        edge = np.append(edge, [origin], axis=0)
        inside = is_in_tri(edge, p)
        if inside == 0:  # On boundary
            sum += .5 * sign
        elif inside == 1:  # Inside
            sum += sign
    if sum == .5:
        return 0
    return 1 if sum >= 1 else -1


# Tests whether p is in the appropriately oriented tetrahedron [cw triange, origin]
def is_in_tetr(t, p):
    m = [[t[0][0], t[1][0], t[2][0], t[3][0]],
         [t[0][1], t[1][1], t[2][1], t[3][1]],
         [t[0][2], t[1][2], t[2][2], t[3][2]],
         [1, 1, 1, 1]]
    if compare(la.det(m), 0) == 0:
        return max(is_in_tri(t[0:3], p), is_in_tri(t[1:4], p),
                   is_in_tri([t[0], t[2], t[3]], p), is_in_tri([t[0], t[2], t[3]], p))
    alphas = la.solve(m, [p[0], p[1], p[2], 1])
    if all(compare(alpha, 0) == 1 for alpha in alphas):
        return 1
    elif any(compare(alpha, 0) == -1 for alpha in alphas):
        return -1
    else:
        return 0


# The algorithm to perform point membership check on a polyhedron
def polyhedron_membership_check(points, faces, p):
    origin = points[0]
    # uses the algorithm from Feito Torres's Inclusion test for general polyhedra
    # This algorithm, especially the pseudo code, was poorly written: there are some minor mistakes like forgetting an
    # i, and some more significant ones like how sign_f=sign_t, and both (I believe) should be sign(Q,F) rather than
    # (O,F), but it is a very robust algorithm
    inclusion = 0  # sum
    v_plus = dict()
    v_minus = dict()
    for i in range(len(faces)):
        face = faces[i]
        sign_f = is_above(face, p)
        if is_above(face, p) == 0:
            # has to be 2D
            flat_face = np.delete(face, 1, 1)
            if in_poly(flat_face, p[0:2], face[0][0:2]) != -1:
                return 0
        if is_on_line(p, [face[0], origin]) and ((sign_f == 1 and not str(face[0]) in v_plus)
                                                 or (sign_f == -1 and not str(face[0]) in v_minus)):
            inclusion += sign_f
            key = str(face[0])
            v_minus.__setitem__(key, face[0]) if sign_f == -1 else v_plus.__setitem__(key, face[0])
        elif is_on_line(p, [face[-1], origin]) and ((sign_f == 1 and not str(face[0]) in v_plus)
                                                    or (sign_f == -1 and not str(face[0]) in v_minus)):
            inclusion += sign_f
            key = str(face[-1])
            v_minus.__setitem__(key, face[-1]) if sign_f == -1 else v_plus.__setitem__(key, face[-1])
        else:
            # This part is questionable in terms of complexity, but amortized analysis shows that each edge is only used
            # twice (once for both incident faces), so it should be O(n) time complexity
            for j in range(1, len(face) - 1):  # go through every possible triangle
                sign_t = is_above([face[0], face[j], face[j + 1]], p)
                if is_in_tri([origin, face[0], face[j]], p) == 1 \
                        or is_in_tri([origin, face[j], face[j + 1]], p) == 1 \
                        or is_in_tri([origin, face[0], face[j + 1]], p) == 1:
                    inclusion += .5 * sign_t
                elif is_on_line(p, [origin, face[j]]) == 1 and \
                        ((sign_t == 1 and not str(face[j]) in v_plus) or
                         (sign_t == -1 and not str(face[j]) in v_minus)):
                    inclusion += sign_t
                    key = str(face[0])
                    v_minus.__setitem__(key, face[0]) if sign_t == -1 else v_plus.__setitem__(key, face[0])
                elif is_in_tetr([face[0], face[j], face[j + 1], origin], p) == 1:
                    inclusion += sign_t
                elif is_in_tetr([face[0], face[j], face[j + 1], origin], p) == 0:
                    inclusion += .5 * sign_t
    if inclusion == .5:
        return 0
    return 1 if inclusion == 1 else -1


# Computes the distance between a face and a point p, returning both the distance and the closest point
def dist_face_p(face, p):
    tet_m = [[face[0][0], face[0][1], face[0][2], 1],
             [face[1][0], face[1][1], face[1][2], 1],
             [face[2][0], face[2][1], face[2][2], 1],
             [p[0], p[1], p[2], 1]]
    # Need only check 3 points if all are planar
    volume = la.det(tet_m) / 6
    v1 = np.subtract(face[1], face[0])
    v2 = np.subtract(face[2], face[0])
    normal = np.cross(v1, v2)
    tri_area = la.norm(normal) / 2
    height = volume / tri_area
    unit_normal = np.divide(normal, la.norm(normal))
    projected_point = np.add(p, np.multiply(height, unit_normal))
    if len(face) == 3:
        is_in = is_in_tri(face, projected_point)
    else:
        is_in = in_poly(face, projected_point, face[0])
    if is_in != -1:
        return height, projected_point
    min = sys.maxsize
    for i in range(len(face)):
        vert = face[i]
        val = d(p, vert)
        if val < min:
            min = val
            projected_point = vert
    return min, projected_point


# Computes the distance between a polyhedron and a point p by computing the distance from each face
def ply_dist(faces, p):
    min = float(sys.maxsize)
    point = list()
    for face in faces:
        dist, new_point = dist_face_p(face, p)
        if abs(dist) < abs(min):
            min = dist
            point = new_point
    return min, point


# If the polyhedron is made purely of triangles, we can speed up computation significantly by focusing only on
# tetrahedra rather than arbitrary pyramids, as in Feito Torres' algorithm. Also, there are less degeneracies.
def tri_mesh_pmc(triangles, p):
    origin = triangles[0][0]
    inclusion = 0
    for tri in triangles:
        o_sign = is_above(tri, origin)
        if o_sign == 0:
            if is_in_tri(tri, p) != -1:
                return 0
            else:
                continue
        in_tet = is_in_tetr(np.concatenate((tri, [origin]), axis=0), p)
        if in_tet == -1:
            continue
        p_sign = is_above(tri, p)
        sign = p_sign * o_sign
        if sign == 0:
            if is_in_tri(tri, p) != -1:
                return 0
        elif in_tet == 1:
            inclusion += sign
        elif in_tet == 0:
            inclusion += .5 * sign
    if inclusion >= 1:
        return 1
    else:
        return -1


def tri_mesh_volume_area(triangles):
    origin = triangles[0][0]
    vol = 0
    surface_area = 0
    for tri in triangles:
        tet_m = [[tri[0][0], tri[0][1], tri[0][2], 1],
                 [tri[1][0], tri[1][1], tri[1][2], 1],
                 [tri[2][0], tri[2][1], tri[2][2], 1],
                 [origin[0], origin[1], origin[2], 1]]
        this_vol = la.det(tet_m) / 6
        this_area = signed_tri_area(tri)
        surface_area += this_area
        vol += this_vol
    return abs(vol), abs(surface_area)


# Takes a planar face in 3d space and rotates and projects it to 2d. Fails on collinear points
def make_2d(face):
    try:
        n = np.cross(np.subtract(face[1], face[0]), np.subtract(face[2], face[0]))
    except IndexError:
        raise DimensionException('Less than 3 points, points are collinear by definition', 0)
    n = sympy.Matrix(n)
    if compare(n.norm(), 0) == 0:  # points are collinear
        raise DimensionException('Points are collinear', 1)
    n = n.normalized()
    phi = sympy.acos(n[2])
    v = n.cross(sympy.Matrix([0, 0, 1]))
    if compare(v.norm(), 0) != 0:
        v = v.normalized()
        v_cross = sympy.Matrix(np.array([0, -v[2], v[1], v[2], 0, -v[0], -v[1], v[0], 0]).reshape(3, 3))
        M = (sympy.eye(3) * sympy.cos(phi)) + (v_cross * sympy.sin(phi)) + (
                sympy.Matrix(3, 3, sympy.tensorproduct(v, v)) * (1 - sympy.cos(phi)))
        face = np.array([M * sympy.Matrix(x) for x in face])
    face = np.delete(face, 2, axis=1)
    return face


# Deprecated
# An attempt to implement the algorithm described here: Frédéric Cazals, Kanhere Harshad, Sebastien Loriot. Computing
# the Volume of a Union of Balls: a Certified Algorithm. [Research Report] RR-7013, INRIA. 2009, pp.25. <inria-00409374>
# I later found this has already been implemented in the Structural BioInformatics Library, and decided to use that.
def volume(rad_dict, AABB):
    points = np.array(list(rad_dict.keys()))
    radii = np.array(list(rad_dict.values()))
    c = list()  # tess.Container(points, limits=AABB, radii=radii, periodic=False)
    tri = Delaunay(points, qhull_options='QJ')
    tot_vol = 0
    for cell in c:
        o_i = cell.pos
        r_i = cell.radius
        vertices = np.array(cell.vertices())
        sphere_region = vertices[np.array(cell.face_vertices())]
        neighbors = np.array(cell.neighbors())
        neighbors = neighbors[np.where(neighbors >= 0)]
        neighbors = points[neighbors]
        big_vertex_set = list()
        # Compute planar faces for all neighbors
        for o_j in neighbors:
            r_j = rad_dict[tuple(o_j)]
            region = list()
            normals = cell.normals()
            d_ij = d(o_i, o_j)
            u_ij = o_j - o_i / d_ij
            h_ij = (d_ij ** 2 + r_i ** 2 - r_j ** 2) / 2 * d_ij
            o_ij = o_i + h_ij * u_ij
            for index, face in enumerate(sphere_region):
                norm = normals[index]
                if d(norm, u_ij) < EPS:
                    region = face
                    break
            if len(region) == 0:
                raise BaseException("Could not match a face to any pair of vertices")
            if r_i ** 2 - h_ij ** 2 < 0:  # This face does not intersect the sphere
                continue
            r_ij = np.sqrt(r_i ** 2 - h_ij ** 2)
            # if len(region) == 1:
            #     if d(region[0], o_ij) >= r_ij:
            #         plan_area = np.pi * r_ij ** 2
            #         # add_to_set(o_ij, big_vertex_set, 0)
            #     else:
            #         dist = d(region[0], o_ij)
            #         half_len_e = np.sqrt(r_ij ** 2 - dist ** 2)
            #         theta = 2 * np.arcsin(half_len_e/r_ij)
            #         d_vec = (region[0] - o_ij) / dist
            #         n = (o_i - o_j) / d_ij
            #         r_z = [[n[0]**2, n[0]*n[1] - n[2], n[0]*n[2] + n[1]],
            #                [n[0]*n[1] + n[2], n[1]**2, n[1]*n[2] - n[0]],
            #                [n[0]*n[2] - n[1], n[0]*n[1] + n[0], n[2]**2]]
            #         r_vec = np.matmul(d_vec, r_z) / dist * half_len_e
            #         [v1, v2] = [region[0] + r_vec, region[0] - r_vec]
            #         plan_area = signed_tri_area([v1, v2, o_ij]) + r_ij * theta / 2
            #         big_vertex_set = add_to_set(v1, big_vertex_set, 0)
            #         big_vertex_set = add_to_set(v2, big_vertex_set, 0)
            # else:
            plan_area, vertices = planar_area(o_ij, r_ij, region)
            # tot_vol += plan_area * 1 / 3 * dist_face_p(vertices, o_ij)
            for vertex in vertices:
                big_vertex_set = add_to_set(vertex, big_vertex_set, 0)
            tot_vol += plan_area * h_ij / 3
        # Compute top face for spherical calculations
        if len(big_vertex_set) > 3:
            hull = ConvexHull(big_vertex_set)
            min_height = sys.maxsize
            top_face = None
            # Polygonal faces:
            for face in hull.simplices:
                face = hull.points[face]
                height = dist_face_p(face, o_i)[0]
                if height < min_height:
                    top_face = face
                    min_height = height
        else:
            top_face = np.array(big_vertex_set)
        # make sure no new edges have been made
        edges = list()
        top_neighbors = list()
        top_face_normal = np.cross(top_face[1] - top_face[0], top_face[1] - top_face[2]) if len(top_face) >= 3 \
            else top_face[0] - o_i
        for index in range(len(top_face)):
            vertex = (top_face[index] + top_face[(index + 1) % len(top_face)]) / 2
            comparisons = [compare(d(vertex, o_i), d(vertex, o_j)) == 0 for o_j in neighbors]
            if any(comparisons):
                edges.append([top_face[index], top_face[(index + 1) % len(top_face)]])
                places = np.where(comparisons)
                if len(places[0]) > 1:
                    for place in places[0]:
                        # print(neighbors[place] - o_i)
                        # print(np.dot(neighbors[place] - o_i, top_face_normal))
                        if compare(np.dot(neighbors[place] - o_i, top_face_normal), 0) == 0:
                            places = place
                if type(places) is tuple:
                    places = places[0][0]
                    # raise Exception('No coplanar vertex for top face')
                top_neighbors.append(neighbors[places])
        # Compute spherical face
        v_surf_pyr = volume_of_spherical_area(edges, o_i, r_i, rad_dict, top_neighbors)
        tot_vol += v_surf_pyr
    return tot_vol


# Deprecated
# Same as above, but this one actually worked ;)
def volume_of_spherical_area(edges, o_i, r_i, rad_dict, top_neighbors):
    if len(top_neighbors) == 0:
        return 4 * np.pi * r_i ** 3 / 3
    if len(top_neighbors) == 1:
        h_ij = d(top_neighbors[0], o_i)
        k = r_i - h_ij
        return 2 * np.pi * (r_i ** 2 * k - k ** 3 / 3)
    sum_of_edges = 0
    sum_of_alphas = 0
    for index, o_j in enumerate(top_neighbors):
        edge = edges[index]
        r_j = rad_dict[tuple(o_j)]
        d_ij = d(o_i, o_j)
        u_ij = o_j - o_i / d_ij
        h_ij = (d_ij ** 2 + r_i ** 2 - r_j ** 2) / 2 * d_ij
        o_ij = o_i + h_ij * u_ij
        r_ij = np.sqrt(r_i ** 2 - h_ij ** 2)
        loc_sum = (1 - r_ij) * (2 * np.arcsin(la.norm(edge) / 2 * r_ij)) / r_ij
        sum_of_edges += loc_sum
        alpha = np.arccos(np.dot(edge[0] - o_ij, edge[1] - o_ij) / r_ij ** 2)
        sum_of_alphas += alpha
    return r_i ** 2 * (sum_of_edges + (2 * np.pi - sum_of_alphas)) * h_ij / 3


# Deprecated
# precisely same as above
def planar_area(o_ij, r_ij, region):
    plan_area = 0
    sum_of_alphas = 0
    vertices = list()
    for k, v_k in enumerate(region):
        e_k = np.array([v_k, region[(k + 1) % len(region)]])
        d_k = d_p_l(o_ij, e_k)
        if d_k > r_ij:
            continue
        if compare(d(o_ij, v_k), r_ij) < 0:
            vertices.append(v_k)
            if compare(d(o_ij, e_k[1]), r_ij) >= 0:
                d_v_k, d_v_k1 = d(o_ij, v_k), d(o_ij, e_k[1])
                vector = (e_k[1] - e_k[0]) / d(e_k[0], e_k[1])
                e_k[1] = v_k + vector * (np.sqrt(d_v_k ** 2 - d_k ** 2) + np.sqrt(r_ij ** 2 - d_k ** 2))
                vertices.append(e_k[1])
        elif compare(d(o_ij, e_k[1]), r_ij) < 0:
            d_v_k, d_v_k1 = d(o_ij, v_k), d(o_ij, e_k[1])
            vector = (e_k[0] - e_k[1]) / d(e_k[0], e_k[1])
            e_k[0] = e_k[1] + vector * (np.sqrt(d_v_k1 ** 2 - d_k ** 2) + np.sqrt(r_ij ** 2 - d_k ** 2))
        else:
            half_len_e = np.sqrt(r_ij ** 2 - d_k ** 2)
            d_v_k = d(o_ij, e_k[0])
            vector = (e_k[1] - e_k[0]) / d(e_k[0], e_k[1])
            center_on_edge = e_k[0] + vector * np.sqrt(d_v_k ** 2 - d_k ** 2)
            e_k = [center_on_edge - vector * half_len_e, center_on_edge + vector * half_len_e]
        len_e = d(e_k[0], e_k[1])
        sign = (on_left(o_ij, e_k) - .5) * 2
        A_k = .5 * d_k * len_e * sign
        if sign > 0:
            alpha_k = .5 * np.arccos(np.dot(e_k[0] - o_ij, e_k[0] - o_ij) / d(o_ij, e_k[0]) * d(o_ij, e_k[1]))
            sum_of_alphas += alpha_k
        plan_area += A_k
        vertices.append(e_k[0])
        vertices.append(e_k[1])
    arc_area = r_ij ** 2 * (2 * np.pi - sum_of_alphas) * .5
    plan_area += arc_area
    return plan_area, vertices

def ball_conv_hull(rad_dict):
    points = np.array(rad_dict.keys())
    return ConvexHull(points)



# An exception to throw when an object does not have the expected number of dimensions
class DimensionException(BaseException):
    def __init__(self, msg, ndim):
        self.__context__ = msg
        self.__ndim__ = ndim

    __ndim__ = property(lambda self: object(), lambda self, v: None, lambda self: None)
    pass
