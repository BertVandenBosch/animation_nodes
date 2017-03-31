import bpy
import json
from bpy.props import *
from . an_operator import AnimationNodeOperator
from .. preferences import getAnimationNodesVersion
from .. base_types.nodes.base_node import callSaveMethods

class ExportTemplate(bpy.types.Operator, AnimationNodeOperator):
    bl_idname = "an.export_template"
    bl_label = "Export Template"

    filepath = StringProperty(subtype = "FILE_PATH")
    filename = StringProperty()

    def invoke(self, context, event):
        self.filename = "template.json"
        context.window_manager.fileselect_add(self)
        return {"RUNNING_MODAL"}

    def execute(self, context):
        callSaveMethods()
        nodeTree = context.getActiveAnimationNodeTree()
        nodes = getSelectedNodes(nodeTree)
        template = createTemplateJson(nodeTree, nodes)
        text = json.dumps(template, sort_keys = True, indent = 4)

        with open(self.filepath, "w") as textFile:
            textFile.write(text)

        return {"FINISHED"}

def getSelectedNodes(nodeTree):
    return {node for node in nodeTree.nodes if node.select}

def createTemplateJson(nodeTree, nodes):
    links = getLinksBetweenNodes(nodeTree, nodes)
    orderedNodes = list(nodes)
    template = {
        "version" : getAnimationNodesVersion(),
        "nodes" : jsonFromNodes(orderedNodes),
        "links" : jsonFromLinks(links, orderedNodes)
        }

    return template

def getLinksBetweenNodes(nodeTree, nodes):
    links = set()
    for link in nodeTree.links:
        if link.from_node in nodes and link.to_node in nodes:
            links.add(link)
    return links

def jsonFromNodes(nodes):
    data = []
    for i, node in enumerate(nodes):
        data.append(jsonFromNode(node))
    return data

def jsonFromNode(node):
    return {
        "bl_idname" : node.bl_idname,
        "name" : node.name,
        "properties" : jsonFromNodeProperties(node),
        "sockets" : {
            "inputs" :jsonFromNodeSockets(node, node.inputs),
            "outputs" : jsonFromNodeSockets(node, node.outputs)
        }
    }

def jsonFromNodeProperties(node):
    nodeProperties = {}
    for prop in node.bl_rna.properties:
        if prop.identifier not in ignoredNodeAttributes:
            nodeProperties[prop.identifier] = serializeProperty(node, prop)
    return nodeProperties

def serializeProperty(owner, prop, skipDefaultSubProps = False):
    identifier = prop.identifier
    if prop.type in ("BOOLEAN", "INT", "FLOAT"):
        if prop.array_length <= 1:
            return getattr(owner, identifier)
        else:
            return tuple(getattr(owner, identifier))
    elif prop.type in ("STRING", "ENUM"):
        return getattr(owner, identifier)
    elif prop.type == "POINTER":
        return serializePointerProperty(owner, prop, skipDefaultSubProps)
    elif prop.type == "COLLECTION":
        return serializeCollectionProperty(owner, prop, skipDefaultSubProps)
    return "unknown type"

def serializeCollectionProperty(owner, prop, skipDefaults = False):
    collectionType = getCollectionType(prop)
    elements = []
    for item in getattr(owner, prop.identifier):
        element = {}
        for _prop in collectionType.bl_rna.properties:
            if _prop.identifier == "rna_type": continue
            if skipDefaults and doesPropertyEqualDefault(item, _prop): continue
            element[_prop.identifier] = serializeProperty(item, _prop, skipDefaults)
        elements.append(element)
    return elements

def serializePointerProperty(owner, prop, skipDefaults = False):
    pointerType = getPointerType(prop)
    data = {}
    _owner = getattr(owner, prop.identifier)
    for _prop in pointerType.bl_rna.properties:
        if _prop.identifier == "rna_type": continue
        if skipDefaults and doesPropertyEqualDefault(_owner, _prop): continue
        data[_prop.identifier] = serializeProperty(_owner, _prop, skipDefaults)
    return data

def getCollectionType(prop):
    if prop.srna is None:
        return getattr(bpy.types, prop.fixed_type.identifier)
    else:
        return getattr(bpy.types, prop.srna.identifier)

def getPointerType(prop):
    return getattr(bpy.types, prop.fixed_type.identifier)


def jsonFromNodeSockets(node, sockets):
    elements = []
    for socket in sockets:
        elements.append(jsonFromNodeSocket(node, socket))
    return elements

def jsonFromNodeSocket(node, socket):
    propNames = node.getUsedSocketProperties()
    return {
        "bl_idname" : socket.bl_idname,
        "identifier" : socket.identifier,
        "value" : socket.getProperty(),
        "properties" : jsonFromSocketProperties(socket, propNames)
    }

def jsonFromSocketProperties(socket, propNames):
    socketProperties = {}
    for prop in socket.bl_rna.properties:
        if prop.identifier in propNames:
            socketProperties[prop.identifier] = serializeProperty(socket, prop, True)
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

def jsonFromLinks(links, nodes):
    indexByNode = {node : i for i, node in enumerate(nodes)}
    data = []
    for link in links:
        data.append(jsonFromLink(link, indexByNode))
    return data

def jsonFromLink(link, indexByNode):
    return {
        "from" : {
            "node" : indexByNode[link.from_node],
            "socket" : list(link.from_node.outputs).index(link.from_socket)
        },
        "to" : {
            "node" : indexByNode[link.to_node],
            "socket" : list(link.to_node.inputs).index(link.to_socket)
        }
    }


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
