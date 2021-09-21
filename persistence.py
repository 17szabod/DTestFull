import gudhi
import pyexcel as pe
import matplotlib.pyplot as plt
from skimage import metrics
pc1_matrix = pe.get_array(file_name='/Users/engs2281/Documents/Interoperability/INV_allpts.xls')
# We assume the max distance between two points is max_edge_length -- 2epsilon
rips_complex = gudhi.RipsComplex(points=pc1_matrix,
                                 max_edge_length=60.0)

simplex_tree = rips_complex.create_simplex_tree(max_dimension=3)

result_str = 'Rips complex is of dimension ' + repr(simplex_tree.dimension()) + ' - ' + \
    repr(simplex_tree.num_simplices()) + ' simplices - ' + \
    repr(simplex_tree.num_vertices()) + ' vertices.'
print(result_str)
fmt = '%s -> %.2f'
for filtered_value in simplex_tree.get_filtration():
    print(fmt % tuple(filtered_value))

diag1 = simplex_tree.persistence(min_persistence=0.4)
gudhi.plot_persistence_barcode(diag1)
plt.show()

gudhi.plot_persistence_diagram(diag1)
plt.show()
print("Inventor model: Betti_numbers()=")
print(simplex_tree.betti_numbers())

pc2_matrix = pe.get_array(file_name='/Users/engs2281/Documents/Interoperability/SW_allpts.xls') # done
rips_complex2 = gudhi.RipsComplex(points=pc2_matrix,
                                 max_edge_length=60.0)
simplex_tree2 = rips_complex2.create_simplex_tree(max_dimension=3)
result_str2 = 'Rips complex is of dimension ' + repr(simplex_tree2.dimension()) + ' - ' + \
    repr(simplex_tree2.num_simplices()) + ' simplices - ' + \
    repr(simplex_tree2.num_vertices()) + ' vertices.'
print(result_str2)
for filtered_value in simplex_tree2.get_filtration():
   print(fmt % tuple(filtered_value))

diag2 = simplex_tree2.persistence(min_persistence=0.4)
print("SolidWorks model: Betti_numbers()=")
print(simplex_tree2.betti_numbers())

gudhi.plot_persistence_barcode(diag2)
plt.show()
gudhi.plot_persistence_diagram(diag2)
plt.show()
print(diag1)

a1=simplex_tree.persistence_intervals_in_dimension(1)
a2=simplex_tree2.persistence_intervals_in_dimension(1)
message = "Bottleneck distance approximation between the diagrams=" + '%.2f' % gudhi.bottleneck_distance(a1, a2, 0.1)
print(message)



