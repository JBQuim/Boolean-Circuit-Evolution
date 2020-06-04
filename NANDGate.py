import numpy as np
from itertools import product
import random
import copy
import time
import bisect
from numba import jit


sizeParam = 0.2
inputCount = 4
cutoff = 10
fractionElite = 0.3
maxSize = 15
minSize = 9
# nothing - duplication - new - delete - switch - crossover
mutationWeights = [0.3, 0.05, 0.05, 0.05, 0.05, 0.5]

popSize = 1000
simLength = 100000


def resolve(numb, genome, inputs, visited=None, computed=None):
    if visited is None:
        visited = [False] * len(genome)
    if computed is None:
        computed = [2] * len(genome)
    if numb < 0:
        return inputs[-1 + numb * -1]
    elif not visited[numb]:
        visited[numb] = True
        input1 = resolve(genome[numb][0], genome, inputs, visited, computed)
        if input1 == 0:
            computed[numb] = 1
        else:
            input2 = resolve(genome[numb][1], genome, inputs, visited, computed)
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
    return list(map(lambda x: resolve(0, genome, x), possibleInputs))


def fitness(genome, func):
    possibleInputs = list(product([1, 0], repeat=inputCount))
    requiredOutputs = [func(booleans) for booleans in possibleInputs]

    correct = np.equal(requiredOutputs, truthTable(genome, possibleInputs))

    accuracy = sum(correct) / len(possibleInputs)
    sizePenalty = sizeParam * max(0, len(getPrecursors(genome, [0])) - cutoff)

    return accuracy - sizePenalty


def getDependents(genome, numbs, *args):
    if not args:
        visited = set([])
    else:
        visited = args[0]

    directDependents = [i for numb in numbs for i, k in enumerate(genome) if
                        (k[0] == numb or k[1] == numb) and i not in visited]

    visited.update(directDependents)

    if len(directDependents) == 0:
        return visited
    else:
        return getDependents(genome, directDependents, visited)


def getPrecursors(genome, numbs, *args):
    if not args:
        visited = set([])
        depth = 0
    else:
        visited = args[0]
        depth = args[1]

    # directPrecursors = [i for numb in numbs if numb >= 0 for i in genome[numb] if i not in visited] <- use this if
    # getPrecursors() should return inputs as precursors
    directPrecursors = [i for numb in numbs if numb >= 0 for i in genome[numb] if i not in visited and i >= 0]
    visited.update(directPrecursors)

    if len(directPrecursors) == 0:
        return visited
    else:
        return getPrecursors(genome, directPrecursors, visited, depth + 1)


def hasCycles(genome):
    for i in range(len(genome)):
        if i in getPrecursors(genome, [i]):
            return True
    return False


def countCycles(population):
    return [hasCycles(specimen) for specimen in population].count(True)


def randomNetwork(minSize, maxSize):
    size = random.randint(minSize, maxSize)
    possibleConnections = [x for x in range(-inputCount, size) if x != 0]
    genome = [[random.choice(possibleConnections), random.choice(possibleConnections)] for i in range(size)]

    return genome


def g1(inputs):
    return inputs[0] ^ inputs[1] and inputs[2] ^ inputs[3]


def g2(inputs):
    return inputs[0] ^ inputs[1] or inputs[2] ^ inputs[3]


