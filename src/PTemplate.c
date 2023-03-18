//
// Created by daniel on 10/27/22.
//

#include "PTemplate.h"
#include <stdio.h>
#include <unistd.h>
#include <stdlib.h>
#include <string.h>
#include <fcntl.h>
#include <math.h>
#include <time.h>
#include <python3.10/Python.h>
#include <libxml/parser.h>
#include <libxml/tree.h>
#include <libxml/xmlIO.h>
#include <libxml/xinclude.h>

// Packages for server-side
#include <netinet/tcp.h>
#include <sys/socket.h>
#include <sys/types.h>
#include <netinet/in.h>
#include <netdb.h>
#include <zconf.h>

#define HOSTNAME "localhost"

// Local python system locations - CHANGE THESE TO INSTALL
#define PY_LIB "/home/dani/anaconda3/envs/pyDTest/lib/python3.10"
#define PY_LIB_DYNLOAD "/home/dani/anaconda3/envs/pyDTest/lib/python3.10/lib-dynload"
#define PY_PACKAGES "/home/dani/anaconda3/envs/pyDTest/lib/python3.10/site-packages"
#define PY_HOME_BINARIES "/home/dani/anaconda3/envs/pyDTest/bin/python3.10m"
#define PY_EXECUTABLE "/home/dani/anaconda3/envs/pyDTest/bin/python3.10"
// This is only necessary if your python code is in a different directory, otherwise set it to the python_support
// directory or comment out wherever it is used
#define PY_LOCATION "/home/daniel/Coding/DTestFull/python_support"

/**
 * Enumerator for supported system types
 * (Maybe should be in DTest.h)
 */
enum systemTypes {
    Rhino = 0, OpenCasCade = 1, OpenSCAD = 2, MeshLab = 3, SolidWorks = 4, Inventor = 5
};

/**
 * Dumps the contents (not all) of temp
 * @param temp The Template struct to dump
 */
void dump_template(Template temp) {
    printf("\n========DUMPING TEMPLATE FILE=========\n");
    printf("Model: %s\n", temp.model);
//    printf("Queries: %lu\n", temp.queries);
    printf("Algorithm Precision: %f\n", temp.algorithmPrecision);
    printf("System: %i\n", temp.system);
    printf("Bounds: ");
    for (int i = 0; i < 6; i++) {
        printf("%f, ", temp.bounds[i > 2 ? 1 : 0][i % 3]);
    }
    printf("\nConvexity: %i\n", temp.convex);
    printf("========END DUMP=========\n\n");
}

/**
 * Dumps the contents of prop
 * @param prop The Properties struct to dump
 */
void dump_proxy(Proxy prox) {
    printf("\n========DUMPING PROPERTIES FILE=========\n");
    printf("Number of points: %lu\n", prox.num_points);
    printf("Proxy model is at: %p\n", prox.proxyModel);
    printf("========END DUMP=========\n\n");
}

/**
 * Dumps the contents of prop
 * @param prop The Properties struct to dump
 */
void dump_properties(Properties prop) {
    printf("\n========DUMPING PROPERTIES FILE=========\n");
    printf("Surface Area: %f\n", prop.surfaceArea);
    printf("Volume: %f\n", prop.volume);
    printf("Number of points: %lu\n", prop.proxy->num_points);
    printf("Proxy model is at: %p\n", prop.proxy);
    printf("========END DUMP=========\n\n");
}

/**
 * Creates a shared cover file for the given proxy model of the form rad$point~rad$point ...
 * @param filename the name of the file to write the shared cover to
 * @param proxy a pointer to the Proxy struct containing the proxy model to create the shared cover from
 */
void writeProxy(char *filename, Proxy *prox) {
    FILE *fp;
    fp = fopen(filename, "w");
    if (fp == NULL) {
        printf("Failed to open file for writing.\n");
        return;
    }

    for (int i = 0; i < prox->num_points; i++) {
        fprintf(fp, "%lf~(%lf, %lf, %lf)$", prox->proxyModel[i][3], prox->proxyModel[i][0], prox->proxyModel[i][1], prox->proxyModel[i][2]);
    }

    fclose(fp);
}


/**
 * Write the given proxy models and other necessary data to a template file
 * @param prox The proxy model calculated by getProxy
 * @param inf The various template informations that will be populated either by internal computation or inputs
 * @param doc A pointer to the xml doc that will be populated
 * @param filename The name of the template file that will be written
 * @return None
 *
 * http://xmlsoft.org/examples/tree2.c
 * This code was generated using the help of ChatGPT by OpenAI
 */
