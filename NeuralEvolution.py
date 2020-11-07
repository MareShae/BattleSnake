"""
General Information:
It starts out with the simple Input & Output Layers.
Random mutations occur for the given genome and they are tested with the fitness function.
The best out of the mutations get to further develop/mutate their genes and progress.
All Neurons can mutate. Given a Neuron & its Links it can:
      create a new link to another existing neuron
      modify, i.e increase or decrease, the weights of a link
      create a new neuron in that link

This Version:
Combines all hidden layers into one.
Total number of hidden neurons is fixed.
Simplifies Propagation.
Simplifies Crossover.
"""
from NeuralFunctions import *


# NEURAL NETWORK
class NeuralNetwork:
    def __init__(self, genome):
        self.genome = deepcopy(genome)  # Gene will be updated directly

        self.shape = self.genome['shape']
        self.Neuron = self.genome['neuron']

        self.Layer = self.genome['layer']
        self.input = self.Layer['input']  # ...
        self.output = self.Layer['output']  # ...
        self.hidden = self.Layer['hidden']  # Neuron Detail

    # FEEDING THE NETWORK
    def ReadOutput(self):
        return [self.Neuron[Neuron_UID]['activationValue'] for Neuron_UID in self.output]

    def Propagate(self, Neuron):
        for endUID in Neuron['synapse']:
            # Check the status of the Synapse
            linkWeight = Neuron['synapse'][endUID]  # Weight of the StructLink
            linkOutput = Multiply(linkWeight, Neuron['activationValue'])  # Apply Weight
            UpdateNeuron(self.Neuron[endUID], linkOutput)  # Update the Linked Neuron

    def ForwardPass(self, image: list):
        for index in range(len(image)):
            if index >= len(self.input):
                break
            Neuron_UID = self.input[index]
            self.Neuron[Neuron_UID]['neuronValue'] = image[index]

        # Propagate Input Layers
        for Neuron_UID in self.input:
            Neuron = self.Neuron[Neuron_UID]
            ActivateNeuron(Neuron, ActivationFn=TanH)
            self.Propagate(self.Neuron[Neuron_UID])
        # Propagate Hidden Layers
        for Neuron_UID in self.hidden:
            Neuron = self.Neuron[Neuron_UID]
            ActivateNeuron(Neuron, ActivationFn=TanH)
            self.Propagate(Neuron)
        # Propagate Output Layers
        for Neuron_UID in self.output:
            Neuron = self.Neuron[Neuron_UID]
            ActivateNeuron(Neuron)
            self.Propagate(Neuron)

    # EVOLVING THE NETWORK
    def Clone(self):  # Create a child network
        MutateType = [self.LinkMutate,
                      self.DeLinkMutate,
                      self.WeightMutate]
        if len(self.hidden) < self.shape[2]:
            MutateType += [self.NeuronMutate]
        Mutate = Choice(MutateType)
        return Mutate()

    def LinkMutate(self):
        # LINK Mutation: Creating a StructLink between two Neuron
        childGenome = deepcopy(self.genome)  # Copy parent genome
        childLayer, childNeuron = childGenome['layer'], childGenome['neuron']

        Layer1 = childLayer[Choice(['input', 'hidden', 'output'])]
        Layer2 = childLayer[Choice(['input', 'hidden', 'output'])]
        if Layer1 and Layer2:
            NUID1, NUID2 = Choice(Layer1), Choice(Layer2)
            if NUID2 not in childNeuron[NUID1]['synapse']:
                StructLink(childGenome, NUID1, NUID2, Random())  # StructLink both Neuron
        return childGenome

    def DeLinkMutate(self):
        # DeLINK Mutation: Modify the StructLink Status
        childGenome = deepcopy(self.genome)  # Copy parent genome
        childLayer, childNeuron = childGenome['layer'], childGenome['neuron']

        Layer = childLayer[Choice(['input', 'hidden', 'output'])]
        if Layer:
            NUID = Choice(Layer)
            Neuron = childNeuron[NUID]  # The Neuron
            synapseUID = list(Neuron['synapse'].keys())
            if synapseUID:
                RemoveLink(childGenome, NUID, Choice(synapseUID))
        return childGenome

    def WeightMutate(self):
        # WEIGHT Mutation: Modify the weights
        childGenome = deepcopy(self.genome)  # Copy parent genome
        childLayer, childNeuron = childGenome['layer'], childGenome['neuron']

        Layer = childLayer[Choice(['input', 'hidden', 'output'])]
        if Layer:
            Neuron = childNeuron[Choice(Layer)]  # The Neuron
            synapseUID = list(Neuron['synapse'].keys())  # The dict keys: UID
            if synapseUID:
                endUID = Choice(synapseUID)
                Neuron['synapse'][endUID] += Multiply(0.01, Random())  # Update the Synapse weight
        return childGenome

    def NeuronMutate(self):
        # NEURON Mutation: Neuron between links
        childGenome = deepcopy(self.genome)  # Copy parent genome
        childLayer, childNeuron = childGenome['layer'], childGenome['neuron']

        Layer = childLayer[Choice(['input', 'hidden', 'output'])]
        if Layer:
            NUID1 = Choice(Layer)
            Neuron = childNeuron[NUID1]  # The Neuron
            synapseUID = list(Neuron['synapse'].keys())
            if synapseUID:
                NUID2 = Choice(synapseUID)
                NUIDmid = len(childNeuron) + 1

                childLayer['hidden'] += [NUIDmid]
                weight = Neuron['synapse'][NUID2]
                childNeuron[NUIDmid] = StructNeuron()
                RemoveLink(childGenome, NUID1, NUID2)
                StructLink(childGenome, NUID1, NUIDmid, 1)
                StructLink(childGenome, NUIDmid, NUID2, weight)
        return childGenome


