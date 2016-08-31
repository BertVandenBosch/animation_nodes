import bpy
from bpy.props import *
from ... tree_info import keepNodeState
from ... base_types.node import AnimationNode

supportedDataTypes = ["Float", "Vector"]
dataTypeItems = [(s, s, "", "NONE", i) for i, s in enumerate(supportedDataTypes)]

class TestAssertionNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_TestAssertionNode"
    bl_label = "Test Assertion"

    def dataTypeChanged(self, context):
        self.recreateInputs()

    dataType = EnumProperty(name = "Data Type", items = dataTypeItems)
    assertionName = StringProperty(name = "Assertion Name", default = "Test")

    def create(self):
        self.recreateInputs()

    def draw(self, layout):
        col = layout.column()
        col.prop(self, "assertionName", text = "")
        col.prop(self, "dataType", text = "")

    @keepNodeState
    def recreateInputs(self):
        self.newInput(self.dataType, "A", "a")
        self.newInput(self.dataType, "B", "b")

    def log(self, success, message = ""):
        logAssertionResult(self.assertionName, success, message)

    def getExecutionFunctionName(self):
        return "execute_" + self.dataType

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

logFunction = None

def setLogger(function):
    global logFunction
    logFunction = function

def logAssertionResult(name, success, message):
    if logFunction is not None:
        logFunction(name, success, message)
