#define PY_SSIZE_T_CLEAN
#include <Python.h>
#include <float.h>


typedef struct
{
    void (*null)();
    void (*insert)(PyObject*, int, PyObject*);
    PyObject* (*pop)(PyObject*, int);
    void (*set_item)(PyObject*, int, PyObject*);
    PyObject* (*get_item)(PyObject*, int);
    int (*reversed)(PyObject*, PyObject*, int);
    PyObject* (*get_type_info)();
    int (*check_type)(PyObject*);
} object_methods;


typedef struct
{
    PyObject_HEAD
    short t_size;
    object_methods* methods;
    size_t step;
    size_t size;
    size_t capacity;
    void* items;
} carray_object;


static int check_long(PyObject* num)
{
    if(PyObject_RichCompareBool(num, PyLong_FromLong(LONG_MAX), Py_GT)
       || PyObject_RichCompareBool(num, PyLong_FromLong(LONG_MIN), Py_LT)
       || !PyLong_Check(num))
    {
        PyErr_SetString(PyExc_TypeError, "value must be C long");
        return -1;
    }
    return 0;
}


static int check_double(PyObject* num)
{
    if(PyObject_RichCompareBool(num, PyFloat_FromDouble(DBL_MAX), Py_GT)
       || PyObject_RichCompareBool(num, PyFloat_FromDouble(-DBL_MAX), Py_LT))
    {
        PyErr_SetString(PyExc_TypeError, "value must be C double");
        return -1;
    }
    return 0;
}


static void set_long_item(PyObject* self, int index, PyObject* num)
{
    ((long*) ((carray_object*) self)->items)[index] = PyLong_AsLong(num);
}


static void set_double_item(PyObject* self, int index, PyObject* num)
{
    ((double*) ((carray_object*) self)->items)[index] = PyFloat_AsDouble(num);
}


static int set_item(carray_object* self, int index, PyObject* num)
{
    if(index >= 0 && index < self->size)
    {
        if(self->methods->check_type(num) == -1)
            return -1;
        self->methods->set_item((PyObject*) self, index, num);
        return 0;
    }
    PyErr_SetString(PyExc_IndexError, "index out of range");
    return -1;
}


static PyObject* get_long_item(PyObject* self, int index)
{
    return PyLong_FromLong(
        ((long*) ((carray_object*) self)->items)[index]
    );
}


static PyObject* get_double_item(PyObject* self, int index)
{
    return PyFloat_FromDouble(
        ((double*) ((carray_object*) self)->items)[index]
    );
}


static PyObject* get_item(carray_object* self, int index)
{
    if(index >= 0 && index < self->size)
    {
        PyObject* item = self->methods->get_item((PyObject*) self, index);
        Py_INCREF(item);
        return item;
    }
    PyErr_SetString(PyExc_IndexError, "index out of range");
    return NULL;
}


static void increase_capacity(carray_object* self)
{
    if(self->size >= self->capacity)
    {
        self->capacity = self->capacity * 2 + 1;
        self->items = PyMem_Realloc(
            self->items, self->capacity * self->t_size
        );
    }
}


static void reduce_capacity(carray_object* self)
{
    if(self->size <= self->capacity / 2)
    {
        self->capacity = self->size;
        self->items = PyMem_Realloc(
            self->items, self->capacity * self->t_size
        );
    }
}


static PyObject* carray_append(carray_object* self, PyObject* args)
{
    PyObject* num;
    if(!PyArg_ParseTuple(args, "O", &num)
       || self->methods->check_type(num) == -1)
        return NULL;
    increase_capacity(self);
    self->methods->set_item((PyObject*) self, (int) self->size, num);
    self->size++;
    Py_INCREF(Py_None);
    return Py_None;
}


static int get_index(size_t size, int index)
{
    if (index < 0)
        return (int) size + index;
    return index;
}


#define INSERT(type) static void insert_##type( \
    PyObject* self, int index, PyObject* num) \
{ \
    carray_object* c_self = (carray_object*) self; \
    memmove(&((type*) c_self->items)[index + 1], \
            &((type*) c_self->items)[index], \
            (c_self->size - index) * c_self->t_size); \
    set_##type##_item(self, index, num); \
    c_self->size++; \
}

INSERT(long)
INSERT(double)


static PyObject* carray_insert(carray_object* self, PyObject* args)
{
    int index;
    PyObject* num;
    if(!PyArg_ParseTuple(args, "nO", &index, &num)
       || self->methods->check_type(num) == -1)
        return NULL;
    index = get_index(self->size, index);
    if(index < 0)
        index = 0;
    else if(index > self->size)
        index = (int) self->size;
    increase_capacity(self);
    self->methods->insert((PyObject*) self, index, num);
    Py_INCREF(Py_None);
    return Py_None;
}


