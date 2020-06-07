import numpy as np
from itertools import product
import time
import NetworkFunctions as NFunc
import EvolutionFunctions as GAFunc

sizeParam = 0.2
inputCount = 4
cutoff = 12
length = 13
Qmax = 0.6339
Qrand = 0.3523


popSize = 1000
simLength = 100000

def booleanFitness(genome, func):
    # return the fitness of a network given by the % similarity across all inputs with func minus a size penalty
    possibleInputs = list(product([1, 0], repeat=inputCount))
    requiredOutputs = [func(booleans) for booleans in possibleInputs]
    correct = np.equal(requiredOutputs, NFunc.truthTable(genome, possibleInputs))


    accuracy = np.count_nonzero(correct) / len(possibleInputs)
    sizePenalty = sizeParam * max(0, sum(NFunc.getPrecursors(genome)) - cutoff)

    return accuracy - sizePenalty

def g1(inputs):
    return inputs[0] ^ inputs[1] and inputs[2] ^ inputs[3]


def g2(inputs):
    return inputs[0] ^ inputs[1] or inputs[2] ^ inputs[3]

# this was used to find Qmax
# to preserve the connectivity of the network to the 0 output, a penalty is applied from departure from it
def modularityFitness(genome):
    modularity = NFunc.getModularity(genome)
    prec = sum(NFunc.getPrecursors(genome))
    penalty = max(11-prec,0)

    return modularity-penalty

generation = np.array([NFunc.randomNetwork(length) for i in range(popSize)])


t1 = time.clock()
history = np.full(simLength, np.nan)
modularities = np.full(simLength, np.nan)

i = 0
history[0] = 0
modularities[0] = 0
t0 = time.clock()
while i < simLength - 1:
    i += 1
    if i % 10 == 0 and i != 0:
        t2 = time.clock()
        print("Generations: " + str(i))
        print("Time per generation: " + str((t2 - t1) / 10))
        print("Fitness: " + str(history[i - 1]))
        data = open("Data/data.txt", "w")
        data.write(",".join([str(k) for k in history[:i]]))
        data.close()
        data = open("Data/data2.txt", "w")
        data.write(",".join([str(k) for k in modularities[:i]]))
        data.close()

        t1 = time.clock()

    if i % 40 < 40:
        generation, history[i], winner = GAFunc.runGeneration(generation, lambda x: booleanFitness(x, g2))
        if history[i] == 1:
            networkFile = open("Data/networks.txt", "a")
            networkFile.write("For G2: \n")
            networkFile.write(str(winner) + " \n")
    else:
        generation, history[i], winner = GAFunc.runGeneration(generation, lambda x: booleanFitness(x, g1))
        if history[i] == 1:
            networkFile = open("Data/networks.txt", "a")
            networkFile.write("For G1: \n")
            networkFile.write(str(winner) + " \n")
    modularities[i] = NFunc.adjustedModularity(winner, Qmax, Qrand)
