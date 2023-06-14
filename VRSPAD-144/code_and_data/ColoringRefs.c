#define PY_SSIZE_T_CLEAN
#include <Python.h>
#include <numpy/arrayobject.h>
#include <math.h>
#include <stdbool.h>

// Forward function declaration.
static PyObject *nonredundant_search(PyObject *self, PyObject *args);
static PyObject *annealing_sampling(PyObject *self, PyObject *args);


//method list. One entry for each method/function
static PyMethodDef methods[] = {
    {"nonredundant_search", nonredundant_search, METH_VARARGS, "Doc string."},
    {"annealing_sampling", annealing_sampling, METH_VARARGS, "Doc string."},
    {NULL, NULL, 0, NULL} //this line of junk is added so that methods[] is thought of as an array and not just a pointer? huh?
};



static struct PyModuleDef coloringModule = {
    PyModuleDef_HEAD_INIT,
    "ColoringRefs",
    "some graph coloring algorithms",
    -1,
    methods
};


PyMODINIT_FUNC PyInit_ColoringRefs(void){
    return PyModule_Create(&coloringModule);
}

// Boilerplate: Module initialization.
// PyMODINIT_FUNC PyInit_ColoringRefs(void) {
//   (void) Py_InitModule("ColoringRefs", methods);
//   import_array();
// }

/*****************************************************************************
 * Array access macros.                                                      *
 *****************************************************************************/
#define edges_data(x0, x1) ((npy_int32*)(PyArray_DATA(edges)))[x0 + x1*PyArray_DIM(edges, 1)]

#define edges_shape(i) (PyArray_DIM(edges, i))

//PyArray_DATA returns a void pointer to the start of the data;
//we reinterpret it as a pointer to our chosen data type,
//and then index into the array using x0
#define coloring_data(x0) ((npy_int32*)(PyArray_DATA(coloring)))[x0]

//OR:
//reinterpret void pointer as a simple 64 bit value,
//and then add to it based on the desired index and stride values;
//convert the value back into the pointer of the desired data type, and use the data from the pointer?


//Actual functions --------------------------------------------------------
/************************************************************************/

//recursive function - for internal module use only
void nofunc(void){}


bool search_recursion(PyObject *edges, PyObject *coloring, int nnodes, int ncolors, int node_indx){

  if (nnodes == node_indx) {return true;}

  for (int color = 0; color<ncolors; color++){
    coloring_data(node_indx) = color;

    bool ok = true;
    for (int j=0; j<nnodes; j++){
      if (edges_data(node_indx, j) == 1 && coloring_data(j) == color) {ok = false;} 
    }
    if (ok) {
      if (search_recursion(edges, coloring, nnodes, ncolors, node_indx+1)) {return true;}
    }

  }
  coloring_data(node_indx) = -1;
  return false;

}




static PyObject *nonredundant_search(PyObject *self, PyObject *args) {
  // Declare variables.
  npy_intp ncolors, nnodes;
  // // PyArrayObject *edges, *coloring;

  PyObject *edges_arg=NULL, *coloring_arg=NULL;
  PyObject *edges=NULL, *coloring=NULL;

  // Parse arguments. 
  if (!PyArg_ParseTuple(args, "iOO",
                        &ncolors, 
                        &edges, 
                        &coloring)) {
    return NULL;
  }


  nnodes = edges_shape(0);

  //initialize coloring to indicate that it is not colored:
  for (int i = 0; i<nnodes; i++){
    coloring_data(i) = -1;
  }

  //first node is set to 0 by default - no need to iterate through colors of the first node
  coloring_data(0) = 0;

  if (search_recursion(edges, coloring, nnodes, ncolors, 1)){
    Py_RETURN_NONE;
  }
  else {
    coloring_data(0) = -1; //set to indicate failure
  }


  // // nnodes = (*(npy_int8*)PyArray_DATA(coloring)) + 5;
  // coloring_data(0) = nnodes;

  Py_RETURN_NONE;
};


static PyObject *annealing_sampling(PyObject *self, PyObject *args) {
  // Declare variables.
  int ncolors, nnodes, maxiters;
  float temp;
  // // PyArrayObject *edges, *coloring;

  PyObject *edges_arg=NULL, *coloring_arg=NULL;
  PyObject *edges=NULL, *coloring=NULL;

  // Parse arguments. 
  if (!PyArg_ParseTuple(args, "iifOO",
                        &ncolors, 
                        &maxiters,
                        &temp,
                        &edges, 
                        &coloring)) {
    return NULL;
  }

  nnodes = edges_shape(0);

  //initialize coloring to a uniform coloring
  for (int i = 0; i<nnodes; i++){
    coloring_data(i) = 0;
  }



  //keep track of how many bad edges there are.  We will incrimentally adjust this number rather than recalculate
  int bad_edges = 0;
  for (int i = 0; i<nnodes; i++){
    for (int j = 0; j<i; j++){
      if (edges_data(i,j) == 1) bad_edges++; //must be bad, since we initialize to all be the same color
    }
  }

  for (int iter = 0; iter < maxiters; iter++){
    //randomly choose a node and color to attempt an update:
    int node2try = rand()%nnodes;
    int color2try = rand()%ncolors;

    //calculate difference in bad edges if update is accepted:
    int current_bad = 0;
    for (int j = 0; j<nnodes; j++){
      if (edges_data(node2try, j) == 1 && coloring_data(j) == coloring_data(node2try)) {current_bad++;} 
    }
    int proposed_bad = 0;
    for (int j = 0; j<nnodes; j++){
      if (edges_data(node2try, j) == 1 && coloring_data(j) == color2try) {proposed_bad++;} 
    }

    float move_de = proposed_bad - current_bad;

    //decide wether or not to accept the update:
    float p_move;
    if (move_de <= 0) p_move = 1;
    else p_move = exp(-move_de/temp);
    float rnd = (float)(rand()%1000000)/(float)1000000;
    // float div =        1000000;
    // rnd = rnd / div;

    // coloring_data(0) = temp*100;
    // coloring_data(1) = move_de;
    // coloring_data(2) = p_move*100;
    // coloring_data(3) = rnd*1000000;
    // Py_RETURN_NONE;


    if (p_move > rnd) {
      bad_edges = bad_edges + move_de;
      coloring_data(node2try) = color2try;
      if (bad_edges <= 0){
          Py_RETURN_NONE;
      }
    }

    //update state if needed, and check if we have stumbled upon a solution:

  }

  coloring_data(0) = -1; //failed to find a solution
  Py_RETURN_NONE;

}