def mutate(generation):
    popSize = len(generation)
    integers = WeightedRandomGenerator(mutationWeights)
    mutationType = [integers() for i in generation]
    mutationType[:int(popSize * fractionElite)] = [0] * int(popSize * fractionElite)

    mutationFunctions = np.array([lambda x: x, duplicate, addGate, removeGate, switchInputs, lambda x: x])
    newGeneration = [mutationFunctions[mutationType[i]](specimen) for i, specimen in enumerate(generation)]

    crossoverCount = np.count_nonzero(mutationType == 5)
    crossOverPairs = [newGeneration[i] for i, k in enumerate(mutationType) if
                      k == 5 and not (i == crossoverCount and i % 2 == 0)]
    for i, (genome1, genome2) in enumerate(
            zip(crossOverPairs[:len(crossOverPairs) // 2], crossOverPairs[len(crossOverPairs) // 2:])):
        newGeneration[i], newGeneration[i + 1] = crossOver(genome1, genome2)

    return newGeneration


def crossOver(individual1, individual2):
    size1 = len(individual1)
    size2 = len(individual2)

    recombinationSite = random.randint(1, min(size1, size2) - 1)
    individual1[recombinationSite:], individual2[recombinationSite:] = copy.deepcopy(
        individual2[recombinationSite:]), copy.deepcopy(individual1[recombinationSite:])

    size1 = len(individual1)
    possible = [i for i in range(-inputCount, size1) if i != 0]
    for i, (k1, k2) in enumerate(individual1):
        if k1 >= size1:
            individual1[i][0] = random.choice(possible)
        if k2 >= size1:
            individual1[i][1] = random.choice(possible)

    size2 = len(individual2)
    possible = [i for i in range(-inputCount, len(individual2)) if i != 0]
    for i, (k1, k2) in enumerate(individual2):
        if k1 >= size2:
            individual2[i][0] = random.choice(possible)
        if k2 >= size2:
            individual2[i][1] = random.choice(possible)
    return individual1, individual2




def duplicate(genome):
    size = len(genome)
    new = genome
    if size < maxSize:
        point1 = random.randint(0, size - 2)
        duplicationSize = random.randint(1, min(size - point1, maxSize - size))

        point2 = point1 + duplicationSize
        slice = copy.deepcopy(genome[point1:point2])
        new = copy.deepcopy(genome + slice)
        slice = new[size:-1]
        for k, (i0, i1) in enumerate(slice):
            if point1 <= i0 < point2:
                slice[k][0] = i0 + size - point1
            if point1 <= i1 < point2:
                slice[k][1] = i1 + size - point1
        for i in range(random.randint(0, 2)):
            switchInputs(new)
    return new


def addGate(genome):
    size = len(genome)
    if size < maxSize:
        # should be size+1 if wiring to itself is to be allowed. For now, not because this motif is probably not good
        options = [i for i in range(-inputCount, size) if i != 0]
        genome = genome + [[random.choice(options), random.choice(options)]]
    return genome


def removeGate(genome):
    size = len(genome)
    if size <= minSize:
        return genome
    target = random.randint(1, size - 1)
    for i, (k0, k1) in enumerate(genome):
        if k0 == target:
            possible = [x for x in range(-inputCount, size) if x != 0 and x != target]
            genome[i][0] = random.choice(possible)
        if k1 == target:
            possible = [x for x in range(-inputCount, size) if x != 0 and x != target]
            genome[i][1] = random.choice(possible)

    for i, (k0, k1) in enumerate(genome):
        if k0 > target:
            genome[i][0] -= 1
        if k1 > target:
            genome[i][1] -= 1
    del genome[target]
    return genome


def switchInputs(genome):
    size = len(genome)
    target1 = random.randint(0, size - 1)
    target2 = random.randint(0, 1)

    possible = [i for i in range(-inputCount, size) if i != 0]

    genome[target1][target2] = random.choice(possible)
    return genome


def available(genome, gate):
    size = len(genome)
    dependents = getDependents(genome, [gate])
    possibleInputs = [x for x in range(-inputCount, size) if x != 0]
    return list(set(possibleInputs).difference(dependents) - {gate})


def runGeneration(population, goal):
    fitnesses = [fitness(individual, goal) for individual in population]
    maxFitness = max(fitnesses)
    indexes = np.argsort(fitnesses)[int(len(population) * (1 - fractionElite)):]
    elite = [genome for i, genome in enumerate(population) if i in indexes][::-1]
    mostFit = elite[0]

    newGen = [copy.deepcopy(elite[i % len(elite)]) for i in range(len(population))]

    return mutate(newGen), maxFitness, mostFit


def checkMayhem(genome):
    size = len(genome)
    correctSize = [i0 < size and i1 < size for k, (i0, i1) in enumerate(genome)].count(False) > 0
    return correctSize


def countMayhem(population):
    return [checkMayhem(specimen) for specimen in population].count(True)


generation = [randomNetwork(minSize, maxSize) for i in range(popSize)]
t1 = time.clock()
history = np.full(simLength, np.nan)

i = 0
history[0] = 0
t0 = time.clock()
while i < simLength - 1:
    i += 1
    if i % 50 == 0 and i != 0:
        t2 = time.clock()
        print("Generations: " + str(i))
        if i != 0:
            print("Time per generation: " + str((t2 - t1) / 50))
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

t2 = time.clock()
print(winner)
print((t2 - t0) / i)