#define POP(type) static PyObject* pop_##type(PyObject* self, int index) \
{ \
    carray_object* c_self = (carray_object*) self; \
    PyObject* num = get_##type##_item(self, index); \
    memmove(&((type*) c_self->items)[index], \
            &((type*) c_self->items)[index + 1], \
            (c_self->size - index - 1) * c_self->t_size); \
    c_self->size--; \
    return num; \
}

POP(long)
POP(double)


static PyObject* carray_pop(carray_object* self, PyObject* args)
{
    int index = (int) self->size - 1;
    if(!PyArg_ParseTuple(args, "|n", &index))
        return NULL;
    index = get_index(self->size, index);
    if(index >= 0 && index < self->size)
    {
        PyObject* num = self->methods->pop((PyObject*) self, index);
        reduce_capacity(self);
        Py_INCREF(num);
        return num;
    }
    PyErr_SetString(PyExc_IndexError, "index out of range");
    return NULL;
}


static PyObject* carray_remove(carray_object* self, PyObject* args)
{
    PyObject* num;
    if(!PyArg_ParseTuple(args, "O", &num))
        return NULL;
    Py_INCREF(Py_None);
    if(!PyFloat_Check(num) && !PyLong_Check(num))
        return Py_None;
    int index = -1;
    for(int i = 0; i < self->size; i++)
        if(PyObject_RichCompareBool(
            num, self->methods->get_item((PyObject*) self, i), Py_EQ
        ))
        {
            index = i;
            break;
        }
    if(index != - 1)
    {
        self->methods->pop((PyObject*) self, index);
        reduce_capacity(self);
    }
    return Py_None;
}


