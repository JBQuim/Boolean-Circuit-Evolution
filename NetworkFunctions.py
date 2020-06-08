import numpy as np
import random
from numba import jit
import networkx as nx
from networkx.algorithms import community

inputCount = 4

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

# function can be written as map or list comprehension but is written as for loop for compatibility with numba
@jit(nopython=True)
def truthTable(genome, possibleInputs):
    # calculate the output for every possible input
    results = np.full(len(possibleInputs), np.nan)
    for i in range(len(possibleInputs)):
        results[i] = resolve(0, genome, possibleInputs[i])
    return results



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
def getPrecursors(genome, numbs=None, visited=None):
    # returns a boolean array which is True if that item is a precursor of any of the gates in numbs
    if visited is None:
        visited = np.full(len(genome) // 2, False)
    if numbs is None:
        numbs = np.array([0])

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

    for i in numbs:
        visited[i] = True

    directPrecursors = np.where(directPrecursors)[0]

    if len(directPrecursors) == 0:
        return visited
    else:
        return getPrecursors(genome, directPrecursors, visited)

@jit(nopython=True)
def getPrecursorsWithInputs(genome, numbs=None, visited=None):
    # returns a boolean array which is True if that item is a precursor of any of the gates in numbs
    if visited is None:
        visited = np.full(len(genome) // 2 + inputCount, False)
    if numbs is None:
        numbs = np.array([0])

    directPrecursors = np.full(len(genome)//2 + inputCount, False)
    for i in numbs:
        if visited[i+inputCount] or i<0:
            continue
        k1 = genome[i*2]+inputCount
        k2 = genome[i*2+1]+inputCount
        if not visited[k1]:
            directPrecursors[k1] = True
        if not visited[k2]:
            directPrecursors[k2] = True

    for i in numbs:
        visited[i+inputCount] = True

    directPrecursors = np.where(directPrecursors)[0]-inputCount


    if len(directPrecursors) == 0:
        return visited
    else:
        return getPrecursorsWithInputs(genome, directPrecursors, visited)


def randomNetwork(size, inputCount):
    # initializes completely random networks
    possibleConnections = np.arange(-inputCount, size)
    genome = np.array([random.choice(possibleConnections) for i in range(size * 2)])
    return genome


def getGraph(genome):
    precursors = getPrecursorsWithInputs(genome)
    # add 0 node even if its not its own precursor
    precursors[0] = True
    graph = nx.Graph()
    graph.add_nodes_from(np.where(precursors)[0])
    edgeList = [(i//2, k) for i, k in enumerate(genome) if precursors[i//2+inputCount]]
    graph.add_edges_from(edgeList)

    return graph


def getModularity(genome):
    G = getGraph(genome)
    if G.number_of_edges() == 0:
        return 0
    else:
        partition = community.greedy_modularity_communities(G)
        modularity = community.modularity(G, partition)

    return modularity


def adjustedModularity(genome, Qmax, Qrand):
    Q = getModularity(genome)
    Qreal = (Q-Qrand)/(Qmax-Qrand)
    return Qreal