int writeTemplate(Proxy *prox, TemplateInfo *info, xmlDocPtr doc, char* filename) {
//    xmlNodePtr root_node = NULL, node = NULL, node1 = NULL;/* node pointers */

    /*
     * Creates a new document, a node and set it as a root node
     */
    doc = xmlNewDoc(BAD_CAST "1.0");

    // Create the root element and add it to the document
    xmlNodePtr root = xmlNewNode(NULL, BAD_CAST "template");
    xmlDocSetRootElement(doc, root);

    // Create a child for the template
//    xmlNodePtr templ = xmlNewChild(root, NULL);

    // Cast floating point data types to a xmlChar* using a buffer of size 64
    char buffer[64];

    // Add child elements for each field in the TemplateInfo struct
    xmlNodePtr sys_node = xmlNewChild(root, NULL, BAD_CAST "CAD_System_and_Version", NULL);
    xmlNewChild(sys_node, NULL, BAD_CAST "CAD_System_and_Version", BAD_CAST info->system);
    // Add the version?

    xmlNewChild(root, NULL, BAD_CAST "Unit_parameters", BAD_CAST info->units);

    xmlNodePtr tols = xmlNewChild(root, NULL, BAD_CAST "Tolerances", NULL);
    snprintf(buffer, sizeof(buffer), "%.5f", info->abs_tol);
    xmlNewChild(tols, NULL, BAD_CAST "Abs_tol", BAD_CAST buffer);
    snprintf(buffer, sizeof(buffer), "%.5f", info->par_tol);
    xmlNewChild(tols, NULL, BAD_CAST "Par_tol", BAD_CAST buffer);
    snprintf(buffer, sizeof(buffer), "%.5f", info->alg_tol);
    xmlNewChild(tols, NULL, BAD_CAST "Alg_tol", BAD_CAST buffer);

    xmlNodePtr model_info = xmlNewChild(root, NULL, BAD_CAST "Model_Information", NULL);
    // Write the file first
    if (!info->filename) {
        // Make a randomish name if we don't have one
        snprintf(buffer, sizeof(buffer), "prox_%05ld", time(0));
        info->filename = buffer;
    }
    writeProxy(info->filename, prox);
    xmlNewChild(model_info, NULL, BAD_CAST "FileName", BAD_CAST info->filename);
    xmlNewChild(model_info, NULL, BAD_CAST "Model_dim", BAD_CAST info->dim);
    xmlNewChild(model_info, NULL, BAD_CAST "Boundary_dim", BAD_CAST info->bd_dim);
    xmlNewChild(model_info, NULL, BAD_CAST "Convexity", BAD_CAST info->convexity);

    xmlNewChild(root, NULL, BAD_CAST "Representation_scheme", BAD_CAST info->representation);

    // Create a bounding_box element and add it as a child of the root element
    xmlNodePtr bounding_box = xmlNewChild(root, NULL, BAD_CAST "Bounding_box_coords", NULL);
    snprintf(buffer, sizeof(buffer), "%.10f", info->bbox.xmax);
    xmlNewProp(bounding_box, BAD_CAST "xmax", BAD_CAST buffer);
    snprintf(buffer, sizeof(buffer), "%.10f", info->bbox.ymax);
    xmlNewProp(bounding_box, BAD_CAST "ymax", BAD_CAST buffer);
    snprintf(buffer, sizeof(buffer), "%.10f", info->bbox.zmax);
    xmlNewProp(bounding_box, BAD_CAST "zmax", BAD_CAST buffer);
    snprintf(buffer, sizeof(buffer), "%.10f", info->bbox.xmin);
    xmlNewProp(bounding_box, BAD_CAST "xmin", BAD_CAST buffer);
    snprintf(buffer, sizeof(buffer), "%.10f", info->bbox.ymin);
    xmlNewProp(bounding_box, BAD_CAST "ymin", BAD_CAST buffer);
    snprintf(buffer, sizeof(buffer), "%.10f", info->bbox.zmin);
    xmlNewProp(bounding_box, BAD_CAST "zmin", BAD_CAST buffer);

    // Save the document to the specified file
    xmlSaveFormatFileEnc(filename, doc, "UTF-8", 1);


    // Free the memory used by the document
    xmlFreeDoc(doc);
}

/**
 * A currently unused method to perform network queries
 * @param host
 * @param port
 * @return
 */
// source: https://gist.github.com/nolim1t/126991
int socket_connect(char *host, in_port_t port) {
    struct hostent *hp;
    struct sockaddr_in addr;
    int on = 1, sock;

    if ((hp = gethostbyname(host)) == NULL) {
        herror("gethostbyname");
        exit(1);
    }
    bcopy(hp->h_addr, &addr.sin_addr, hp->h_length);
    addr.sin_port = htons(port);
    addr.sin_family = AF_INET;
    sock = socket(PF_INET, SOCK_STREAM, IPPROTO_TCP);
    setsockopt(sock, IPPROTO_TCP, TCP_NODELAY, (const char *) &on, sizeof(int));

    if (sock == -1) {
        perror("setsockopt");
        exit(1);
    }

    if (connect(sock, (struct sockaddr *) &addr, sizeof(struct sockaddr_in)) == -1) {
        perror("connect");
        exit(1);

    }
    return sock;
}

/**
 * The main call to compute the properties of a template that is an OCC system
 * @param template The given template containing settings etc
 * @param pModule The Python module to connect to
 * @param prop The Properties struct to populate
 * @param debug A flag for debug mode
 * @return 0 for success, 1 for failure
 */
