def getUniformRandom(seed, double min, double max):
    return uniformRandomNumber(seed % 0x7fffffff, min, max)

cdef int uniformRandomInteger(int x, int min, int max):
    return <int>uniformRandomNumber(x, min, <double>max + 0.9999999)

cdef double uniformRandomNumber(int x, double min, double max):
    '''Generate a random number between min and max using a seed'''
    x = (x<<13) ^ x
    return ((x * (x * x * 15731 + 789221) + 1376312589) & 0x7fffffff) / 2147483648.0 * (max - min) + min

cdef double randomNumber(int x):
    '''Generate a random number between -1 and 1 using a seed'''
    x = (x<<13) ^ x
    return 1.0 - ((x * (x * x * 15731 + 789221) + 1376312589) & 0x7fffffff) / 1073741824.0

cdef double randomNumber_Positive(int x):
    '''Generate a random number between 0 and 1 using a seed'''
    x = (x<<13) ^ x
    return ((x * (x * x * 15731 + 789221) + 1376312589) & 0x7fffffff) / 2147483648.0
