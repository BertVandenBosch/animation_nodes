import bpy
import json
from bpy.props import *

class LoadTemplate(bpy.types.Operator):
    bl_idname = "an.load_template"
    bl_label = "Load Template"

    filepath = StringProperty(subtype = "FILE_PATH")

    @classmethod
    def poll(cls, context):
        return context.getActiveAnimationNodeTree() is not None

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {"RUNNING_MODAL"}

    def execute(self, context):
        with open(self.filepath, "r") as textFile:
            text = textFile.read()

        template = json.loads(text)
        createNodesFromTemplate(context.getActiveAnimationNodeTree(), template)
        return {"FINISHED"}

def createNodesFromTemplate(nodeTree, template):
    nodes = createNodes(nodeTree, template["nodes"])
    createLinks(nodeTree, nodes, template["links"])

def createNodes(nodeTree, nodesData):
    nodes = []
    for nodeData in nodesData:
        node = createNode(nodeTree, nodeData)
        nodes.append(node)
    return nodes

def createNode(nodeTree, nodeData):
    node = nodeTree.nodes.new(nodeData["bl_idname"])
    node.name = nodeData["name"]
    setProperties(node, nodeData["properties"])
    setSocketProperties(node.inputs, nodeData["sockets"]["inputs"])
    setSocketProperties(node.outputs, nodeData["sockets"]["outputs"])
    return node

def setSocketProperties(sockets, socketData):
    for socket, propertiesData in zip(sockets, socketData):
        setProperties(socket, propertiesData["properties"])

def createLinks(nodeTree, nodes, linksData):
    for linkData in linksData:
        createLink(nodeTree, nodes, linkData)

def createLink(nodeTree, nodes, linkData):
    fromSocket = nodes[linkData["from"]["node"]].outputs[linkData["from"]["socket"]]
    toSocket = nodes[linkData["to"]["node"]].inputs[linkData["to"]["socket"]]
    nodeTree.links.new(toSocket, fromSocket)

def setProperties(owner, propertiesData):
    baseTypes = (int, float, bool, str)
    for propName, propValue in propertiesData.items():
        if not hasattr(owner, propName): continue

        if isinstance(propValue, baseTypes):
            try: setattr(owner, propName, propValue)
            except: print("cannot set " + propName)
        elif isinstance(propValue, list):
            if all(isinstance(value, baseTypes) for value in propValue):
                try: setattr(owner, propName, propValue)
                except: print("cannot set " + propName)
            else:
                collection = getattr(owner, propName)
                for value in propValue:
                    item = collection.add()
                    setProperties(item, value)
        elif isinstance(propValue, dict):
            _owner = getattr(owner, propName)
            setProperties(_owner, propValue)
        else:
            raise Exception("unknown type")