int runOCCConfigure(Template template, PyObject *pModule, Properties *prop, int debug) {
    PyObject * pFunc;
    pFunc = PyObject_GetAttrString(pModule, "occ_configure");
    /* pFunc is a new reference */

    if (pFunc && PyCallable_Check(pFunc)) {

        PyObject * pArgs, *pValue, *pArg1, *pArg2;
        if (template.system != OpenCasCade) {
            fprintf(stderr, "Tried to run OCC configure on system %i, which is not OCC.\n", template.system);
            exit(1);
        }
        if (debug) {
            printf("Calling a new round of occ configure\n");
        }
        pArgs = PyTuple_New(2);
        // The arguments will be: alg_tol, model
        // Convert arguments to Python types
//        pArg1 = PyFloat_FromDouble(template.systemTolerance);
//        printf("Alg precision: %f\n", template.algorithmPrecision);
        pArg1 = PyFloat_FromDouble(template.algorithmPrecision);
        pArg2 = PyUnicode_DecodeFSDefault(template.model);
        PyTuple_SetItem(pArgs, 0, pArg1);
        PyTuple_SetItem(pArgs, 1, pArg2);
        // No longer need to set bounding box from
//        PyTuple_SetItem(pArgs, 2, pArg3);
//        for (int i = 0; i < 2; i++) {
//            for (int j = 0; j < 3; j++) {
//                pBoundArg = PyFloat_FromDouble(template.bounds[i][j]);
//                PyTuple_SetItem(pArgs, 3 + 3 * i + j, pBoundArg);
//            }
//        }
        // Call the function (I believe it waits for termination without needing to call Wait(NULL)
        pValue = PyObject_CallObject(pFunc, pArgs);
        if (pValue != NULL) {
            PyObject * pSurfAr, *pVol, *pProx;
            PyObject * pxmin, *pymin, *pzmin, *pxmax, *pymax, *pzmax;
            PyObject * pSize;
            if (!PyTuple_CheckExact(pValue)) {
                fprintf(stderr, "Did not receive a tuple from function call, exiting.\n");
                exit(1);
            }
            if (debug) {
                printf("The length of the tuple: %lo\n", PyTuple_Size(pValue));
            }
            // Get arguments back and make them usable
            pSurfAr = PyTuple_GetItem(pValue, 0);
            pVol = PyTuple_GetItem(pValue, 1);
            pProx = PyTuple_GetItem(pValue, 2);
            pxmin = PyTuple_GetItem(pValue, 3);
            pymin = PyTuple_GetItem(pValue, 4);
            pzmin = PyTuple_GetItem(pValue, 5);
            pxmax = PyTuple_GetItem(pValue, 6);
            pymax = PyTuple_GetItem(pValue, 7);
            pzmax = PyTuple_GetItem(pValue, 8);
            // Set the bounding box we found
            prop->bbox.xmin = PyFloat_AsDouble(pxmin);
            prop->bbox.ymin = PyFloat_AsDouble(pymin);
            prop->bbox.zmin = PyFloat_AsDouble(pzmin);
            prop->bbox.xmax = PyFloat_AsDouble(pxmax);
            prop->bbox.ymax = PyFloat_AsDouble(pymax);
            prop->bbox.zmax = PyFloat_AsDouble(pzmax);

            // Now we have even more
            prop->surfaceArea = PyFloat_AsDouble(pSurfAr);
            if (debug) {
                printf("Surface Area: %f\n", prop->surfaceArea);
            }
            prop->volume = PyFloat_AsDouble(pVol);
            // The point array might be large, so we need to do some extra work
            pSize = PyLong_FromSsize_t(PyDict_Size(pProx));
            unsigned long size = PyLong_AsUnsignedLong(pSize);
            prop->proxy->proxyModel = malloc(size * sizeof(double *));
            for (int i = 0; i < size; i++) {
                prop->proxy->proxyModel[i] = malloc(4 * sizeof(double)); // Each entry is [x,y,z,rad]
            }
            if (debug) {
                printf("Successfully allocated space for proxy model\n");
            }
            PyObject * key, *value;
            PyObject * xVal, *yVal, *zVal;
            double x, y, z;
            int i = 0;
            Py_ssize_t
                    pos = 0;
            if (debug) {
                printf("Starting to loop through each element in dictionary\n");
                printf("The size of the dictionary is: %lo\n", size);
            }
            prop->proxy->num_points = size;
            // Retrieves all the points
            while (PyDict_Next(pProx, &pos, &key, &value)) {
                xVal = PyTuple_GetItem(key, 0);
                yVal = PyTuple_GetItem(key, 1);
                zVal = PyTuple_GetItem(key, 2);
                x = PyFloat_AsDouble(xVal);
                y = PyFloat_AsDouble(yVal);
                z = PyFloat_AsDouble(zVal);
                if (debug) {
                    printf("Working on point [%f, %f, %f], the value is: %f\n", x, y, z, PyFloat_AsDouble(value));
                }
                if (x == -1 && PyErr_Occurred()) {
                    PyErr_Print();
                    fprintf(stderr, "Failed to read value %i in the proxy model.\n", i);
                    exit(1);
                }
                prop->proxy->proxyModel[i][0] = x;
                prop->proxy->proxyModel[i][1] = y;
                prop->proxy->proxyModel[i][2] = z;
                prop->proxy->proxyModel[i][3] = PyFloat_AsDouble(value);
                i++;
            }
            if (debug) {
                printf("Successfully read the proxy model\n");
                printf("Successfully set the proxy model\n");
            }
            if (debug) {
                printf("Successfully populated new properties structure!\n");
                dump_properties(*prop);
            }
        } else {
            Py_DECREF(pFunc);
            Py_DECREF(pModule);
            PyErr_Print();
            fprintf(stderr, "Call failed\n");
            exit(1);
        }
    } else {
        if (PyErr_Occurred())
            PyErr_Print();
        fprintf(stderr, "Cannot find function \"%s\"\n", "occ_configure");
    }
    Py_DECREF(pFunc);
    return 0;
}

/**
 * The main call to compute the properties of a template that is a SolidWorks system
 * @param template The given template containing settings etc
 * @param pModule The Python module to connect to
 * @param prop The Properties struct to populate
 * @param debug A flag for debug mode
 * @return 0 for success, 1 for failure
 */
