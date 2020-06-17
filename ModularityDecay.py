import numpy as np
from itertools import product
import time
import NetworkFunctions as NFunc
import EvolutionFunctions as GAFunc
import random

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
simLength = 5000
consecutiveSolutions = 20
repetitions = 20
period = 10
samplingPeriod = 100

# to keep solutions small, a penalty of sizeParam is applied per gate above the cutoff
sizeParam = 0.2
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
    modularityArray = np.array([NFunc.adjustedModularity(specimen, Qmax, Qrand) for specimen in population])
    mean = np.mean(modularityArray)
    stdDev = np.std(modularityArray)

    return mean, stdDev


def doNothing(a, b):
    return np.nan, np.nan


def getNetworks(path, networkNumb, amount):
    with open(path + "/Networks" + str(networkNumb) + ".txt") as network:
        finalNetwork = np.array(network.readlines()[-1].split(","))
        # remove the decimal point and trailing zero from the string before turning into an integer
        finalNetwork = np.array([int(i[:-2]) for i in finalNetwork])

    # cycle through those networks until the given amount is achieved
    outputNetworks = np.resize(np.tile(finalNetwork, amount), (amount, length*2))
    return outputNetworks


for j in range(0, repetitions):
    # initiate the network with number networkID
    networkID = 4
    generation = getNetworks("Data/ModularGoals/Networks", networkID, 1000)

    # these will store the data collected throughout
    history = np.full(simLength, np.nan)
    modularities = np.full(simLength, np.nan)
    modularityStdDev = np.full(simLength, np.nan)
    winners = np.full((simLength, length * 2), np.nan)

    t1 = time.perf_counter()
    for i in range(simLength):
        # sample the population modularity once every samplingPeriod generations
        if i % samplingPeriod == 0:
            introspectionFunction = averageModularity
        if i % samplingPeriod == 1:
            introspectionFunction = doNothing

        # here the fixed goal is specified
        goal = lambda x: booleanFitness(x, g2)
        generation, history[i], winners[i], (modularities[i], modularityStdDev[i]) = \
            GAFunc.runGeneration(generation, goal, introspectionFunction, config)

        # broadcast progress every period generations
        if i % period == 0:
            t2 = time.perf_counter()
            print("Run: " + str(j+1) + ". Generation " + str(i) + ".")
            print("Fitness: " + str(history[i]))
            print("Time per generation: " + str((t2 - t1) / period))
            t1 = time.perf_counter()


    # save all data to the appropiate files
    with open("Data/ModularityDecay/Networks/Networks" + str(networkID) + "-" + str(j) + ".txt", "w") as outputFile:
        networkStrings = [",".join([str(k) for k in network]) for network in winners[:i]]
        outputString = "\n".join(networkStrings)
        outputFile.write(outputString)

    with open("Data/ModularityDecay/Fitness/Fitness" + str(networkID) + "-" + str(j) + ".txt", "w") as outputFile:
        outputString = "\n".join([str(k) for k in history[:i]])
        outputFile.write(outputString)

    with open("Data/ModularityDecay/Modularity/Modularity" + str(networkID) + "-" + str(j) + ".txt", "w") as outputFile:
        dataStrings = [str(value) + ", " + str(stdDev) for value, stdDev in zip(modularities[:i], modularityStdDev[:i])]
        outputString = "\n".join(dataStrings)
        outputFile.write(outputString)
