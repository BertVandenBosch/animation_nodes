import os
import bpy
from collections import defaultdict
from os.path import join, dirname, basename
from .. nodes.generic.test_assertion import setLogger
from .. update import updateEverything
from .. utils.nodes import getAnimationNodeTrees

class RunTestFiles(bpy.types.Operator):
    bl_idname = "an.run_test_files"
    bl_label = "Run Test Files"

    def execute(self, context):
        print("Start Tests")
        setLogger(self.log)
        for path in self.iterTestFilePaths():
            self.runTestFile(path)
        setLogger(None)
        bpy.ops.wm.read_homefile()
        print("Tests Finished")
        return {"FINISHED"}

    def iterTestFilePaths(self):
        directory = join(dirname(dirname(__file__)), "test_files")
        for root, dirs, files in os.walk(directory):
            for fileName in files:
                if fileName.endswith(".blend"):
                    yield join(root, fileName)

    def runTestFile(self, path):
        self.loadFile(path)
        updateEverything()
        for tree in getAnimationNodeTrees():
            tree.execute()

    def loadFile(self, path):
        bpy.ops.wm.open_mainfile(filepath = path)

    def log(self, name, success, message):
        result = "SUCCESS" if success else "FAILED"
        if message == "":
            print("{}: {}".format(result, name))
        else:
            print("{}: {}   -   {}".format(result, name, message))
