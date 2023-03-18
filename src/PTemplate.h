//
// Created by daniel on 10/25/2022.
//

#ifndef PTEMPLATE_PTEMPLATE_H
#define PTEMPLATE_PTEMPLATE_H

/**
 * A Bounding Box structure that holds the dimensions (With added tolerance!!) of the model
 */
typedef struct {
    double xmax;  // Put bounding box as individual entries
    double ymax;  // Put bounding box as individual entries
    double zmax;  // Put bounding box as individual entries
    double xmin;  // Put bounding box as individual entries
    double ymin;  // Put bounding box as individual entries
    double zmin;  // Put bounding box as individual entries
} BBox;

/**
 * A Template structure describes anything that can be read from an xml tamplate file
 */
typedef struct {
    int system;
    double systemTolerance;
    float algorithmPrecision;
//    long queries; // The queries supported will be represented by a bitmask-- we will define a set of all possible
//    // queries (less than 32), and the bitmask will represent a subset that is supported.
    int manifold;
    int connected;
    int semilocallysimplyconnected; //added, Duygu
    int closed; //added, Duygu
    int orientation; //added, Duygu
    int convex;
    float minimumFeatureSize;
    BBox bbox; //added, Daniel  form: [[xmin, ymin, zmin], [xmax, ymax, zmax]]
    char *model; // A way to access the model, whether it be a filename or a unique id in a database (filename for now)
    char *proxy; // A filename for the proxy model. The proxy is in the form of temp_spheres.txt from earlier versions
    char *templateName;
} Template;

/**
 * A structure that holds the proxy model
 */
typedef struct {
    unsigned long num_points;
    double **proxyModel;  // A 2D, n by 4 array representing a union of balls
    // NOTE: proxyModel, because of its size, is on the heap, so free it after use
    // Also, it would be much more efficient to handle this via some stream, as it would avoid memory access
} Proxy;

/**
 * A Properties structure that encodes the properties of the cover of a model
 */
typedef struct {
    double surfaceArea;
    double volume;
    BBox bbox;
    Proxy *proxy;
} Properties;

/**
 * A structure that holds various mmodel information for the template
 */
typedef struct {
    int system;
    char *units;  // not in template normalize
    double abs_tol;  // Absolute tolerance (precision)
    double par_tol;  // Parametric tolerance (precision)
    double alg_tol;  // Algorithm tolerance (of PMC)
    char *filename;  // File name for the proxy
    unsigned int dim;  // Model dimension
    unsigned int bd_dim;  // Model boundary dimension
    int convexity;  // Boolean, 1: convex, 0: not
    char *representation;  // name of model representation in system
    BBox bbox;
//    double xmax;  // Put bounding box as individual entries
//    double ymax;  // Put bounding box as individual entries
//    double zmax;  // Put bounding box as individual entries
//    double xmin;  // Put bounding box as individual entries
//    double ymin;  // Put bounding box as individual entries
//    double zmin;  // Put bounding box as individual entries
} TemplateInfo;

float tolerance;

Template readTemplate(char *filename, char *testName, int debug);// what is testName?, Duygu

int setTolerance(float tol);

float getTolerance();

int makeTemplate(float tol, int debug, int system, char* templateName, char *units, double abs_tol, double par_tol,
                 double alg_tol, char *filename, unsigned int dim, unsigned int bd_dim, int convexity,
                 char *representation);

int getProxy(Properties *prop1, Template template1, int debug);

#endif //PTEMPLATE_PTEMPLATE_H
