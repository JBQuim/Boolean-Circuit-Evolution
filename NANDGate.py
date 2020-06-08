import numpy as np
from itertools import product
import time
import NetworkFunctions as NFunc
import EvolutionFunctions as GAFunc

sizeParam = 0.1
inputCount = 4
cutoff = 12
length = 13
Qmax = 0.6339
Qrand = 0.3523
popSize = 1000
simLength = 100000
config = dict([("mutation weights", [0.3, 0.05, 0.05, 0.25, 0.35]), ("elite fraction", 0.3)])
inputs = np.array(list(product([1, 0], repeat=inputCount)))

def booleanFitness(genome, func, possibleInputs):
    # return the fitness of a network given by the % similarity across all inputs with func minus a size penalty
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

def averageModularity(population, fitnesses):
    examined = population[fitnesses==1]
    if len(examined)>0:
        mean = np.mean([NFunc.getModularity(specimen) for specimen in examined])
    else:
        mean = np.nan
    return mean

generation = np.array([NFunc.randomNetwork(length, inputCount) for i in range(popSize)])


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

    if i % 40 > 40:
        generation, history[i], winner, modularities[i] = GAFunc.runGeneration(generation, lambda x: booleanFitness(x, g2, inputs), averageModularity, config)
        if history[i] == 1:
            networkFile = open("Data/networks.txt", "a")
            networkFile.write("For G2: \n")
            networkFile.write(str(winner) + " \n")
    else:
        generation, history[i], winner, modularities[i] = GAFunc.runGeneration(generation, lambda x: booleanFitness(x, g1, inputs), averageModularity, config)
        if history[i] == 1:
            networkFile = open("Data/networks.txt", "a")
            networkFile.write("For G1: \n")
            networkFile.write(str(winner) + " \n")
