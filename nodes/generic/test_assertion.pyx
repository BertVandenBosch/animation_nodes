import bpy
from bpy.props import *
from ... tree_info import keepNodeState
from ... utils.handlers import validCallback
from ... base_types.node import AnimationNode
from ... data_structures cimport MeshData, Vector3DList

supportedDataTypes = ["Float", "Vector", "Mesh Data"]
dataTypeItems = [(s, s, "", "NONE", i) for i, s in enumerate(supportedDataTypes)]

class TestAssertionNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_TestAssertionNode"
    bl_label = "Test Assertion"

    @validCallback
    def dataTypeChanged(self, context):
        self.recreateInputs()

    printResult = BoolProperty(name = "Print Result", default = False)

    assertionName = StringProperty(name = "Assertion Name", default = "Test")
    dataType = EnumProperty(name = "Data Type", items = dataTypeItems,
        update = dataTypeChanged)

    def create(self):
        self.recreateInputs()

    def draw(self, layout):
        col = layout.column()
        col.prop(self, "assertionName", text = "")
        col.prop(self, "dataType", text = "")

    def drawAdvanced(self, layout):
        layout.prop(self, "printResult")

    @keepNodeState
    def recreateInputs(self):
        self.inputs.clear()
        self.newInput(self.dataType, "A", "a")
        self.newInput(self.dataType, "B", "b")

    def log(self, success, message = ""):
        if self.printResult: print(self.assertionName, success, message)
        logAssertionResult(self.assertionName, success, message)

    def getExecutionFunctionName(self):
        return "execute_" + self.dataType.replace(" ", "")

    def execute_Float(self, a, b):
        if abs(a - b) < 0.00001:
            self.log(True)
        else:
            self.log(False, "{:.5f} != {:.5f}".format(a, b))

    def execute_Vector(self, a, b):
        if (abs(a.x - b.x) < 0.00001 and
            abs(a.y - b.y) < 0.00001 and
            abs(a.z - b.z) < 0.00001):
            self.log(True)
        else:
            self.log(False, "{} != {}".format(a, b))

    def execute_MeshData(self, MeshData a, MeshData b):
        if not self.equals_Vector3DList(a.vertices, b.vertices):
            self.log(False, "Different vertices")
            return
        if not (a.edges == b.edges):
            self.log(False, "Different edges")
            return
        if not (a.polygons == b.polygons):
            self.log(False, "Different polygons")
            return
        self.log(True)

    def equals_Vector3DList(self, Vector3DList a, Vector3DList b):
        if a.length != b.length: return False
        cdef Py_ssize_t i
        for i in range(a.length):
            if abs(a.data[i].x - b.data[i].x) >= 0.00001: return False
            if abs(a.data[i].y - b.data[i].y) >= 0.00001: return False
            if abs(a.data[i].z - b.data[i].z) >= 0.00001: return False
        return True


logFunction = None

def setLogger(function):
    global logFunction
    logFunction = function

def logAssertionResult(name, success, message):
    if logFunction is not None:
        logFunction(name, success, message)