int runSWConfigure(Template template, PyObject *pModule, Properties *prop, int debug) {
    PyObject * pFunc;
    pFunc = PyObject_GetAttrString(pModule, "sw_configure");
    /* pFunc is a new reference */

    if (pFunc && PyCallable_Check(pFunc)) {

        PyObject * pArgs, *pValue, *pArg1, *pArg2;
        if (template.system != SolidWorks) {
            fprintf(stderr, "Tried to run OCC configure on system %i, which is not OCC.\n", template.system);
            exit(1);
        }
        if (debug) {
            printf("Calling a new round of solidworks configure\n");
        }
        pArgs = PyTuple_New(2);
        // The arguments will be: alg_tol, model
        // Convert arguments to Python types
//        pArg1 = PyFloat_FromDouble(template.systemTolerance);
//        printf("Alg precision: %f\n", template.algorithmPrecision);
        pArg1 = PyFloat_FromDouble(template.algorithmPrecision);
        pArg2 = PyUnicode_DecodeFSDefault(template.model);
        PyTuple_SetItem(pArgs, 0, pArg1);
        PyTuple_SetItem(pArgs, 1, pArg2);
        // No longer need to set bounding box from
//        PyTuple_SetItem(pArgs, 2, pArg3);
//        for (int i = 0; i < 2; i++) {
//            for (int j = 0; j < 3; j++) {
//                pBoundArg = PyFloat_FromDouble(template.bounds[i][j]);
//                PyTuple_SetItem(pArgs, 3 + 3 * i + j, pBoundArg);
//            }
//        }
        // Call the function (I believe it waits for termination without needing to call Wait(NULL)
        pValue = PyObject_CallObject(pFunc, pArgs);
        if (pValue != NULL) {
            PyObject * pSurfAr, *pVol, *pProx;
            PyObject * pSize;
            if (!PyTuple_CheckExact(pValue)) {
                fprintf(stderr, "Did not receive a tuple from function call, exiting.\n");
                exit(1);
            }
            if (debug) {
                printf("The length of the tuple: %lo\n", PyTuple_Size(pValue));
            }
            // Get arguments back and make them usable
            pSurfAr = PyTuple_GetItem(pValue, 0);
            pVol = PyTuple_GetItem(pValue, 1);
            pProx = PyTuple_GetItem(pValue, 2);
            prop->surfaceArea = PyFloat_AsDouble(pSurfAr);
            if (debug) {
                printf("Surface Area: %f\n", prop->surfaceArea);
            }
            prop->volume = PyFloat_AsDouble(pVol);
            // The point array might be large, so we need to do some extra work
            pSize = PyLong_FromSsize_t(PyDict_Size(pProx));
            unsigned long size = PyLong_AsUnsignedLong(pSize);
            prop->proxy->proxyModel = malloc(size * sizeof(double *));
            for (int i = 0; i < size; i++) {
                prop->proxy->proxyModel[i] = malloc(4 * sizeof(double)); // Each entry is [x,y,z,rad]
            }
            if (debug) {
                printf("Successfully allocated space for proxy model\n");
            }
            PyObject * key, *value;
            PyObject * xVal, *yVal, *zVal;
            double x, y, z;
            int i = 0;
            Py_ssize_t
                    pos = 0;
            if (debug) {
                printf("Starting to loop through each element in dictionary\n");
                printf("The size of the dictionary is: %lo\n", size);
            }
            prop->proxy->num_points = size;
            // Retrieves all the points
            while (PyDict_Next(pProx, &pos, &key, &value)) {
                xVal = PyTuple_GetItem(key, 0);
                yVal = PyTuple_GetItem(key, 1);
                zVal = PyTuple_GetItem(key, 2);
                x = PyFloat_AsDouble(xVal);
                y = PyFloat_AsDouble(yVal);
                z = PyFloat_AsDouble(zVal);
                if (debug) {
                    printf("Working on point [%f, %f, %f], the value is: %f\n", x, y, z, PyFloat_AsDouble(value));
                }
                if (x == -1 && PyErr_Occurred()) {
                    PyErr_Print();
                    fprintf(stderr, "Failed to read value %i in the proxy model.\n", i);
                    exit(1);
                }
                prop->proxy->proxyModel[i][0] = x;
                prop->proxy->proxyModel[i][1] = y;
                prop->proxy->proxyModel[i][2] = z;
                prop->proxy->proxyModel[i][3] = PyFloat_AsDouble(value);
                i++;
            }
            if (debug) {
                printf("Successfully read the proxy model\n");
                printf("Successfully set the proxy model\n");
            }
            if (debug) {
                printf("Successfully populated new properties structure!\n");
                dump_properties(*prop);
            }
        } else {
            Py_DECREF(pFunc);
            Py_DECREF(pModule);
            PyErr_Print();
            fprintf(stderr, "Call failed\n");
            exit(1);
        }
    } else {
        if (PyErr_Occurred())
            PyErr_Print();
        fprintf(stderr, "Cannot find function \"%s\"\n", "occ_configure");
    }
    Py_DECREF(pFunc);
    return 0;
}

/**
 * The main call to compute the properties of a template that is a SolidWorks system
 * @param template The given template containing settings etc
 * @param pModule The Python module to connect to
 * @param prop The Properties struct to populate
 * @param debug A flag for debug mode
 * @return 0 for success, 1 for failure
 */
int runInvConfigure(Template template, PyObject *pModule, Properties *prop, int debug) {
    PyObject * pFunc;
    pFunc = PyObject_GetAttrString(pModule, "inv_configure");
    /* pFunc is a new reference */

    if (pFunc && PyCallable_Check(pFunc)) {

        PyObject * pArgs, *pValue, *pArg1, *pArg2;
        if (template.system != Inventor) {
            fprintf(stderr, "Tried to run Inventor configure on system %i, which is not Inventor.\n", template.system);
            exit(1);
        }
        if (debug) {
            printf("Calling a new round of Inventor configure\n");
        }
        pArgs = PyTuple_New(2);
        // The arguments will be: alg_tol, model
        // Convert arguments to Python types
//        pArg1 = PyFloat_FromDouble(template.systemTolerance);
//        printf("Alg precision: %f\n", template.algorithmPrecision);
        pArg1 = PyFloat_FromDouble(template.algorithmPrecision);
        pArg2 = PyUnicode_DecodeFSDefault(template.model);
        PyTuple_SetItem(pArgs, 0, pArg1);
        PyTuple_SetItem(pArgs, 1, pArg2);
        // No longer need to set bounding box from
//        PyTuple_SetItem(pArgs, 2, pArg3);
//        for (int i = 0; i < 2; i++) {
//            for (int j = 0; j < 3; j++) {
//                pBoundArg = PyFloat_FromDouble(template.bounds[i][j]);
//                PyTuple_SetItem(pArgs, 3 + 3 * i + j, pBoundArg);
//            }
//        }
        // Call the function (I believe it waits for termination without needing to call Wait(NULL)
        pValue = PyObject_CallObject(pFunc, pArgs);
        if (pValue != NULL) {
            PyObject * pSurfAr, *pVol, *pProx;
            PyObject * pSize;
            if (!PyTuple_CheckExact(pValue)) {
                fprintf(stderr, "Did not receive a tuple from function call, exiting.\n");
                exit(1);
            }
            if (debug) {
                printf("The length of the tuple: %lo\n", PyTuple_Size(pValue));
            }
            // Get arguments back and make them usable
            pSurfAr = PyTuple_GetItem(pValue, 0);
            pVol = PyTuple_GetItem(pValue, 1);
            pProx = PyTuple_GetItem(pValue, 2);
            prop->surfaceArea = PyFloat_AsDouble(pSurfAr);
            if (debug) {
                printf("Surface Area: %f\n", prop->surfaceArea);
            }
            prop->volume = PyFloat_AsDouble(pVol);
            // The point array might be large, so we need to do some extra work
            pSize = PyLong_FromSsize_t(PyDict_Size(pProx));
            unsigned long size = PyLong_AsUnsignedLong(pSize);
            prop->proxy->proxyModel = malloc(size * sizeof(double *));
            for (int i = 0; i < size; i++) {
                prop->proxy->proxyModel[i] = malloc(4 * sizeof(double)); // Each entry is [x,y,z,rad]
            }
            if (debug) {
                printf("Successfully allocated space for proxy model\n");
            }
            PyObject * key, *value;
            PyObject * xVal, *yVal, *zVal;
            double x, y, z;
            int i = 0;
            Py_ssize_t
                    pos = 0;
            if (debug) {
                printf("Starting to loop through each element in dictionary\n");
                printf("The size of the dictionary is: %lo\n", size);
            }
            prop->proxy->num_points = size;
            // Retrieves all the points
            while (PyDict_Next(pProx, &pos, &key, &value)) {
                xVal = PyTuple_GetItem(key, 0);
                yVal = PyTuple_GetItem(key, 1);
                zVal = PyTuple_GetItem(key, 2);
                x = PyFloat_AsDouble(xVal);
                y = PyFloat_AsDouble(yVal);
                z = PyFloat_AsDouble(zVal);
                if (debug) {
                    printf("Working on point [%f, %f, %f], the value is: %f\n", x, y, z, PyFloat_AsDouble(value));
                }
                if (x == -1 && PyErr_Occurred()) {
                    PyErr_Print();
                    fprintf(stderr, "Failed to read value %i in the proxy model.\n", i);
                    exit(1);
                }
                prop->proxy->proxyModel[i][0] = x;
                prop->proxy->proxyModel[i][1] = y;
                prop->proxy->proxyModel[i][2] = z;
                prop->proxy->proxyModel[i][3] = PyFloat_AsDouble(value);
                i++;
            }
            if (debug) {
                printf("Successfully read the proxy model\n");
                printf("Successfully set the proxy model\n");
            }
            if (debug) {
                printf("Successfully populated new properties structure!\n");
                dump_properties(*prop);
            }
        } else {
            Py_DECREF(pFunc);
            Py_DECREF(pModule);
            PyErr_Print();
            fprintf(stderr, "Call failed\n");
            exit(1);
        }
    } else {
        if (PyErr_Occurred())
            PyErr_Print();
        fprintf(stderr, "Cannot find function \"%s\"\n", "occ_configure");
    }
    Py_DECREF(pFunc);
    return 0;
}


