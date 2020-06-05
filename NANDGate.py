import numpy as np
from itertools import product
import random
import time
import bisect
from numba import jit
sizeParam = 0.2
inputCount = 4
cutoff = 10
fractionElite = 0.3
length = 13
# nothing - new - delete - switch - crossover
mutationWeights = [0.3, 0.05, 0.05, 0.25, 0.35]

popSize = 1000
simLength = 100000

@jit(nopython=True)
def resolve(numb, genome, inputs, computed=None):
    # compute the output of numb given a network described by genome and some inputs. Output 2 or 3 if state is unknown
    if computed is None:
        computed = [2] * (len(genome) // 2)
    if numb < 0:
        return inputs[-1 + numb * -1]
    elif computed[numb] == 2:
        computed[numb] = 3
        input1 = resolve(genome[numb * 2], genome, inputs, computed)
        if input1 == 0:
            computed[numb] = 1
        else:
            input2 = resolve(genome[numb * 2 + 1], genome, inputs, computed)
            if input2 == 0:
                computed[numb] = 1
            elif input1 == 1 and input2 == 1:
                computed[numb] = 0
    return computed[numb]


class WeightedRandomGenerator(object):
    def __init__(self, weights):
        self.totals = []
        running_total = 0

        for w in weights:
            running_total += w
            self.totals.append(running_total)

    def next(self):
        rnd = random.random() * self.totals[-1]
        return bisect.bisect_right(self.totals, rnd)

    def __call__(self):
        return self.next()



def truthTable(genome, possibleInputs):
    # calculate the output for every possible input
    return np.array(list(map(lambda x: resolve(0, genome, x), possibleInputs)))


def fitness(genome, func):
    # return the fitness of a network given by the % similarity across all inputs with func minus a size penalty
    possibleInputs = list(product([1, 0], repeat=inputCount))
    requiredOutputs = [func(booleans) for booleans in possibleInputs]
    correct = np.equal(requiredOutputs, truthTable(genome, possibleInputs))


    accuracy = np.count_nonzero(correct) / len(possibleInputs)
    sizePenalty = sizeParam * max(0, sum(getPrecursors(genome, [0])) - cutoff)

    return accuracy - sizePenalty


def getDependents(genome, numbs, visited=None):
    # returns a boolean array which is True if that gate is dependent on any of the gates in numbs
    if visited is None:
        visited = np.full(len(genome) // 2, False)

    directDependents = [i // 2 for i, k in enumerate(genome) if k in numbs and not i // 2 in visited]
    visited[directDependents] = True

    if len(directDependents) == 0:
        return visited
    else:
        return getDependents(genome, directDependents, visited)

@jit(nopython=True)
def getPrecursors(genome, numbs, visited=None):
    # returns a boolean array which is True if that item is a precursor of any of the gates in numbs
    if visited is None:
        visited = np.full(len(genome) // 2, False)

    directPrecursors = np.full(len(genome)//2, False)
    for i in numbs:
        if visited[i]:
            continue
        k1 = genome[i*2]
        k2 = genome[i*2+1]
        if k1 >= 0 and not visited[abs(k1)]:
            directPrecursors[k1] = True
        if k2 >= 0 and not visited[abs(k2)]:
            directPrecursors[k2] = True

    visited[directPrecursors] = True
    directPrecursors = np.where(directPrecursors)[0]

    if len(directPrecursors) == 0:
        return visited
    else:
        return getPrecursors(genome, directPrecursors, visited)

def randomNetwork(size):
    # initializes completely random networks
    possibleConnections = np.arange(-inputCount, size)
    genome = np.array([random.choice(possibleConnections) for i in range(size * 2)])
    return genome


def g1(inputs):
    return inputs[0] ^ inputs[1] and inputs[2] ^ inputs[3]


def g2(inputs):
    return inputs[0] ^ inputs[1] or inputs[2] ^ inputs[3]

def mutate(generation):
    # choose a type of mutation for every individual. Elite are not mutated.
    popSize = len(generation)
    integers = WeightedRandomGenerator(mutationWeights)
    mutationType = np.array([integers() for i in generation])
    mutationType[:int(popSize * fractionElite)] = [0] * int(popSize * fractionElite)

    mutationFunctions = np.array([lambda x: x, addGate, removeGate, switchInputs, lambda x: x])
    newGeneration = np.array([mutationFunctions[mutationId](specimen) for mutationId, specimen in zip(mutationType, generation)])

    crossOverPairs = mutationType == 4
    crossOverCount = sum(crossOverPairs)
    crossOvers = np.array(list(enumerate(newGeneration)), dtype=object)[crossOverPairs]
    for (i, specimen1), (k, specimen2) in zip(crossOvers[:crossOverCount//2], crossOvers[crossOverCount//2:]):
        newGeneration[i], newGeneration[k] = crossOver(specimen1, specimen2)

    return newGeneration

def crossOver(individual1, individual2):
    # select random point within genomes and swap
    size = len(individual1)

    recombinationSite = random.randint(2, size - 2)
    individual1[recombinationSite:], individual2[recombinationSite:] = individual2[recombinationSite:].copy(), individual1[
                                                                                                        recombinationSite:].copy()

    return individual1.copy(), individual2.copy()



def addGate(genome):
    # find a gate which's output is ignored. Change its inputs and connect a random gate to it
    size = len(genome) // 2
    nonTargets = np.argwhere(~getPrecursors(genome, [0])[1:])
    targets = [i for i in range(1, size) if i not in nonTargets]
    if len(targets) > 0:
        target = random.choice(targets)
        genome[target * 2], genome[target * 2 + 1] = random.randint(-inputCount, size - 1), random.randint(-inputCount,
                                                                                                           size - 1)

        target2 = random.randint(0, size * 2 - 1)
        genome[target2] = target
    return genome


def removeGate(genome):
    # find all gates connected to the output of target and wire them to another gate
    size = len(genome) // 2
    target = random.randint(1, size - 1)
    possible = [x for x in range(-inputCount, size) if x != target]
    for i, k in enumerate(genome):
        if k == target:
            genome[i] = random.choice(possible)
    return genome


def switchInputs(genome):
    # find a random connection and change it to another gate
    size = len(genome)
    target = random.randint(0, size - 1)

    possible = np.arange(-inputCount, size//2)

    genome[target] = random.choice(possible)
    return genome

def runGeneration(population, goal):
    # calculate fitness for the population, select a fraction to be the elite, reproduce them and return a mutated
    # version of the elite
    fitnesses = [fitness(individual, goal) for individual in population]
    indexes = np.argsort(fitnesses)[int(len(population) * (1 - fractionElite)):]
    elite = np.array([genome for i, genome in enumerate(population) if i in indexes])[::-1]

    newGen = [elite[i % len(elite)].copy() for i in range(len(population))]

    mostFit = elite[0]
    maxFitness = max(fitnesses)

    return mutate(newGen), maxFitness, mostFit

generation = np.array([randomNetwork(length) for i in range(popSize)])


t1 = time.clock()
history = np.full(simLength, np.nan)
i = 0
history[0] = 0
t0 = time.clock()
while i < simLength - 1:
    i += 1
    if i % 10 == 0 and i != 0:
        t2 = time.clock()
        print("Generations: " + str(i))
        if i != 0:
            print("Time per generation: " + str((t2 - t1) / 10))
            print("Fitness: " + str(history[i - 1]))
            data = open("data.txt", "w")
            data.write(",".join([str(k) for k in history[:i]]))
            data.close()

        t1 = time.clock()
    if i % 40 < 20:
        generation, history[i], winner = runGeneration(generation, g2)
        if history[i] == 1:
            networkFile = open("networks.txt", "a")
            networkFile.write("For G2: \n")
            networkFile.write(str(winner) + " \n")
    else:
        generation, history[i], winnner = runGeneration(generation, g1)
        if history[i] == 1:
            networkFile = open("networks.txt", "a")
            networkFile.write("For G1: \n")
            networkFile.write(str(winner) + " \n")