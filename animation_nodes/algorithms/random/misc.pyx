import random
from mathutils import Color
from . numbers cimport randomNumber

def getRandomColor(seed = None, hue = None, saturation = None, value = None):
    if seed is None: random.seed()
    else: random.seed(seed)

    if hue is None: hue = random.random()
    if saturation is None: saturation = random.random()
    if value is None: value = random.random()

    color = Color()
    color.hsv = hue, saturation, value
    return color

def getRandomNumberTuple(seed, int size, double scale):
    cdef int _seed = seed % 0x7fffffff
    cdef int i
    _seed *= 23412
    return tuple(randomNumber(_seed + i) * scale for i in range(size))
