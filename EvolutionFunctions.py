import numpy as np
import random
import bisect
import NetworkFunctions as NFunc

inputCount = 4


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


def mutate(generation, mutationWeights, fractionElite):
    # choose a type of mutation for every individual. Elite are not mutated.
    popSize = len(generation)
    integers = WeightedRandomGenerator(mutationWeights)
    mutationType = np.array([integers() for i in generation])
    mutationType[:int(popSize * fractionElite)] = [0] * int(popSize * fractionElite)

    mutationFunctions = np.array([lambda x: x, addGate, removeGate, switchInputs, lambda x: x])
    newGeneration = np.array(
        [mutationFunctions[mutationId](specimen) for mutationId, specimen in zip(mutationType, generation)])

    crossOverPairs = mutationType == 4
    crossOverCount = sum(crossOverPairs)
    crossOvers = np.array(list(enumerate(newGeneration)), dtype=object)[crossOverPairs]
    for (i, specimen1), (k, specimen2) in zip(crossOvers[:crossOverCount // 2], crossOvers[crossOverCount // 2:]):
        newGeneration[i], newGeneration[k] = crossOver(specimen1, specimen2)

    # shuffling ensures diversity in the elite if there are a large fraction of high fitness individuals
    np.random.shuffle(newGeneration)
    return newGeneration


def crossOver(individual1, individual2):
    # select random point within genomes and swap
    size = len(individual1)

    recombinationSite = random.randint(2, size - 2)
    individual1[recombinationSite:], individual2[recombinationSite:] = individual2[
                                                                       recombinationSite:].copy(), individual1[
                                                                                                   recombinationSite:].copy()

    return individual1.copy(), individual2.copy()


def addGate(genome):
    # find a gate which's output is ignored. Change its inputs and connect a random gate to it
    size = len(genome) // 2
    nonTargets = np.argwhere(~NFunc.getPrecursors(genome)[1:])
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

    possible = np.arange(-inputCount, size // 2)

    genome[target] = random.choice(possible)
    return genome


def runGeneration(population, fitnessFunc, reporterFunc, config):
    # calculate fitness for the population, select a fraction to be the elite, reproduce them and return a mutated
    # version of the elite
    # reporterFunc is passed the whole generation and their fitness and its output is returned. Used to probe the
    # population during the simulation
    fractionElite = config["elite fraction"]
    weights = config["mutation weights"]

    fitnesses = np.array([fitnessFunc(individual) for individual in population])
    indexes = np.argsort(fitnesses)[int(len(population) * (1 - fractionElite)):]
    elite = np.array([genome for i, genome in enumerate(population) if i in indexes])[::-1]

    newGen = [elite[i % len(elite)].copy() for i in range(len(population))]

    mostFit = elite[0]
    maxFitness = max(fitnesses)

    return mutate(newGen, weights, fractionElite), maxFitness, mostFit, reporterFunc(population, fitnesses)