#define GET_INFO(type) static PyObject* get_##type##_info() \
{ \
    return PyUnicode_FromString("carray<"#type">("); \
}

GET_INFO(long)
GET_INFO(double)


static PyObject* get_info(carray_object* self)
{
    PyObject* info = self->methods->get_type_info();
    for(int i = 0; i < self->size; i++)
    {
        info = PyUnicode_Concat(info, PyObject_Str(
            self->methods->get_item((PyObject*) self, i)
        ));
        if(i < self->size - 1)
            info = PyUnicode_Concat(info, PyUnicode_FromString(", "));
    }
    info = PyUnicode_Concat(info, PyUnicode_FromString(")"));
    Py_INCREF(info);
    return info;
}


static PyObject* get_sizeof(carray_object* self, PyObject* args)
{
    PyObject* size = PyLong_FromSize_t(self->capacity * self->t_size);
    Py_INCREF(size);
    return size;
}


static Py_ssize_t get_len(carray_object* self)
{
    return (Py_ssize_t) self->size;
}


static PyObject* carray_compare(carray_object* self, PyObject* other, int op)
{
    if(op != Py_EQ)
        return Py_NotImplemented;
    if(self->size != PySequence_Size(other))
        return Py_False;
    for(int i = 0; i < self->size; i++)
        if(!PyObject_RichCompareBool(
                self->methods->get_item((PyObject*) self, i),
                PySequence_GetItem(other, i), Py_EQ
            ))
            return Py_False;
    return Py_True;
}


static PyObject* carray_iter(carray_object* self)
{
    self->step = 0;
    Py_INCREF(self);
    return (PyObject*) self;
}


static PyObject* carray_next(carray_object* self)
{
    if(self->step < self->size)
    {
        int index = (int) self->step;
        self->step++;
        PyObject* item = self->methods->get_item((PyObject*) self, index);
        Py_INCREF(item);
        return item;
    }
    PyErr_SetString(PyExc_StopIteration, "");
    return NULL;
}


#define GET_TYPECODE(type) \
    PyUnicode_FromString(strcmp(#type, "long") == 0 ? "i" : "d")

#define REVERSED(type) static int reversed_##type( \
    PyObject* obj, PyObject* self, int size) \
{ \
    Py_TYPE(obj)->tp_init( \
        obj, PyTuple_Pack(1, GET_TYPECODE(type)), NULL \
    ); \
    if(!size) \
        return 0; \
    carray_object* c_obj = (carray_object*) obj; \
    carray_object* c_self = (carray_object*) self; \
    c_obj->items = PyMem_Malloc(size * c_obj->t_size); \
    ((type*) c_obj->items)[size / 2] = ((type*) c_self->items)[size / 2]; \
    for(int i = 0; i < size / 2; i++) \
    { \
        ((type*) c_obj->items)[i] = ((type*) c_self->items)[size - i - 1]; \
        ((type*) c_obj->items)[size - i - 1] = ((type*) c_self->items)[i]; \
    } \
    return 0; \
}

REVERSED(long)
REVERSED(double)


static PyObject* carray_reversed(carray_object* self, PyObject* args)
{
    carray_object* r_self = (carray_object*) Py_TYPE(self)->tp_new(
        Py_TYPE(self), NULL, NULL
    );
    self->methods->reversed(
        (PyObject*) r_self, (PyObject*) self, (int) self->size
    );
    r_self->size = self->size;
    r_self->capacity = self->capacity;
    return (PyObject*) r_self;
}


static object_methods type_methods[] = {
    {NULL, insert_long, pop_long, set_long_item,
     get_long_item, reversed_long, get_long_info, check_long},
    {NULL, insert_double, pop_double, set_double_item,
     get_double_item, reversed_double, get_double_info, check_double}
};


static PyMethodDef carray_methods[] = {
    {"__sizeof__", (PyCFunction) get_sizeof, METH_NOARGS, ""},
    {"__reversed__", (PyCFunction) carray_reversed, METH_NOARGS, ""},
    {"append", (PyCFunction) carray_append, METH_VARARGS, ""},
    {"insert", (PyCFunction) carray_insert, METH_VARARGS, ""},
    {"pop", (PyCFunction) carray_pop, METH_VARARGS, ""},
    {"remove", (PyCFunction) carray_remove, METH_VARARGS, ""},
    {NULL}
};


static PyObject* carray_new(PyTypeObject* type, PyObject* args, PyObject* kwds)
{
    carray_object* self = (carray_object*) type->tp_alloc(type, 0);
    if(self != NULL)
    {
        self->size = 0;
        self->capacity = 0;
        self->items = NULL;
    }
    Py_INCREF(self);
    return (PyObject*) self;
}


static int carray_init(carray_object* self, PyObject* args, PyObject* kwds)
{
    int typecode;
    PyObject* iterable = NULL;

    if(!PyArg_ParseTuple(args, "C|O", &typecode, &iterable))
        return -1;

    if(typecode == 'i')
    {
        self->t_size = sizeof(long);
        self->methods = &type_methods[0];
    }
    else if(typecode == 'd')
    {
        self->t_size = sizeof(double);
        self->methods = &type_methods[1];
    }
    else
    {
        PyErr_SetString(PyExc_ValueError, "incorrect data type");
        return -1;
    }
    Py_INCREF(self->methods);

    if(iterable)
    {
        self->size = PySequence_Size(iterable);
        if(self->size == -1)
        {
            PyErr_SetString(PyExc_TypeError, "argument 2 must be iterable");
            return -1;
        }
        self->capacity = self->size;
        self->items = PyMem_Malloc(self->capacity * self->t_size);
        for(int i = 0; i < self->size; i++)
            if(set_item(self, i, PySequence_GetItem(iterable, i)) == -1)
            {
                PyMem_Free(self->items);
                return -1;
            }
    }
    return 0;
}


static void carray_dealloc(carray_object* self)
{
    PyMem_Free(self->items);
    Py_DECREF(self->methods);
    Py_DECREF(self);
    Py_TYPE(self)->tp_free(self);
}


static PySequenceMethods carray_sequence_methods = {
    .sq_length = (lenfunc) get_len,
    .sq_ass_item = (ssizeobjargproc) set_item,
    .sq_item = (ssizeargfunc) get_item
};


static PyTypeObject carray_type = {
    PyVarObject_HEAD_INIT(NULL, 0)
    .tp_name = "carray.carray",
    .tp_basicsize = sizeof(carray_object),
    .tp_itemsize = 0,
    .tp_flags = Py_TPFLAGS_DEFAULT,
    .tp_new = carray_new,
    .tp_init = (initproc) carray_init,
    .tp_dealloc = (destructor) carray_dealloc,
    .tp_richcompare = (richcmpfunc) carray_compare,
    .tp_repr = (reprfunc) get_info,
    .tp_str = (reprfunc) get_info,
    .tp_iter = (getiterfunc) carray_iter,
    .tp_iternext = (iternextfunc) carray_next,
    .tp_methods = carray_methods,
    .tp_as_sequence = &carray_sequence_methods
};


static PyModuleDef carray_module = {
    PyModuleDef_HEAD_INIT,
    .m_name = "carray",
    .m_size = -1
};


PyMODINIT_FUNC PyInit_carray()
{
    if(PyType_Ready(&carray_type) < 0)
        return NULL;
    PyObject* module = PyModule_Create(&carray_module);
    if(module == NULL)
        return NULL;
    Py_INCREF(&carray_type);
    if(PyModule_AddObject(module, "carray", (PyObject*) &carray_type) < 0)
    {
        Py_DECREF(&carray_type);
        Py_DECREF(module);
        return NULL;
    }
    return module;
}
