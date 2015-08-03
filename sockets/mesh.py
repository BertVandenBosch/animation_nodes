import bpy
import bmesh
from .. base_types.socket import AnimationNodeSocket

class MeshSocket(bpy.types.NodeSocket, AnimationNodeSocket):
    bl_idname = "mn_MeshSocket"
    bl_label = "Mesh Socket"
    dataType = "Mesh"
    allowedInputTypes = ["Mesh"]
    drawColor = (0.1, 1.0, 0.1, 1)

    def drawInput(self, layout, node, text):
        layout.label(text)

    def getValue(self):
        return bmesh.new()

    def getCopyValueFunctionString(self):
        return "return value.copy()"