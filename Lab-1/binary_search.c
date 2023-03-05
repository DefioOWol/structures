#define PY_SSIZE_T_CLEAN
#include <Python.h>


static PyObject* binary_search(PyObject* module, PyObject* args)
{
    PyObject* item;
    PyObject* iterable;
    if(!PyArg_ParseTuple(args, "OO", &iterable, &item))
        return NULL;
    int left = 0;
    int right = (int) PySequence_Size(iterable) - 1;
    int mid;
    while(left < right)
    {
        mid = (left + right) / 2;
        if(PyObject_RichCompareBool(
                item, PySequence_GetItem(iterable, mid), Py_LE
            ))
            right = mid;
        else
            left = mid + 1;
    }
    if(right < 0 || PyObject_RichCompareBool(
            item, PySequence_GetItem(iterable, left), Py_NE
        ))
    {
        Py_INCREF(Py_None);
        return Py_None;
    }
    item = PyLong_FromLong(left);
    Py_INCREF(item);
    return item;
}


static PyMethodDef binary_search_funcs[] = {
    {"binary_search", (PyCFunction) binary_search, METH_VARARGS, ""},
    {NULL}
};


static PyModuleDef binary_search_module = {
    PyModuleDef_HEAD_INIT,
    .m_name = "binary_search",
    .m_size = -1
};


PyMODINIT_FUNC PyInit_binary_search()
{
    PyObject* module = PyModule_Create(&binary_search_module);
    PyModule_AddFunctions(module, &binary_search_funcs[0]);
    return module;
}