'''
# TESTING THE NETWORK
gen = 1
maxGenomes = 200
remnantGenomes = 25

GenomePool = []
GenomePoolScore = []
for _ in range(maxGenomes):
    GenomePool.append(StructGenome((14, 4, 4)))
expected = numpy.array([0.45, 0.29, 0.11, 0.53])
while True:
    for genome in GenomePool:  # Run
        Net = NeuralNetwork(genome)
        Net.ForwardPass([0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 0.11, 0.12, 0.13, 0.14])
        predicted = numpy.array(Net.ReadOutput())
        error = Cost(expected, predicted)
        GenomePoolScore.append(error)
    bestScore = min(GenomePoolScore)
    print('Gen:', gen)
    print('Min Error:', bestScore)

    # CHILD Generation: Selection, CrossOver, Mutation
    gen += 1
    # Sort the genes by fitness descending & remove a %
    for x1 in range(maxGenomes):
        for x2 in range(maxGenomes):
            if GenomePoolScore[x1] < GenomePoolScore[x2]:
                Swap(GenomePool, x1, x2)  # Swap genome
                Swap(GenomePoolScore, x1, x2)  # Swap fitness
    GenomePool = GenomePool[0: remnantGenomes]  # Eliminate Genomes
    if bestScore == 0.0:
        GenomePoolScore = GenomePoolScore[0: remnantGenomes]  # Eliminate Scores
        print(GenomePool[0])
        break

    # Reproduction between 2 sets of genes
    crossGenomePool = []
    for x in range(len(GenomePool)-1):
        crossGenomePool.append(CrossOver(GenomePool[x],
                                         GenomePool[x+1]))

    # Modify the Links, Weights or Neurons
    x = 0
    GenomePool = []
    GenomePoolScore = []
    while len(GenomePool) < maxGenomes:
        Net = NeuralNetwork(crossGenomePool[x])
        childGenome = Net.Clone()
        if childGenome and childGenome not in GenomePool:
            GenomePool += [childGenome]
        x += 1
        if x >= len(crossGenomePool):
            x = 0
# '''