/**
 * The main call to compute the properties of a template that is a SCAD system
 * @param template The given template containing settings etc
 * @param pModule The Python module to connect to
 * @param prop The Properties struct to populate
 * @param debug A flag for debug mode
 * @return 0 for success, 1 for failure
 */
int runSCADConfigure(Template template, PyObject *pModule, Properties *prop, int debug) {
    PyObject * pFunc, *pValue, *pArgs;
    pFunc = PyObject_GetAttrString(pModule, "scad_configure");
    /* pFunc is a new reference */

    if (pFunc && PyCallable_Check(pFunc)) {

        PyObject *pArg1, *pArg2, *pArg3, *pBoundArg;
        if (template.system != OpenSCAD) {
            fprintf(stderr, "Tried to run SCAD configure on system %i, which is not SCAD.\n", template.system);
            exit(1);
        }
        if (debug) {
            printf("Calling a new round of scad configure\n");
        }
        pArgs = PyTuple_New(9);
        // The arguments will be: Sys_eps, alg_eps, and some access to the shape (filename?)
        pArg1 = PyFloat_FromDouble(template.systemTolerance);
        pArg2 = PyFloat_FromDouble(template.algorithmPrecision);
        pArg3 = PyUnicode_DecodeFSDefault(template.model);
        PyTuple_SetItem(pArgs, 0, pArg1);
        PyTuple_SetItem(pArgs, 1, pArg2);
        PyTuple_SetItem(pArgs, 2, pArg3);
        for (int i = 0; i < 2; i++) {
            for (int j = 0; j < 3; j++) {
                pBoundArg = PyFloat_FromDouble(template.bounds[i][j]);
                PyTuple_SetItem(pArgs, 3 + 3 * i + j, pBoundArg);
            }
        }
        pValue = PyTuple_New(3);
        pValue = PyObject_CallObject(pFunc, pArgs);
        if (pValue != NULL) {
            PyObject * pSurfAr, *pVol, *pProx;
            PyObject * pSize;
            if (!PyTuple_CheckExact(pValue)) {
                fprintf(stderr, "Did not receive a tuple from function call, exiting.\n");
                exit(1);
            }
            if (debug) {
                printf("The length of the tuple: %lo\n", PyTuple_Size(pValue));
            }
            pSurfAr = PyTuple_GetItem(pValue, 0);
            pVol = PyTuple_GetItem(pValue, 1);
            pProx = PyTuple_GetItem(pValue, 2);
            prop->surfaceArea = PyFloat_AsDouble(pSurfAr);
            if (debug) {
                printf("Surface Area: %f\n", prop->surfaceArea);
            }
            prop->volume = PyFloat_AsDouble(pVol);
            pSize = PyLong_FromSsize_t(PyDict_Size(pProx));
            unsigned long size = PyLong_AsUnsignedLong(pSize);
            prop->proxy->proxyModel = malloc(size * sizeof(double *));
            for (int i = 0; i < size; i++) {
                prop->proxy->proxyModel[i] = malloc(4 * sizeof(double));
            }
            if (debug) {
                printf("Successfully allocated space for proxy model\n");
            }
            PyObject * key, *value;
            PyObject * xVal, *yVal, *zVal;
            double x, y, z;
            int i = 0;
            Py_ssize_t
                    pos = 0;
            if (debug) {
                printf("Starting to loop through each element in dictionary\n");
                printf("The size of the dictionary is: %lo\n", size);
            }
            prop->proxy->num_points = size;
            while (PyDict_Next(pProx, &pos, &key, &value)) {
                xVal = PyTuple_GetItem(key, 0);
                yVal = PyTuple_GetItem(key, 1);
                zVal = PyTuple_GetItem(key, 2);
                x = PyFloat_AsDouble(xVal);
                y = PyFloat_AsDouble(yVal);
                z = PyFloat_AsDouble(zVal);
                if (debug) {
                    printf("Working on point [%f, %f, %f], the value is: %f\n", x, y, z, PyFloat_AsDouble(value));
                }
                if (x == -1 && PyErr_Occurred()) {
                    PyErr_Print();
                    fprintf(stderr, "Failed to read value %i in the proxy model.\n", i);
                    exit(1);
                }
                prop->proxy->proxyModel[i][0] = x;
                prop->proxy->proxyModel[i][1] = y;
                prop->proxy->proxyModel[i][2] = z;
                prop->proxy->proxyModel[i][3] = PyFloat_AsDouble(value);
                i++;
            }
            if (debug) {
                printf("Successfully read the proxy model\n");
                printf("Successfully set the proxy model\n");
            }
            if (debug) {
                printf("Successfully populated new properties structure!\n");
                dump_properties(*prop);
            }

        } else {
            Py_DECREF(pFunc);
            Py_DECREF(pModule);
            PyErr_Print();
            fprintf(stderr, "Call failed\n");
            exit(1);
        }
    } else {
        if (PyErr_Occurred())
            PyErr_Print();
        fprintf(stderr, "Cannot find function \"%s\"\n", "scad_configure");
    }
    return 0;
}


