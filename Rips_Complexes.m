
clc; clear; close all;
import edu.stanford.math.plex4.*;
import eulerCharacteristic.*

max_dimension = 3;
max_filtration_value =33;
num_divisions = 1000;

% create the set of points
load empat.mat
point_cloud1 = empat;
size(point_cloud1)
figure
scatter3(point_cloud1(:,1), point_cloud1(:,2), point_cloud1(:,3), '.')
axis equal
view(120,80)
% create a Vietoris-Rips stream 
stream1 = api.Plex4.createVietorisRipsStream(point_cloud1, max_dimension, max_filtration_value, num_divisions);
num_simplices1 = stream1.getSize()

% get persistence algorithm over Z/2Z
persistence1 = api.Plex4.getDefaultSimplicialAlgorithm(max_dimension);%api.Plex4.getModularSimplicialAlgorithm(max_dimension1, 2);

% compute the intervals
intervals1 = persistence1.computeIntervals(stream1);

% create the barcode plots
options.filename = 'ripsINV';
options.max_filtration_value = max_filtration_value;
options.max_dimension = max_dimension - 1;
options.side_by_side = true;
plot_barcodes(intervals1, options);

% get the infinite barcodes
infinite_barcodes1 = intervals1.getInfiniteIntervals()

% print out betti numbers array
betti_numbers_array1 = infinite_barcodes1.getBettiSequence()

eulerCharacteristic(stream1, max_dimension-1)
%% SW Model
%max_dimension = 3;% max dimension of any simplex included
%max_filtration_value = 21;
%num_divisions = 100;
%persistence_diagram(intervals1,0, 2, 'SW')
% create the set of points
%load pointsTorusGrid.mat
%load empatSW_all.mat This has 720 points
%point_cloud2 = empatSW_all;
load empatSW.mat
%point_cloud = pointsTorusGrid;
point_cloud2 = empatSW;
size(point_cloud2)

% create a Vietoris-Rips stream 
stream2 = api.Plex4.createVietorisRipsStream(point_cloud2, max_dimension, max_filtration_value, num_divisions);
num_simplices2 = stream2.getSize()

% get persistence algorithm over Z/2Z
%persistence = api.Plex4.getModularSimplicialAlgorithm(max_dimension, 2);
persistence2 = api.Plex4.getDefaultSimplicialAlgorithm(max_dimension) %deniorum
% compute the intervals
intervals2 = persistence2.computeIntervals(stream2);
%%persistence_diagram(intervals2,0, 2, 'INV')
% create the barcode plots
options.filename = 'ripsSW';
options.max_filtration_value = max_filtration_value; %the largest filtration value to be displayed;
options.max_dimension = max_dimension - 1; % the largest persistent homology dimension to be displayed;
options.side_by_side = true;%so that betti barcodes of different dims are displayed side by side instead top=bottom
plot_barcodes(intervals2, options);

% get the infinite barcodes
infinite_barcodes2 = intervals2.getInfiniteIntervals()

% print out betti numbers array
betti_numbers_array2 = infinite_barcodes2.getBettiSequence() %The computed semi-infinite intervals are merely those that persist until t = tmax
eulerCharacteristic(stream2, max_dimension-1)


intervals1_dim1=intervals1.getIntervalsAtDimension(1)
intervals2_dim1=intervals2.getIntervalsAtDimension(1)
intervals1_dim0=intervals1.getIntervalsAtDimension(0);
intervals2_dim0=intervals2.getIntervalsAtDimension(0);
%bottleneck_distance_dim = edu.stanford.math.plex4.bottleneck.BottleneckDistance.computeBottleneckDistance(intervals1_dim1,intervals2_dim1)

%subplot(1, 2, 1);
% scatter(point_cloud1(:,1), point_cloud1(:, 2));
% title("Shaft from Inventor");
% %subplot(1, 2, 2);
% scatter(point_cloud2(:,1), point_cloud2(:, 2));
% title("Shaft from SolidWorks");
