import cv2
import json
import math
import time
from NeuralFunctions import *
from NeuralEvolution import NeuralNetwork

# ANGLES
def Sin(val):
    val = math.radians(val)
    return Decimal(math.sin(val))


def Cos(val):
    val = math.radians(val)
    return Decimal(math.cos(val))


def RotMat(theta, mat):
    cosO = Cos(theta)
    sinO = Sin(theta)
    return MatMul([[cosO, sinO],
                   [-sinO, cosO]], mat)


def Divide(y, x):
    try:
        return Decimal(y / x)
    except ZeroDivisionError:
        return 1


# READING & WRITING
def Append2File(filename, detail):
    file = open(filename, 'a')
    file.writelines(json.dumps(detail) + NextLine)
    file.close()


def OpenFromFile(file_):
    file = open(file_, 'r')
    return json.loads(file.readline())


def SaveToFile(file_, data):
    file = open(file_, 'w')
    file.write(json.dumps(data))
    file.close()


def ReadGenomeFile(name):
    file = open(name, 'r')
    genomePool = json.loads(file.readline())
    file.close()
    cont = []
    for ev in genomePool:
        cont += [PythonJSONDumps(ev)]
    return cont


def ReadGenome(name):
    file = open(name, 'r')
    cont = file.readline()
    file.close()
    cont = json.loads(cont)
    return PythonJSONDumps(cont)