/**
 * The main call to compute the properties of a template that is a MeshLab system
 * @param template The given template containing settings etc
 * @param pModule The Python module to connect to
 * @param prop The Properties struct to populate
 * @param debug A flag for debug mode
 * @return 0 for success, 1 for failure
 */
int runMeshLabConfigure(Template template, PyObject *pModule, Properties *prop, int debug) {
    if (debug) {
        fprintf(stdout, "Starting to run MeshLab Configure.\n");
    }
    PyObject * pFunc;
    pFunc = PyObject_GetAttrString(pModule, "meshlab_configure_cover");
    /* pFunc is a new reference */

    if (pFunc && PyCallable_Check(pFunc)) {
        PyObject * pArgs, *pValue, *pArg1, *pArg2, *pArg3, *pBoundArg;
        if (template.system != MeshLab) {
            fprintf(stderr, "Tried to run MeshLab configure on system %i, which is not MeshLab.\n", template.system);
            exit(1);
        }
        if (debug) {
            printf("Calling a new round of MeshLab configure\n");
        }
        pArgs = PyTuple_New(9);
        // The arguments will be: Sys_eps, alg_eps, and some access to the shape (filename?)
        pArg1 = PyFloat_FromDouble(template.systemTolerance);
        pArg2 = PyFloat_FromDouble(template.algorithmPrecision);
        pArg3 = PyUnicode_DecodeFSDefault(template.model);
        PyTuple_SetItem(pArgs, 0, pArg1);
        PyTuple_SetItem(pArgs, 1, pArg2);
        PyTuple_SetItem(pArgs, 2, pArg3);
        for (int i = 0; i < 2; i++) {
            for (int j = 0; j < 3; j++) {
                pBoundArg = PyFloat_FromDouble(template.bounds[i][j]);
                PyTuple_SetItem(pArgs, 3 + 3 * i + j, pBoundArg);
            }
        }
        pValue = PyTuple_New(3);
        pValue = PyObject_CallObject(pFunc, pArgs);
        if (pValue != NULL) {
            PyObject * pSurfAr, *pVol, *pProx;
            PyObject * pSize;
            if (!PyTuple_CheckExact(pValue)) {
                fprintf(stderr, "Did not receive a tuple from function call, exiting.\n");
                exit(1);
            }
            if (debug) {
                printf("The length of the tuple: %lo\n", PyTuple_Size(pValue));
            }
            pSurfAr = PyTuple_GetItem(pValue, 0);
            pVol = PyTuple_GetItem(pValue, 1);
            pProx = PyTuple_GetItem(pValue, 2);
            prop->surfaceArea = PyFloat_AsDouble(pSurfAr);
            if (debug) {
                printf("Surface Area: %f\n", prop->surfaceArea);
            }
            prop->volume = PyFloat_AsDouble(pVol);
            pSize = PyLong_FromSsize_t(PyDict_Size(pProx));
            unsigned long size = PyLong_AsUnsignedLong(pSize);
            prop->proxy->proxyModel = malloc(size * sizeof(double *));
            for (int i = 0; i < size; i++) {
                prop->proxy->proxyModel[i] = malloc(4 * sizeof(double));
            }
            if (debug) {
                printf("Successfully allocated space for proxy model\n");
            }
            PyObject * key, *value;
            PyObject * xVal, *yVal, *zVal;
            double x, y, z;
            int i = 0;
            Py_ssize_t
                    pos = 0;
            if (debug) {
                printf("Starting to loop through each element in dictionary\n");
                printf("The size of the dictionary is: %lo\n", size);
            }
            prop->proxy->num_points = size;
            while (PyDict_Next(pProx, &pos, &key, &value)) {
                xVal = PyTuple_GetItem(key, 0);
                yVal = PyTuple_GetItem(key, 1);
                zVal = PyTuple_GetItem(key, 2);
                x = PyFloat_AsDouble(xVal);
                y = PyFloat_AsDouble(yVal);
                z = PyFloat_AsDouble(zVal);
                if (debug) {
                    printf("Working on point [%f, %f, %f]\n", x, y, z);
                }
                if (x == -1 && PyErr_Occurred()) {
                    PyErr_Print();
                    fprintf(stderr, "Failed to read value %i in the proxy model.\n", i);
                    exit(1);
                }
                prop->proxy->proxyModel[i][0] = x;
                prop->proxy->proxyModel[i][1] = y;
                prop->proxy->proxyModel[i][2] = z;
                prop->proxy->proxyModel[i][3] = PyFloat_AsDouble(value);
                i++;
            }
            if (debug) {
                printf("Successfully read the proxy model\n");
                printf("Successfully set the proxy model\n");
            }
            if (debug) {
                printf("Successfully populated new properties sructure!\n");
                dump_properties(*prop);
            }
        } else {
            Py_DECREF(pFunc);
            Py_DECREF(pModule);
            PyErr_Print();
            fprintf(stderr, "Call failed\n");
            exit(1);
        }
    } else {
        if (PyErr_Occurred())
            PyErr_Print();
        fprintf(stderr, "Cannot find function \"%s\"\n", "meshlab_configure");
    }
    return 0;
}


