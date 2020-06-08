import numpy as np
import NetworkFunctions as NFunc
from scipy.stats import sem

# generate random networks
randomNetworks = [NFunc.randomNetwork(13, 4) for i in range(100000)]

# select those whose connectivity matches that of those evolved. i.e. have 11 gates connected to gate 0
sanitizedNetworks = [individual for individual in randomNetworks if sum(NFunc.getPrecursors(individual))==11]
quantity = len(sanitizedNetworks)

# record the modularity of these networks and take the average
modularities = list(map(NFunc.getModularity, sanitizedNetworks))
average = np.mean(modularities)
stdDev = sem(modularities)

# write measured modularity to file
with open("Data\AdjustedModularityParams\Qrand.txt", "w") as outputFile:
    outputFile.write("Average modularity over " + str(len(sanitizedNetworks)) + " random networks found to be: \n")
    outputFile.write(str(average) + "±" + str(stdDev))