# it is important that the compiler does not add padding here
cdef struct Vector3:
    float x, y, z

cdef float lengthVec3(Vector3* v) nogil
cdef void scaleVec3(Vector3* v, float factor) nogil
cdef void addVec3(Vector3* target, Vector3* a, Vector3* b) nogil
cdef void subVec3(Vector3* target, Vector3* a, Vector3* b) nogil
cdef void mixVec3(Vector3* target, Vector3* a, Vector3* b, float factor) nogil
cdef void crossVec3(Vector3* result, Vector3* a, Vector3* b) nogil
cdef float dotVec3(Vector3* a, Vector3* b) nogil

cdef void normalizeVec3(Vector3* v) nogil
cdef float distanceVec3(Vector3* a, Vector3* b) nogil
cdef float distanceSquaredVec3(Vector3* a, Vector3* b) nogil
