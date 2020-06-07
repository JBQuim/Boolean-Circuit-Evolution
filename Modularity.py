import numpy as np
import NetworkFunctions as NFunc




rand = [NFunc.randomNetwork(13) for i in range(100000)]
sanitized = [individual for individual in rand if sum(NFunc.getPrecursors(individual))==11]
modularities = list(map(NFunc.getModularity, sanitized))
print(np.mean(modularities))


"""
networks = [randomNetwork(12) for i in range(100000)]
sanitized = [network for network in networks if sum(getPrecursors(network)) >= 11]
modularities = list(map(getModularity, networks))
print(np.mean(modularities))
print(len(sanitized))
"""
