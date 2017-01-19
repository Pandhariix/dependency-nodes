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

FILES_EXTENSION_LIST = ['.py']

UNDEFINED = -1
PYTHON    = 0

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

    global CLASS_ID

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
            classDict    = {"id":CLASS_ID, "value":1, "label":className}
            CLASS_ID     += 1
            classesList.append(classDict)

    return classesList



def extractProjectClasses(filePathList):
    """
    Extract the classes from the code files of the project. Computes the nodes
    of the futur display

    Parameters:
        filePathList - The list of file paths

    Returns:
        classes - Dictionnary of classes in the project, for instance :
        {PYTHON: ["ClassA, ClassB"], CPP: ["ClassT, ClassM"]}
    """

    classes = dict()

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

            classes[PYTHON].extend(exctractPythonClasses(code))

        else:
            print path + " : language unknown"

    return classes



def extractProjectDependencies(filePathList):
    """
    Extract the dependencies of the project. Compute the values of the nodes and
    the edges of the futur display

    Parameters:
        filePathList - The list of file paths
    """



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




def main():
    projectPath  = '../ARIIA'
    projectFiles = getProjectFiles(projectPath)
    classesDict  = extractProjectClasses(projectFiles)

    print classesDict

    dataDict = dict()
    dataDict["nodes"] = classesDict[PYTHON]
    dumpJson(dataDict)

if __name__ == "__main__":
    main()
