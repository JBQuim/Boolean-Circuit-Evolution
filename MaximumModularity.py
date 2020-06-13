import numpy as np
from itertools import product
import time
import NetworkFunctions as NFunc
import EvolutionFunctions as GAFunc

# inputCount is the number of inputs the network takes
# length is the number of gates encoded in the genome
inputCount = 4
length = 13

# popSize is the number of individuals per generation
# simLength the maximum number of generations at which the simulation will be halted
# repetitions specifies how many runs are done
# epochLength specifies every how many generations the goal is switched
# period specifies every how many generations the internal state is printed to console
popSize = 1000
simLength = int(1E4)
repetitions = 10
period = 10

# to keep solutions small, a penalty of sizeParam is applied per gate above the cutoff
sizeParam = 0.1
cutoff = 11

# config is a dictionary with the probability of each mutation and the fraction of top fitness individuals considered
# elite. These pass on to the next generation unmutatated and then reproduce. The weights correspond, in order, to:
# no mutation - new gate - gate deletion - switch of inputs - crossover
config = dict([("mutation weights", [0.3, 0.05, 0.05, 0.25, 0.35]), ("elite fraction", 0.3)])

# this was used to find Qmax
# to preserve the connectivity of the network to the 0 output, a penalty is applied from departure from it
def modularityFitness(genome):
    modularity = NFunc.getModularity(genome)
    prec = sum(NFunc.getPrecursors(genome))
    penalty = max(11-prec, 0)

    return modularity-penalty

def averageModularity(population, fitnesses):
    mean = np.mean(fitnesses[fitnesses > 0])
    stdDev = np.std(fitnesses)
    return mean, stdDev


for j in range(repetitions):
    # initiate random generation of networks of a certain length
    generation = np.array([NFunc.randomNetwork(length, inputCount) for i in range(popSize)])

    # these will store the data collected throughout
    history = np.full(simLength, np.nan)
    modularities = np.full(simLength, np.nan)
    modularityStdDev = np.full(simLength, np.nan)
    winners = np.full((simLength, length * 2), np.nan)

    i = 0
    terminate = False
    t1 = time.perf_counter()
    for i in range(simLength):
        # here the fixed goal is specified, make sure to also change the destination of the data
        goal = modularityFitness
        generation, history[i], winners[i], (modularities[i], modularityStdDev[i]) = \
            GAFunc.runGeneration(generation, goal, averageModularity, config)

        # broadcast progress every period generations
        if i % period == 0:
            t2 = time.perf_counter()
            print("Run: " + str(j+1) + ". Generation " + str(i) + ".")
            print("Fitness: " + str(history[i]))
            print("Time per generation: " + str((t2 - t1) / period))
            t1 = time.perf_counter()

    # save all data to the appropiate files
    with open("Data/AdjustedModularityParams/Qmax/Networks/Networks" + str(j) + ".txt", "w") as outputFile:
        networkStrings = [",".join([str(k) for k in network]) for network in winners[:i]]
        outputString = "\n".join(networkStrings)
        outputFile.write(outputString)

    with open("Data/AdjustedModularityParams/Qmax/Fitnesses/Fitnesses" + str(j) + ".txt", "w") as outputFile:
        outputString = "\n".join([str(k) for k in history[:i]])
        outputFile.write(outputString)

    with open("Data/AdjustedModularityParams/Qmax/Modularity/Modularity" + str(j) + ".txt", "w") as outputFile:
        dataStrings = [str(value) + ", " + str(stdDev) for value, stdDev in zip(modularities, modularityStdDev)]
        outputString = "\n".join(dataStrings)
        outputFile.write(outputString)