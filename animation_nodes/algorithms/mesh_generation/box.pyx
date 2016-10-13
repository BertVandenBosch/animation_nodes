from ... data_structures cimport Vector3DList, EdgeIndicesList, PolygonIndicesList

# Vertices
############################################

def vertices(float width, float length, float height,
             int xDivisions, int yDivisions, int zDivisions):
    assert xDivisions >= 2
    assert yDivisions >= 2
    assert zDivisions >= 2

    cdef:
        int amount = 2 * xDivisions * yDivisions + 2 * (xDivisions + yDivisions - 2) * (zDivisions - 2)
        Vector3DList output = Vector3DList(length = amount)
        int offset = 0
        int x, y, z
        float xOffset = width / 2.0
        float yOffset = length / 2.0
        float zOffset = height / 2.0
        float xStep = width / <float>(xDivisions - 1)
        float yStep = length / <float>(yDivisions - 1)
        float zStep = height / <float>(zDivisions - 1)

    # -Z Direction
    for x in range(xDivisions):
        for y in range(yDivisions):
            output.data[offset].x = x * xStep - xOffset
            output.data[offset].y = y * yStep - yOffset
            output.data[offset].z = -zOffset
            offset += 1

    # Z Direction
    for x in range(xDivisions):
        for y in range(yDivisions):
            output.data[offset].x = x * xStep - xOffset
            output.data[offset].y = y * yStep - yOffset
            output.data[offset].z = zOffset
            offset += 1

    # Y Direction
    for x in range(xDivisions):
        for z in range(1, zDivisions - 1):
            output.data[offset].x = x * xStep - xOffset
            output.data[offset].y = yOffset
            output.data[offset].z = z * zStep - zOffset
            offset += 1

    # -Y Direction
    for x in range(xDivisions):
        for z in range(1, zDivisions - 1):
            output.data[offset].x = x * xStep - xOffset
            output.data[offset].y = -yOffset
            output.data[offset].z = z * zStep - zOffset
            offset += 1

    # X Direction
    for y in range(1, yDivisions - 1):
        for z in range(1, zDivisions - 1):
            output.data[offset].x = xOffset
            output.data[offset].y = y * yStep - yOffset
            output.data[offset].z = z * zStep - zOffset
            offset += 1

    # -X Direction
    for y in range(1, yDivisions - 1):
        for z in range(1, zDivisions - 1):
            output.data[offset].x = -xOffset
            output.data[offset].y = y * yStep - yOffset
            output.data[offset].z = z * zStep - zOffset
            offset += 1

    return output


# Edges
############################################

def edges(int xDivisions, int yDivisions, int zDivisions):
    assert xDivisions >= 2
    assert yDivisions >= 2
    assert zDivisions >= 2

    cdef:
        int amount = (2 * (2 * xDivisions * yDivisions - xDivisions - yDivisions) +
                      (zDivisions - 1) * (2 * xDivisions + 2 * (yDivisions - 2)) +
                      (zDivisions - 2) * (2 * (xDivisions - 1) + 2 * (yDivisions - 1)))
        EdgeIndicesList edges = EdgeIndicesList(length = amount)
        int offset



    return edges
