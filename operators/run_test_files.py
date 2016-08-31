import os
import bpy
from collections import defaultdict
from os.path import join, dirname, basename, relpath
from .. nodes.generic.test_assertion import setLogger
from .. update import updateEverything
from .. utils.nodes import getAnimationNodeTrees

class RunTestFiles(bpy.types.Operator):
    bl_idname = "an.run_test_files"
    bl_label = "Run Animation Nodes Test Files"

    def execute(self, context):
        print("Start Tests")

        self.fails = 0
        self.successes = 0
        self.failedTests = []
        files = list(self.iterTestFilePaths())
        self.fileAmount = len(files)

        setLogger(self.log)
        for path in files:
            self.runTestFile(path)
        setLogger(None)

        bpy.ops.wm.read_homefile()
        print("Tests Finished")
        self.printFinalResult()
        return {"FINISHED"}

    def iterTestFilePaths(self):
        directory = self.getTestFileDirectory()
        if not os.path.exists(directory):
            print("Directory with test files does not exist")
            return
        for root, dirs, files in os.walk(self.getTestFileDirectory()):
            for fileName in files:
                if fileName.endswith(".blend"):
                    yield join(root, fileName)

    def getTestFileDirectory(self):
        return join(dirname(dirname(__file__)), "test_files")

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

        if success: self.successes += 1
        else:
            self.fails += 1
            self.failedTests.append((
                relpath(bpy.data.filepath, self.getTestFileDirectory()),
                name, message))

    def printFinalResult(self):
        print("\n" * 2)
        print("Fails: {}".format(self.fails))
        print("Tested Files: {}".format(self.fileAmount))
        print("Tested Assertions: {}\n".format(self.fails + self.successes))

        if self.fails > 0:
            print("SOME TESTS FAILED:")
            for fileName, testName, message in self.failedTests:
                if message != "": message = "    -    " + message
                print("  {}: {}{}".format(fileName, testName, message))
