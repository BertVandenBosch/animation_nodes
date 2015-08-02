import bpy
from mathutils import *
from ... base_types.node import AnimationNode
from ... mn_execution import nodePropertyChanged, allowCompiling, forbidCompiling


class mn_DecomposeMatrix(bpy.types.Node, AnimationNode):
    bl_idname = "mn_DecomposeMatrix"
    bl_label = "Decompose Matrix"
    outputUseParameterName = "useOutput"
    isDetermined = True
    
    def init(self, context):
        forbidCompiling()
        self.inputs.new("mn_MatrixSocket", "Matrix")
        self.outputs.new("mn_VectorSocket", "Translation")
        self.outputs.new("mn_VectorSocket", "Rotation")
        self.outputs.new("mn_VectorSocket", "Scale")
        allowCompiling()
        
    def getInputSocketNames(self):
        return {"Matrix" : "matrix"}
    def getOutputSocketNames(self):
        return {"Translation" : "translation",
                "Rotation" : "rotation",
                "Scale" : "scale"}

    def useInLineExecution(self):
        return True
    def getInLineExecutionString(self, outputUse):
        codeLines = []
        if outputUse["Translation"]: codeLines.append("$translation$ = %matrix%.to_translation()")
        if outputUse["Rotation"]: codeLines.append("$rotation$ = mathutils.Vector((%matrix%.to_euler()))")
        if outputUse["Scale"]: codeLines.append("$scale$ = %matrix%.to_scale()")
        return "\n".join(codeLines)
    def getModuleList(self):
        return ["mathutils"]