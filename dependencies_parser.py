# -*- coding: utf-8 -*-
# !/usr/bin/env python

# MIT License
#
# Copyright (c) 2017 Maxime Busy
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import os
import glob
import json
import inspect
import snakefood.find as snake_finder

FILES_EXTENSION_LIST = ['.py']

# Define the languages
UNDEFINED = -1
PYTHON    = 0
CPP       = 1

# define the object type
UNDEFINED     = -1
BASIC_CLASS   = 0
MOTHER_CLASS  = 1
NATIVE_MODULE = 2

CLASS_ID  = 0

def detectLanguage(pathToFile):
    """
    Detects the language of a code file (based on the extension)

    Parameters:
        pathToFile - The path to the file

    Returns:
        language - The language used in the file
    """

    try:
        assert isinstance(pathToFile, str)

    except AssertionError:
        return UNDEFINED

    if pathToFile.endswith('.py'):
        return PYTHON

    else:
        return UNDEFINED



def readFile(pathToFile):
    """
    Reads a text file and return its content

    Parameters:
        pathToFile - The path to the text file

    Returns:
        content - The content of the text file (list of lines)
    """

    content = list()

    try:
        assert detectLanguage(pathToFile) != UNDEFINED

        with open(pathToFile, 'r') as codeFile:
            content = codeFile.readlines()

    except AssertionError:
        pass

    return content



def exctractPythonClasses(pythonCode):
    """
    Exctracts the classes name from the python code

    Parameters:
        pythonCode - The python code text (list of lines)

    Returns:
        classesList - The list of the names of the python classes declared in
        the file
    """

    classesList       = list()
    isShortCommentary = False
    isLongCommentary  = False

    for line in pythonCode:
        if len(line.split('#')) > 1:
            isShortCommentary = True
        else:
            isShortCommentary = False

        if len(line.split('"""')) > 1\
        or len(line.split("'''")) > 1:
            isLongCommentary = not isLongCommentary

        if isShortCommentary or isLongCommentary:
            continue

        splittedLine = line.split('class ')

        if len(splittedLine) > 1:
            splittedLine = splittedLine[-1]
            className    = splittedLine.split(':')[0]
            classesList.append(className)

    return classesList



def extractProjectClasses(filePathList):
    """
    Extract the classes from the code files of the project. Computes the nodes
    of the futur display

    Parameters:
        filePathList - The list of file paths

    Returns:
        classesDict - Dictionnary of classes in the project, for instance :
        {   PYTHON: [
                {"fileClassA&B": ["ClassA", "ClassB"]},
                {"fileClassE&F": ["ClassE", "ClassF"]}
            ],

            CPP: [
                {"fileClassT&M": ["ClassT", "ClassM"]},
                {"fileClassR&N": ["ClassR", "ClassN"]}
            ]
        }
    """

    classes         = dict()
    classes[PYTHON] = list()
    classes[CPP]    = list()

    for path in filePathList:
        language = detectLanguage(path)
        code     = readFile(path)

        if language == PYTHON:
            try:
                assert isinstance(classes[PYTHON], list)

            except KeyError:
                classes[PYTHON] = list()

            except AssertionError:
                classes[PYTHON] = list()

            classes[PYTHON].append(
                {path: exctractPythonClasses(code)}
            )

        else:
            print path + " : language unknown"

    return classes



def extractProjectDependencies(classesDict):
    """
    Extract the dependencies of the project. Compute the values of the nodes and
    the edges of the futur display

    Parameters:
        classesDict - Classes dictionnary computed by method
        @extractProjectClasses

    Returns:
        dependencies - The project dependencies as a dictionnary, structured
        like the following example:

        {   PYTHON: {
                'ClassA': [
                        'ClassB',
                        'ClassK'
                    ],
                    'ClassAlpha': [
                        'Class32',
                        'module3'
                    ],
                    ...
            }
        }

        where ClassA depends on ClassB and classK, ClassAlpha depends on the
        Class32 and the module3
    """

    dependencies        = dict()
    dependenciesPython  = dict()
    classModulesDict    = dict()
    classModulesList    = list()
    nonClassModulesList = list()
    moduleClassNameConv = dict()

    # Fill classModulesDict
    for classDict in classesDict[PYTHON]:
        try:
            assert len(classDict.keys()) == 1

        except AssertionError:
            print "Several files " + classesDict.keys() + " for classes\
                declaration " + classesDict.values()
            continue

        pythonClassFile     = classDict.keys()[0]

        pythonClassModule   = convertModuleName(
            pythonClassFile,
            inspect.getmodulename(pythonClassFile)
        )

        dependencyFilesList = snake_finder.find_dependencies(
            pythonClassFile,
            verbose=False,
            process_pragmas=False)[0]

        pythonClassDependencyModules = list()

        for depFile in dependencyFilesList:
            depModuleName = convertModuleName(
                depFile,
                inspect.getmodulename(depFile)
            )

            if depModuleName is not None:
                pythonClassDependencyModules.append(depModuleName)

        for className in classDict.values()[0]:
            classModulesDict[className] = {
                "classModule"      : pythonClassModule,
                "dependencyModules": pythonClassDependencyModules
            }

    # Fill class modules list
    rawClassModulesList = list()

    for element in classModulesDict.values():
        rawClassModulesList.append(element["classModule"])

    for classModule in rawClassModulesList:
        if classModule not in classModulesList:
            classModulesList.append(classModule)

    # Fill non class modules list
    rawNonClassModulesList = list()

    for element in classModulesDict.values():
        for module in element["dependencyModules"]:
            if module not in classModulesList:
                rawNonClassModulesList.append(module)

    for nonClassModule in rawNonClassModulesList:
        if nonClassModule not in nonClassModulesList:
            nonClassModulesList.append(nonClassModule)

    # Fill module classname conversion dict
    for className, modulesDict in classModulesDict.items():
        moduleClassNameConv[modulesDict["classModule"]] = className

    # Compute the python dependencies
    for className, modulesDict in classModulesDict.items():
        dependenciesPython[className] = list()

        for depModule in modulesDict["dependencyModules"]:
            if depModule in classModulesList:
                dependenciesPython[className].append(
                    moduleClassNameConv[depModule]
                )
            else:
                dependenciesPython[className].append(depModule)

    for nonClassModule in nonClassModulesList:
        dependenciesPython[nonClassModule] = list()

    dependencies[PYTHON] = dependenciesPython
    return dependencies



