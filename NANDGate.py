import numpy as np
from itertools import product
import random
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
import copy
import time
import bisect
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas

genome = np.array([(1, 2), (-1, -2), (-3, -4), (2, 2)])
sizeParam = 0.2
inputCount = 4
cutoff = 10
fractionElite = 0.3
maxSize = 16
minSize = 5
mutationChance = 0.3
# nothing - duplication - deletion - switch - new
mutationWeights = [0.3, 0.1, 0.2, 0.35, 0.05]
popSize = 1000
simLength = 30000


def resolve(numb, genome, inputs):
    if numb < 0:
        return inputs[-1 + numb * -1]
    else:
        input1 = resolve(genome[numb][0], genome, inputs)
        input2 = resolve(genome[numb][1], genome, inputs)
        return not (input1 and input2)


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
    possibleInputs = list(product([True, False], repeat=inputCount))
    requiredOutputs = [func(booleans) for booleans in possibleInputs]

    mistakes = np.logical_xor(requiredOutputs, truthTable(genome, possibleInputs))

    accuracy = 1 - sum(mistakes) / len(possibleInputs)
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

    cycles = True
    while cycles:
        genome = [[random.choice(possibleConnections), random.choice(possibleConnections)] for i in range(size)]
        cycles = hasCycles(genome)

    return genome


def g1(inputs):
    return inputs[0] ^ inputs[1] and inputs[2] ^ inputs[3]


def g2(inputs):
    return inputs[0] ^ inputs[1] or inputs[2] ^ inputs[3]


def mutate(generation):
    integers = WeightedRandomGenerator(mutationWeights)
    mutationType = [integers() for i in generation]
    mutationType[:int(popSize * fractionElite)] = [0] * int(popSize * fractionElite)
    mutationFunctions = np.array([lambda x: x, duplicate, addGate, removeGate, switchInputs])
    newGeneration = np.array([mutationFunctions[mutationType[i]](specimen) for i, specimen in enumerate(generation)])
    return newGeneration


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
        if len(new) > maxSize:
            print("Went from " + str(size) + " to " + str(len(new)))
            print("Duplication size was: " + str(duplicationSize))
            print("Allowed range was: 1, " + str(min(size - point1, maxSize - point1) - 1))
    return new


def addGate(genome):
    size = len(genome)
    if size < maxSize:
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
            possible = available(genome, i)
            possible.remove(target)
            genome[i][0] = random.choice(possible)
        if k1 == target:
            possible = available(genome, i)
            possible.remove(target)
            genome[i][1] = random.choice(possible)

    for i, (k0, k1) in enumerate(genome):
        if k0 > target:
            genome[i][0] -= 1
        if k1 > target:
            genome[i][1] -= 1
    try:
        del genome[target]
    except:
        print(genome)
        print(target)
        print("ERROR FOUND ---------------------------------------------------------------------------------------")
    return genome


def switchInputs(genome):
    size = len(genome)
    target1 = random.randint(0, size - 1)
    target2 = random.randint(0, 1)

    possible = available(genome, target1)

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
    elite = population[indexes][::-1]
    mostFit = elite[0]

    newGen = np.array([copy.deepcopy(elite[i % len(elite)]) for i in range(len(population))])

    difference = len(population) - len(newGen)
    if difference > 0:
        newGen = np.concatenate((newGen, elite[:difference]))

    return mutate(newGen), maxFitness, mostFit


def checkMayhem(genome):
    size = len(genome)
    correctSize = [i0 < size and i1 < size for k, (i0, i1) in enumerate(genome)].count(False) > 0
    return correctSize


def countMayhem(population):
    return [checkMayhem(specimen) for specimen in population].count(True)


generation = np.array([randomNetwork(10, 15) for i in range(popSize)])
t1 = time.clock()
history = np.full(simLength, np.nan)

fig = Figure()
canvas = FigureCanvas(fig)
ax = fig.add_subplot(111)

i = 0
history[0] = 0
while history[i] < 1 and i < simLength - 1:
    i += 1
    if i % 50 == 0:
        t2 = time.clock()
        print("Generations: " + str(i))
        if i != 0:
            print("Time per generation: " + str((t2 - t1) / 50))
            print("Fitness: " + str(history[i - 1]))
        t1 = time.clock()
    generation, history[i], winner = runGeneration(generation, g1)
t2 = time.clock()
print(winner)
print((t2 - t1) / simLength)

fig.clf()
plt.xlabel("Generations")
plt.ylabel("Fitness")
plt.plot(list(range(simLength)), history)
plt.show()