/**
 * The main call to compute the properties of a template that is a Rhino system
 * @param template The given template containing settings etc
 * @param pModule The Python module to connect to
 * @param prop The Properties struct to populate
 * @param debug A flag for debug mode
 * @return 0 for success, 1 for failure
 */
int runRhinoConfigure(Template template, PyObject *pModule, Properties *prop, int debug) {
    // For now, this only assumes that the given filename is a cover and does not do complex calculations
    PyObject * pFunc;
    pFunc = PyObject_GetAttrString(pModule, "rhino_configure");
    /* pFunc is a new reference */

    if (pFunc && PyCallable_Check(pFunc)) {

        PyObject * pArgs, *pValue, *pArg1, *pArg2, *pArg3;
        if (template.system != Rhino) {
            fprintf(stderr, "Tried to run rhino configure on system %i, which is not Rhino.\n", template.system);
            exit(1);
        }
        if (debug) {
            printf("Calling a new round of rhino configure\n");
        }
        pArgs = PyTuple_New(3);
        // The arguments will be: Sys_eps, alg_eps, and some access to the shape (filename?)
        pArg1 = PyFloat_FromDouble(template.systemTolerance);
        pArg2 = PyFloat_FromDouble(template.algorithmPrecision);
        pArg3 = PyUnicode_DecodeFSDefault(template.model);
        PyTuple_SetItem(pArgs, 0, pArg1);
        PyTuple_SetItem(pArgs, 1, pArg2);
        PyTuple_SetItem(pArgs, 2, pArg3);

        pValue = PyTuple_New(3);
        pValue = PyObject_CallObject(pFunc, pArgs);
        if (pValue != NULL) {
            PyObject * pSurfAr, *pVol, *pProx;
            PyObject * pSize;
            if (!PyTuple_CheckExact(pValue)) {
                fprintf(stderr, "Did not receive a tuple from function call, exiting.\n");
                exit(1);
            }
            if (debug) {
                printf("The length of the tuple: %lo\n", PyTuple_Size(pValue));
            }
            pSurfAr = PyTuple_GetItem(pValue, 0);
            pVol = PyTuple_GetItem(pValue, 1);
            pProx = PyTuple_GetItem(pValue, 2);
            prop->surfaceArea = PyFloat_AsDouble(pSurfAr);
            if (debug) {
                printf("Surface Area: %f\n", prop->surfaceArea);
            }
            prop->volume = PyFloat_AsDouble(pVol);
            pSize = PyLong_FromSsize_t(PyDict_Size(pProx));
            unsigned long size = PyLong_AsUnsignedLong(pSize);
            prop->proxy->proxyModel = malloc(size * sizeof(double *));
            for (int i = 0; i < size; i++) {
                prop->proxy->proxyModel[i] = malloc(4 * sizeof(double));
            }
            if (debug) {
                printf("Successfully allocated space for proxy model\n");
            }
            PyObject * key, *value;
            PyObject * xVal, *yVal, *zVal;
            double x, y, z;
            int i = 0;
            Py_ssize_t
                    pos = 0;
            if (debug) {
                printf("Starting to loop through each element in dictionary\n");
                printf("The size of the dictionary is: %lo\n", size);
            }
            prop->proxy->num_points = size;
            while (PyDict_Next(pProx, &pos, &key, &value)) {
                xVal = PyTuple_GetItem(key, 0);
                yVal = PyTuple_GetItem(key, 1);
                zVal = PyTuple_GetItem(key, 2);
                x = PyFloat_AsDouble(xVal);
                y = PyFloat_AsDouble(yVal);
                z = PyFloat_AsDouble(zVal);
                if (debug) {
                    printf("Working on point [%f, %f, %f], the value is: %f\n", x, y, z, PyFloat_AsDouble(value));
                }
                if (x == -1 && PyErr_Occurred()) {
                    PyErr_Print();
                    fprintf(stderr, "Failed to read value %i in the proxy model.\n", i);
                    exit(1);
                }
                prop->proxy->proxyModel[i][0] = x;
                prop->proxy->proxyModel[i][1] = y;
                prop->proxy->proxyModel[i][2] = z;
                prop->proxy->proxyModel[i][3] = PyFloat_AsDouble(value);
                i++;
            }
            if (debug) {
                printf("Successfully read the proxy model\n");
                printf("Successfully set the proxy model\n");
            }
            if (debug) {
                printf("Successfully populated new properties structure!\n");
                dump_properties(*prop);
            }
        } else {
            Py_DECREF(pFunc);
            Py_DECREF(pModule);
            PyErr_Print();
            fprintf(stderr, "Call failed\n");
            exit(1);
        }
    } else {
        if (PyErr_Occurred())
            PyErr_Print();
        fprintf(stderr, "Cannot find function \"%s\"\n", "rhino_configure");
    }
    Py_DECREF(pFunc);
    return 0;

}


/**
 * The wrapper function for creating a proxy model
 * @param props Pointers to the Properties structs to populate
 * @param template1 The first Template
 * @param template2 The second Template
 * @param debug A flag for debug
 * @return 0 for success, exit on failure
 */
