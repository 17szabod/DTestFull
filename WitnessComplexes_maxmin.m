% This script calculates the intervals for a witness complex - Section 5.3

clc; clear; close all;
import edu.stanford.math.plex4.*;

%% Torus Example

%%%%%%%%%%%%%%%%%num_points = 10000;
num_landmark_points = 50;
max_dimension = 4;
num_divisions = 1000;

% create the set of points
% % % % % % %%%%%point_cloud = examples.PointCloudExamples.getRandomSphereProductPoints(num_points, 1, 2);

load empat.mat
load empatSW.mat
point_cloud_I = empat
point_cloud_S= empatSW

% % % % % % % % % create a sequential maxmin landmark selector
% % % % % % % % landmark_selector = api.Plex4.createMaxMinSelector(point_cloud, num_landmark_points);
% % % % % % % % R = landmark_selector.getMaxDistanceFromPointsToLandmarks()
% % % % % % % % max_filtration_value = R / 8;
% % % % % % % % 
% % % % % % % % % create a witness stream
% % % % % % % % stream = api.Plex4.createWitnessStream(landmark_selector, max_dimension, max_filtration_value, num_divisions);
% % % % % % % % 
% % % % % % % % % print out the size of the stream
% % % % % % % % num_simplices = stream.getSize()
% % % % % % % % 
% % % % % % % % % get persistence algorithm over Z/2Z
% % % % % % % % persistence = api.Plex4.getModularSimplicialAlgorithm(max_dimension, 2);
% % % % % % % % 
% % % % % % % % % compute the intervals
% % % % % % % % intervals = persistence.computeIntervals(stream);
% % % % % % % % 
% % % % % % % % % create the barcode plots
% % % % % % % % options.filename = 'witnessTorus';
% % % % % % % % options.max_filtration_value = max_filtration_value;
% % % % % % % % options.max_dimension = max_dimension - 1;
% % % % % % % % plot_barcodes(intervals, options);



% DS added below 
max_filtration_value=4.35;

% create a sequential maxmin landmark selector
landmark_selector_I = api.Plex4.createMaxMinSelector(point_cloud_I, num_landmark_points);
R_I = landmark_selector_I.getMaxDistanceFromPointsToLandmarks()
max_filtration_value_I = R_I / 8

% create a witness stream
stream_I = api.Plex4.createWitnessStream(landmark_selector_I, max_dimension, max_filtration_value, num_divisions);
stream_I.finalizeStream()
eulerCharacteristic(stream_I, 3)
% print out the size of the stream
num_simplices_I = stream_I.getSize();

% get persistence algorithm over Z/2Z
persistence_I = api.Plex4.getModularSimplicialAlgorithm(max_dimension, 2);

% compute the intervals
intervals_I = persistence_I.computeIntervals(stream_I);

% create the barcode plots
options.filename = 'witnessInventor';
options.max_filtration_value = max_filtration_value_I;
options.max_dimension = max_dimension - 1;
plot_barcodes(intervals_I, options);

% create a sequential maxmin landmark selector
landmark_selector_S = api.Plex4.createMaxMinSelector(point_cloud_S, num_landmark_points);
R_S = landmark_selector_S.getMaxDistanceFromPointsToLandmarks()
max_filtration_value_S = R_S / 8

% create a witness stream
stream_S = api.Plex4.createWitnessStream(landmark_selector_S, max_dimension, max_filtration_value, num_divisions);
stream_S.finalizeStream()
% print out the size of the stream
num_simplices_S = stream_S.getSize();
eulerCharacteristic(stream_S, 3);
% get persistence algorithm over Z/2Z
persistence_S = api.Plex4.getModularSimplicialAlgorithm(max_dimension, 2);

% compute the intervals
intervals_S = persistence_S.computeIntervals(stream_S);

% create the barcode plots
options.filename = 'witnessSolidWorks';
options.max_filtration_value = max_filtration_value_S;
options.max_dimension = max_dimension - 1;
plot_barcodes(intervals_S, options);



intervals_I_dim0=intervals_I.getIntervalsAtDimension(0);
intervals_S_dim0=intervals_S.getIntervalsAtDimension(0);
bottleneck_distance_dim0 = edu.stanford.math.plex4.bottleneck.BottleneckDistance.computeBottleneckDistance(intervals_I_dim0,intervals_S_dim0)

intervals_I_dim1=intervals_I.getIntervalsAtDimension(1);
intervals_S_dim1=intervals_S.getIntervalsAtDimension(1);
bottleneck_distance_dim1 = edu.stanford.math.plex4.bottleneck.BottleneckDistance.computeBottleneckDistance(intervals_I_dim1,intervals_S_dim1)

intervals_I_dim2=intervals_I.getIntervalsAtDimension(2);
intervals_S_dim2=intervals_S.getIntervalsAtDimension(2);
bottleneck_distance_dim2 = edu.stanford.math.plex4.bottleneck.BottleneckDistance.computeBottleneckDistance(intervals_I_dim2,intervals_S_dim2)
