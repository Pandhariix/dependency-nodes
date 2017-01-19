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

UNDEFINED = -1
PYTHON    = 0


def detectLanguage(pathToFile):
    """
    Detects the language of a code file (based on the extension)

    Parameters:
        pathToFile - The path to the file

    Returns:
        language - The language used in the file
    """

    pathList  = pathToFile.split('.')

    try:
        assert len(pathList) > 0

    except AssertionError:
        return UNDEFINED

    extension = pathList[-1]

    if extension == 'py':
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

    with open(pathToFile, 'r') as codeFile:
        content = codeFile.readlines()

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

    classesList = list()

    for line in pythonCode:
        splittedLine = line.split('class ')

        if len(splittedLine) > 1:
            splittedLine = splittedLine[-1]
            className    = splittedLine.split(':')[0]

            classesList.append(className)

    return classesList



def extractProjectClasses(filePathList):
    """
    Extract the classes from the code files of the project

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




def main():
    path     = '/home/mbusy/Documents/apps/Hopias/python_structure/Hopias/brain.py'

    print extractProjectClasses([path])

if __name__ == "__main__":
    main()
