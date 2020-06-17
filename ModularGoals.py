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
# consecutiveEpochs is the number of consecutive epochs ending in a perfect solution before terminating the sim
popSize = 1000
simLength = int(1E5)
epochLength = 20
consecutiveEpochs = 20
repetitions = 100
period = 10

# to keep solutions small, a penalty of sizeParam is applied per gate above the cutoff
sizeParam = 0.1
cutoff = 11

# modularity is adjusted for, using the values of Qmax and Qrand previously found
Qmax = 0.6435
Qrand = 0.3523

# config is a dictionary with the probability of each mutation and the fraction of top fitness individuals considered
# elite. These pass on to the next generation unmutatated and then reproduce. The weights correspond, in order, to:
# no mutation - new gate - gate deletion - switch of inputs - crossover
config = dict([("mutation weights", [0.3, 0.05, 0.05, 0.25, 0.35]), ("elite fraction", 0.3)])


# the two goals are defined
# G1: x XOR y AND z XOR w
# G2: x XOR y OR z XOR w
def g1(inputs):
    return inputs[0] ^ inputs[1] and inputs[2] ^ inputs[3]


def g2(inputs):
    return inputs[0] ^ inputs[1] or inputs[2] ^ inputs[3]


# booleanFitness takes in a function as argument, which defines what the target outputs are
def booleanFitness(genome, func, possibleInputs=np.array(list(product([1, 0], repeat=inputCount)))):
    # return the fitness of a network given by the % similarity across all inputs with func minus a size penalty

    # first find the required outputs
    requiredOutputs = [func(booleans) for booleans in possibleInputs]
    # then compare with the outputs of the network
    correct = np.equal(requiredOutputs, NFunc.truthTable(genome, possibleInputs))

    accuracy = np.count_nonzero(correct) / len(possibleInputs)
    sizePenalty = sizeParam * max(0, sum(NFunc.getPrecursors(genome)) - cutoff)

    return accuracy - sizePenalty


def averageModularity(population, fitnesses):
    # the average modularity of fitness 1 networks is measured
    examined = population[fitnesses == 1]
    if len(examined) > 0:
        modularityArray = np.array([NFunc.adjustedModularity(specimen, Qmax, Qrand) for specimen in examined])
        mean = np.mean(modularityArray)
        stdDev = np.std(modularityArray)
    else:
        mean = np.nan
        stdDev = np.nan
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
    consecutiveSolutionsFound = 0
    t1 = time.perf_counter()
    while i < simLength and not terminate:
        # alternate goal every epoch
        if i % epochLength * 2 < epochLength:
            goal = lambda x: booleanFitness(x, g1)
        else:
            goal = lambda x: booleanFitness(x, g2)
        generation, history[i], winners[i], (modularities[i], modularityStdDev[i]) = \
            GAFunc.runGeneration(generation, goal, averageModularity, config)

        # at the end of every epoch check how many consecutive solutions have been found
        if i % epochLength == epochLength - 1:
            if history[i] == 1:
                consecutiveSolutionsFound += 1
            else:
                consecutiveSolutionsFound = 0

            if consecutiveSolutionsFound == consecutiveEpochs:
                terminate = True

        # broadcast progress every period generations
        if i % period == 0:
            t2 = time.perf_counter()
            print("Run: " + str(j+1) + ". Generation " + str(i) + ".")
            print("Fitness: " + str(history[i]))
            print("Time per generation: " + str((t2 - t1) / period))
            t1 = time.perf_counter()

        i += 1

    # save all data to the appropiate files
    with open("Data/ModularGoals/Networks/Networks" + str(j) + ".txt", "w") as outputFile:
        networkStrings = [",".join([str(k) for k in network]) for network in winners[:i]]
        outputString = "\n".join(networkStrings)
        outputFile.write(outputString)

    with open("Data/ModularGoals/Fitness/Fitness" + str(j) + ".txt", "w") as outputFile:
        outputString = "\n".join([str(k) for k in history[:i]])
        outputFile.write(outputString)

    with open("Data/ModularGoals/Modularity/Modularity" + str(j) + ".txt", "w") as outputFile:
        dataStrings = [str(value) + ", " + str(stdDev) for value, stdDev in zip(modularities[:i], modularityStdDev[:i])]
        outputString = "\n".join(dataStrings)
        outputFile.write(outputString)