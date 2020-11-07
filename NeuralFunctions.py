import numpy
import random
from math import exp
from copy import deepcopy

# STATIC FUNCTIONS
def Round(val):
    return int(round(val))


def RoundList(image):
    reImage = []
    for val in image:
        reImage.append(Round(val))
    return reImage


def Decimal(value, decimalPoints=5):
    value = format(value, '.' + str(decimalPoints) + 'f')
    return float(value)


# https://stackoverflow.com/questions/17099556/why-do-int-keys-of-a-python-dict-turn-into-strings-when-using-json-dumps
def PythonJSONDumps(json_data):
    correctedDict = {}
    for key, value in json_data.items():
        if isinstance(value, list):
            value = [PythonJSONDumps(item) if isinstance(item, dict) else item for item in value]
        elif isinstance(value, dict):
            value = PythonJSONDumps(value)
        try:
            key = int(key)
        except ValueError:
            pass
        correctedDict[key] = value

    return correctedDict


# ARRAY FUNCTIONS
def Array(image):  # Make sure results are always in FLOAT
    return numpy.array(image, dtype=float)


def Cost(predicted, expected, d_P=5):
    cost = sum(((expected - predicted) ** 2) / len(predicted))
    return Decimal(cost, d_P)


def MatMul(weight, image):
    mul = []
    row2 = len(image)
    row1, col1 = len(weight), len(weight[0])
    # R1 must be EQUAL TO C2
    if col1 == row2:
        for r1 in range(row1):
            rSum = 0
            for c1 in range(col1):
                rSum += weight[r1][c1] * image[c1]
            mul += [Decimal(rSum)]
    return mul


# ACTIVATION FUNCTIONS
def Sigmoid(value, d_P=5):
    return Decimal(1 / (1 + exp(-value)), d_P)


def TanH(value, d_P=5):
    exponential = exp(2 * value)
    return Decimal((exponential - 1) / (exponential + 1), d_P)


# ARITHMETIC FUNCTIONS
def Add(values, d_P=5):
    return Decimal(sum(values), d_P)


def Multiply(*args, d_P=5):
    multiplied = 1
    for value in args:
        multiplied *= value
    return Decimal(multiplied, d_P)


# RANDOM FUNCTIONS
def Choice(sequence):
    return random.choice(sequence)


def Random(start=-1, end=1, d_P=5):
    return Decimal(random.uniform(start, end), d_P)


def RandInt(start, end):
    if start == end:
        return start
    elif start > end:
        return
    return random.randint(start, end)


def Swap(sequence: list, x1: int, x2: int):
    temp = sequence[x1]
    sequence[x1] = sequence[x2]
    sequence[x2] = temp


# CONSTRUCTING A GENOME
def RemoveLink(genome: dict, startUID: int, endUID: int):
    genome['gene'].remove([startUID, endUID])
    genome['neuron'][startUID]['synapse'].pop(endUID)


def StructLink(genome: dict, startUID: int, endUID: int, weight):
    genome['gene'].append([startUID, endUID])
    genome['neuron'][startUID]['synapse'][endUID] = weight


def StructNeuron():
    return {'synapse': {},  # Takes the neurons it is linked to
            'neuronValue': 0,  # Value of the neuron before activation
            'activationValue': 0  # Value of the neuron after activation
            }


def StructGenome(shape):  # I, O, H Shape
    Neuron, neuronUID = {}, 1
    input_, output_, hidden_ = [], [], []
    for _ in range(0, shape[0]):  # Input
        input_.append(neuronUID)
        Neuron[neuronUID] = StructNeuron()
        neuronUID += 1
    for _ in range(0, shape[1]):  # Output
        output_.append(neuronUID)
        Neuron[neuronUID] = StructNeuron()
        neuronUID += 1
    return {'gene': [],  # Genome Links
            'shape': shape,  # Input, Output
            'neuron': Neuron,  # Genome Neuron
            'layer': {'input': input_,
                      'output': output_,
                      'hidden': hidden_}  # Genome Layers
            }


# NEURON
def UpdateNeuron(Neuron, value):
    Neuron['neuronValue'] = Add([value, Neuron['neuronValue']])


def ActivateNeuron(Neuron, ActivationFn=Sigmoid):
    Neuron['activationValue'] = ActivationFn(Neuron['neuronValue'])
    Neuron['neuronValue'] = 0


# REPRODUCTION
def CrossOver(parent1: dict, parent2: dict):
    # CROSSOVER: New Gene will be a combination of both parents
    childGenome = StructGenome(parent1['shape'])
    childLayer, childNeuron = childGenome['layer'], childGenome['neuron']
    hiddenP1, hiddenP2 = parent1['layer']['hidden'], parent2['layer']['hidden']
    childHidden = hiddenP1 if len(hiddenP1) >= len(hiddenP2) else hiddenP2

    for NUID in childHidden:
        childLayer['hidden'] += [NUID]
        childNeuron[NUID] = StructNeuron()
    geneP1, geneP2 = parent1['gene'], parent2['gene']
    neuronP1, neuronP2 = parent1['neuron'], parent2['neuron']

    # Align Parent Genes assuming Parent1 has the superior genome
    inherited = geneP1.copy()  # Parent1 + Excess
    for gene in geneP2:
        if gene not in geneP1:
            inherited.append(gene)  # Parent2 Excess
    inherited.sort()
    for NUID1, NUID2 in inherited:
        if [NUID1, NUID2] in geneP1 and [NUID1, NUID2] in geneP2:
            weight = Choice([neuronP1[NUID1]['synapse'][NUID2],
                             neuronP2[NUID1]['synapse'][NUID2]])
        elif [NUID1, NUID2] in geneP1:
            weight = neuronP1[NUID1]['synapse'][NUID2]
        elif [NUID1, NUID2] in geneP2:
            weight = neuronP2[NUID1]['synapse'][NUID2]
        # StructLink both Neurons in Child Gene
        StructLink(childGenome, NUID1, NUID2, weight)
    return childGenome
