import bpy
import json
from . an_operator import AnimationNodeOperator
from .. preferences import getAnimationNodesVersion
from .. base_types.nodes.base_node import callSaveMethods

class ExportTemplate(bpy.types.Operator, AnimationNodeOperator):
    bl_idname = "an.export_template"
    bl_label = "Export Template"

    def execute(self, context):
        callSaveMethods()
        nodeTree = context.space_data.node_tree
        nodes = getSelectedNodes(nodeTree)
        jsonDict = jsonFromNodes(nodeTree, nodes)
        print(json.dumps(jsonDict, sort_keys = True, indent = 4))
        return {"FINISHED"}

def getSelectedNodes(nodeTree):
    return {node for node in nodeTree.nodes if node.select}

def jsonFromNodes(nodeTree, nodes):
    links = getLinksBetweenNodes(nodeTree, nodes)
    template = {
        "version" : getAnimationNodesVersion(),
        "nodes" : {},
        "links" : []
        }
    orderedNodes = list(nodes)
    for i, node in enumerate(orderedNodes):
        template["nodes"][i] = jsonFromNode(node)
    return template

def getLinksBetweenNodes(nodeTree, nodes):
    links = set()
    for link in nodeTree.links:
        if link.from_node in nodes and link.to_node in nodes:
            links.add(link)
    return links

def jsonFromNode(node):
    return {
        "location" : (node.location.x, node.location.y),
        "data" : jsonFromNodeData(node)
    }

def jsonFromNodeData(node):
    return {
        "bl_idname" : node.bl_idname,
        "name" : node.name,
        "properties" : jsonFromNodeProperties(node),
        "sockets" : {
            "inputs" :jsonFromNodeSockets(node.inputs),
            "outputs" : jsonFromNodeSockets(node.outputs)
        }
    }

def jsonFromNodeProperties(node):
    nodeProperties = {}
    for prop in node.bl_rna.properties:
        if prop.identifier not in ignoredNodeAttributes:
            if not doesPropertyEqualDefault(node, prop):
                nodeProperties[prop.identifier] = serializeProperty(node, prop)
    return nodeProperties

def serializeProperty(owner, prop):
    identifier = prop.identifier
    if prop.type in ("BOOLEAN", "INT", "FLOAT"):
        if prop.array_length <= 1:
            return getattr(owner, identifier)
        else:
            return tuple(getattr(owner, identifier))
    elif prop.type in ("STRING", "ENUM"):
        return getattr(owner, identifier)
    elif prop.type == "POINTER":
        return serializePointerProperty(owner, prop)
    elif prop.type == "COLLECTION":
        return serializeCollectionProperty(owner, prop)
    return "unknown type"

def serializeCollectionProperty(owner, prop):
    collectionType = getCollectionType(prop)
    elements = []
    for item in getattr(owner, prop.identifier):
        element = {}
        for _prop in collectionType.bl_rna.properties:
            if _prop.identifier == "rna_type": continue
            element[_prop.identifier] = serializeProperty(item, _prop)
        elements.append(element)
    return elements

def serializePointerProperty(owner, prop):
    pointerType = getPointerType(prop)
    data = {}
    _owner = getattr(owner, prop.identifier)
    for _prop in pointerType.bl_rna.properties:
        if _prop.identifier == "rna_type": continue
        data[_prop.identifier] = serializeProperty(_owner, _prop)
    return data

def getCollectionType(prop):
    if prop.srna is None:
        return getattr(bpy.types, prop.fixed_type.identifier)
    else:
        return getattr(bpy.types, prop.srna.identifier)

def getPointerType(prop):
    return getattr(bpy.types, prop.fixed_type.identifier)


def jsonFromNodeSockets(sockets):
    elements = []
    for socket in sockets:
        elements.append(jsonFromNodeSocket(socket))
    return elements

def jsonFromNodeSocket(socket):
    socketProperties = {}
    for prop in socket.bl_rna.properties:
        if prop.identifier not in ignoredSocketAttributes:
            if not doesPropertyEqualDefault(socket, prop):
                socketProperties[prop.identifier] = serializeProperty(socket, prop)
    return socketProperties

def doesPropertyEqualDefault(owner, prop):
    if prop.type in ("BOOLEAN", "INT", "FLOAT", "STRING", "ENUM"):
        if getattr(prop, "array_length", 1) <= 1:
            return getattr(owner, prop.identifier) == prop.default
        else:
            return tuple(getattr(owner, prop.identifier)) == tuple(prop.default_array)
    elif prop.type == "POINTER":
        _owner = getattr(owner, prop.identifier)
        for _prop in getPointerType(prop).bl_rna.properties:
            if _prop.identifier == "rna_type": continue
            if not doesPropertyEqualDefault(_owner, _prop):
                return False
        return True
    elif prop.type == "COLLECTION":
        return False

def getIgnoredNodeAttributes():
    attributes = {prop.identifier for prop in bpy.types.Node.bl_rna.properties}
    attributes.add("identifier")
    attributes.add("isAnimationNode")
    attributes.add("viewLocation")
    attributes.add("inInvalidNetwork")
    attributes.add("activeInputIndex")
    attributes.add("activeOutputIndex")
    return attributes

def getIgnoredSocketAttributes():
    attributes = {prop.identifier for prop in bpy.types.NodeSocket.bl_rna.properties}
    attributes.add("isAnimationNodeSocket")
    attributes.add("execution")
    attributes.add("show")
    attributes.remove("hide")
    return attributes

ignoredNodeAttributes = getIgnoredNodeAttributes()
ignoredSocketAttributes = getIgnoredSocketAttributes()
