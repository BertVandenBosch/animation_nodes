import bpy
from .... base_types.node import AnimationNode
from .... algorithms.mesh_generation import box

class BoxMeshNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_BoxMeshNode"
    bl_label = "Box Mesh"

    def create(self):
        self.newInput("Float", "Width", "width", value = 2)
        self.newInput("Float", "Length", "length", value = 2)
        self.newInput("Float", "Height", "height", value = 2)
        self.newInput("Integer", "X Divisions", "xDivisions", value = 2, minValue = 2)
        self.newInput("Integer", "Y Divisions", "yDivisions", value = 2, minValue = 2)
        self.newInput("Integer", "Z Divisions", "zDivisions", value = 2, minValue = 2)

        self.newOutput("Vector List", "Vertices", "vertices")
        self.newOutput("Edge Indices List", "Edge Indices", "edgeIndices")
        self.newOutput("Polygon Indices List", "Polygon Indices", "polygonIndices")

    def getExecutionCode(self):
        isLinked = self.getLinkedOutputsDict()
        yield "_xDivisions =  max(xDivisions, 2)"
        yield "_yDivisions =  max(yDivisions, 2)"
        yield "_zDivisions =  max(zDivisions, 2)"
        if isLinked["vertices"]:
            yield "vertices = AN.algorithms.mesh_generation.box.vertices("
            yield "    width, length, height, _xDivisions, _yDivisions, _zDivisions)"
        if isLinked["edgeIndices"]:
            yield "edgeIndices = AN.algorithms.mesh_generation.box.edges("
            yield "    _xDivisions, _yDivisions, _zDivisions)"