def convertModuleName(pythonFile, pythonModule):
    """
    If the module is "__init__", changes the name of the module to an
    appropriate name. Warning, if the module name is None, will return None

    Parameters:
        pythonFile - The python file path corresponding to the module
        pythonModule - The name of the module

    Returns:
        pythonModule - The converted name of the module
    """

    if pythonModule == "__init__":
        if len(pythonFile.split("/")) > 1:
            pythonModule = pythonFile.split("/")[-2]
        elif len(pythonFile.split("\\")) > 1:
            pythonModule = pythonFile.split("\\")[-2]

    return pythonModule



def computeNodesAndEdges(dependencies):
    """
    From the dependencies of the project, compute the nodes and the edges to be
    displayed

    Parameters:
        dependencies - The dependencies of the project, for more informations,
        see @extractProjectDependencies

    Returns:
        nodesAndEdgesDict - The dict containing the nodes and edges of the
        project
    """
    global CLASS_ID

    nodesBackgroundColorDict = {PYTHON: '#97C2FC'}
    nodesBorderColorDict     = {BASIC_CLASS: '#2B7CE9'}
    nodesHighlightColorDict  = {PYTHON: {"background": '#D2E5FF'}}

    nodes             = list()
    edges             = list()
    nodesAndEdgesDict = dict()

    for language in dependencies.keys():
        for analysedClass in dependencies[language].keys():
            nodeDict = dict()
            nodeDict["id"]    = CLASS_ID
            nodeDict["value"] = 4 + len(dependencies[language][analysedClass])
            nodeDict["label"] = analysedClass
            nodeDict["group"] = language
            CLASS_ID         += 1

            nodeDict["color"]               = dict()
            nodeDict["color"]["background"] = nodesBackgroundColorDict[language]
            nodeDict["color"]["border"]     = nodesBorderColorDict[BASIC_CLASS]
            nodeDict["color"]["highlight"]  = nodesHighlightColorDict[language]

            nodes.append(nodeDict)

        for nodeDict in nodes:
            for dependencyClass in dependencies[language][nodeDict["label"]]:
                dependencyClassId = -1
                edgeDict          = dict()

                for nodeCheckId in nodes:
                    if nodeCheckId["label"] == dependencyClass:
                        dependencyClassId = nodeCheckId["id"]

                try:
                    assert dependencyClassId != -1

                except AssertionError:
                    continue

                edgeDict["from"]  = nodeDict["id"]
                edgeDict["to"]    = dependencyClassId
                edgeDict["value"] = 2

                edges.append(edgeDict)

    nodesAndEdgesDict["nodes"] = nodes
    nodesAndEdgesDict["edges"] = edges

    return nodesAndEdgesDict



def getProjectFiles(projectFolderPath):
    """
    Gets the file of a project

    Parameters:
        projectFolderPath - The path of the folder of the project

    Returns:
        projectFiles - The source files of the project
    """

    projectFiles = list()

    for path, subdirs, files in os.walk(projectFolderPath):
        for name in files:
            filePath         = os.path.join(path, name)
            _, fileExtension = os.path.splitext(filePath)

            if fileExtension in FILES_EXTENSION_LIST:
                projectFiles.append(filePath)

    return projectFiles



def dumpJson(dictionnary):
    """
    Dumps the data into a json

    Parameters:
        dictionnary - The dictionnary correpsonding to the data to be written in
        the JSON
    """

    with open('ressources/data.json', 'w') as jsonFile:
        json.dump(dictionnary, jsonFile)



# TODO : add specific modules in addition to the classes
# TODO : compute inheritance

def main():
    projectPath       = '../ARIIA'
    projectFiles      = getProjectFiles(projectPath)
    classesDict       = extractProjectClasses(projectFiles)
    dependencies      = extractProjectDependencies(classesDict)
    nodesAndEdgesDict = computeNodesAndEdges(dependencies)

    dumpJson(nodesAndEdgesDict)

if __name__ == "__main__":
    main()