int getProxy(Properties *prop1, Template template1, int debug) {
    if (template1.system == OpenCasCade || template1.system == OpenSCAD || template1.system == Rhino) {
        // Create the Python Connection- Prone to failure
        PyObject * pName, *pModule;
        size_t stringsize;
        char py_paths[1024];
        snprintf(py_paths, sizeof py_paths, "%s%s%s%s%s", PY_LIB, ":", PY_LIB_DYNLOAD, ":", PY_PACKAGES);
        // Forcibly sets the path to include all Python Libraries- would need to be changed on another system
        Py_SetPath(Py_DecodeLocale(py_paths, &stringsize));
        Py_Initialize();
        // Again, forcibly makes sure we are using the correct Python- was having issues with this,
        // and may have overdone it
        Py_SetPythonHome(Py_DecodeLocale(PY_HOME_BINARIES, &stringsize));
        Py_SetProgramName(Py_DecodeLocale(PY_EXECUTABLE, &stringsize));
        if (debug) {
            printf("The python home: %s\n", Py_EncodeLocale(Py_GetPythonHome(), &stringsize));
            printf("The exec prefix: %s\n", Py_EncodeLocale(Py_GetPrefix(), &stringsize));
            printf("The program name: %s\n", Py_EncodeLocale(Py_GetProgramName(), &stringsize));
            printf("The full paths in the program: %s\n", Py_EncodeLocale(Py_GetPath(), &stringsize));
        }
        // This one is necessary; this is how it knows where your Python scripts are
        char py_sup_call[512];
        snprintf(py_sup_call, sizeof py_sup_call, "%s%s%s", "import sys\nsys.path.append(\"", PY_LOCATION, "\")\n");
        PyRun_SimpleString(py_sup_call);
        // Python is loaded, begin to load the specific module
        pName = PyUnicode_DecodeFSDefault("py_interface");
        pModule = PyImport_Import(pName);
        Py_DECREF(pName);
        if (pModule != NULL) {
            // Call appropriate version of Configure depending on system- order matters!
            if (template1.system == OpenSCAD) {
                if (runSCADConfigure(template1, pModule, prop1, debug) != 0) {
                    fprintf(stderr, "Failed to run SCAD configure for %s\n", template1.model);
                }
            }
            if (template1.system == OpenCasCade) {
                if (runOCCConfigure(template1, pModule, prop1, debug) != 0) {
                    fprintf(stderr, "Failed to run OCC configure for %s\n", template1.model);
                    exit(1);
                }
            }
            if (template1.system == SolidWorks) {
                if (runSWConfigure(template1, pModule, prop1, debug) != 0) {
                    fprintf(stderr, "Failed to run SolidWorks configure for %s\n", template1.model);
                }
            }
            if (template1.system == Inventor) {
                if (runInvConfigure(template1, pModule, prop1, debug) != 0) {
                    fprintf(stderr, "Failed to run Inventor configure for %s\n", template1.model);
                }
            }
            if (template1.system == Rhino) {
                if (runRhinoConfigure(template1, pModule, prop1, debug) != 0) {
                    fprintf(stderr, "Failed to run Rhino configure for %s\n", template1.model);
                }
            }
            if (template1.system == MeshLab) {
                if (runMeshLabConfigure(template1, pModule, prop1, debug) != 0) {
                    fprintf(stderr, "Failed to run MeshLab configure for %s\n", template1.model);
                }
            }
        } else {
            PyErr_Print();
            fprintf(stderr, "Failed to load py_interface.py\n");
            exit(1);
        }
        if (Py_FinalizeEx() < 0) {
            fprintf(stderr, "Failed to close python connection\n");
            exit(1);
        } else {
            Py_Finalize();
        }
        // If we ever figure out the Rino compute server, changes would come here, as we wouldn't need Python
    } else if (template1.system == Rhino) {
        socket_connect(HOSTNAME, 80); // Might need to change ports
    } else if (template1.system == OpenSCAD) {

    } else {
        fprintf(stderr, "System not recognized, aborting\n");
        exit(1);
    }
    if (debug) {
//        printf("props[0] is point in the method at %p and props[1] at %p\n", props[0], props[1]);
//        printf("props[1] has volume: %f\n", props[1]->volume);
    }
    return 0;
}


/**
 * The main command to run PTemplate, makes a single template, including the proxy. This may create a few different
 * processes.
 *
 */
int makeTemplate(float tol, int debug, int system, char* templateName, char *units, double abs_tol, double par_tol,
                 double alg_tol, char *filename, unsigned int dim, unsigned int bd_dim, int convexity,
                 char *representation) { // double xmax, double ymax, double zmax, double xmin, double ymin, double zmin
    // Populate all the template info we have, guessing what we don't know
    TemplateInfo *tinfo;
    tinfo->system = system;
    tinfo->filename = filename;
    if (abs_tol) {
        tinfo->abs_tol = abs_tol;
    } else {
        tinfo->abs_tol = tol;  // default to given DTest tolerance
    }
    if (par_tol) {
        tinfo->par_tol = par_tol;
    } else {
        tinfo->par_tol = tinfo->abs_tol*100;
    }
    if (alg_tol) {
        tinfo->alg_tol = alg_tol;
    } else {
        tinfo->alg_tol = -1;  // alg_tol is inferred later if -1
    }
    if (bd_dim) {
        tinfo->bd_dim = bd_dim;
    } else {
        tinfo->bd_dim = 2;  // assume 3D
    }
    if (dim) {
        tinfo->dim = dim;
    } else {
        tinfo->dim = 3;  // assume 3D
    }
    tinfo->convexity = convexity;  // Assume not unless specified
    tinfo->representation = representation;  // okay if Not given
    tinfo->units = units;  // Can't guess units

    // Start defining templates
    Template temp1;
    temp1.system = system;
    setTolerance(tol);
    Properties *prop;
    Proxy *prox;
    prop->proxy = prox;

    // The main part of the code, runs the configure script, passing workload over to Python backend
    int success = getProxy(prop, temp1, debug);
    if (!success) {
        fprintf(stderr, "GetProxy failed, exiting.\n");
        exit(1);
    }
    if (debug) {
        printf("Actually got the properties!!!!!\n");
        printf("props[0] is pointing outside the method at %p\n", prop);
        printf("prop has volume: %f\n", prop->volume);
        dump_properties(*prop);
    }

    // Set bounding box
    tinfo->bbox = prop->bbox;

    xmlDocPtr doc;
    writeTemplate(prox, tinfo, doc, templateName);
    return 0;
}


/**
 * A tool that automates the creation of the Template file and the proxy model
 * @param argc arg count
 * @param argv arg vector
 * @return 0 for success, 1 for failure
 */
//int main(int argc, char *argv[]) {
//    // Optional bbox param
//
//    // Free proxy models of prop1 and prop2
//    for (int i = 0; i < (int) sizeof(prop1.proxyModel) / sizeof(prop1.proxyModel[0]); i++) {
//        free(prop1.proxyModel[i]);
//    }
//    free(prop1.proxyModel);
//    for (int i = 0; i < (int) sizeof(prop2.proxyModel) / sizeof(prop2.proxyModel[0]); i++) {
//        free(prop2.proxyModel[i]);
//    }
//    free(prop2.proxyModel);
//    return 0;
//};