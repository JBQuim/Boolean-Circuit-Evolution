import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Polygon

def getTrajectories(path, fileCount, maxSize):
    trajectories = np.full((fileCount, maxSize), np.nan)
    for i in range(fileCount):
        with open(path + str(i) + ".txt") as file:
            data = np.array(file.readlines())
        trajectories[i][:len(data)] = data
    return trajectories


def getModularity(path, fileCount):
    modularities = np.full(fileCount, np.nan)
    for i in range(fileCount):
        with open(path + str(i) + ".txt") as file:
            data = file.readlines()

        samples = 40
        mod = np.full(samples, np.nan)
        for j,k in enumerate(data[-samples:]):
            mod[j] = k.split(",")[0]
        mod = mod[~np.isnan(mod)]
        if len(mod) > 0:
            modularities[i] = np.mean(mod)
    modularities = modularities[~np.isnan(modularities)]
    return modularities

resolution = 20
maxLength = int(1E5)
resolution = 20
start = resolution - 1
labels = ["Modular goals", "G1 fixed goal", "G2 fixed goal"]

# get the fitness over time of all experiments
G1Fitness = getTrajectories("Data/FixedGoals/G1/Fitness/Fitness", 50, maxLength)
G2Fitness = getTrajectories("Data/FixedGoals/G2/Fitness/Fitness", 50, maxLength)
MixedFitness = getTrajectories("Data/ModularGoals/Fitness/Fitness", 100, maxLength)

# find time needed to complete simulation
# when doing the experiments the simulation was carried on for some time before terminating so this is accounted for
lengthG1 = np.array([len(run[~np.isnan(run)]) for run in G1Fitness if run[~np.isnan(run)][-1] == 1])-20
lengthG2 = np.array([len(run[~np.isnan(run)]) for run in G2Fitness if run[~np.isnan(run)][-1] == 1])-20
lengthModularGoals = np.array([len(run[~np.isnan(run)]) for run in MixedFitness if run[~np.isnan(run)][-1] == 1])-400

# take means and 1st and 3rd quartiles
meanG1 = np.median(lengthG1)
meanG2 = np.median(lengthG2)
meanModular = np.median(lengthModularGoals)
quartilesG1 = np.quantile(lengthG1, [0.25, 0.75])-meanG1
quartilesG2 = np.quantile(lengthG2, [0.25, 0.75])-meanG2
quartilesModular = np.quantile(lengthModularGoals, [0.25, 0.75])-meanModular

# print time taken to reach a solution for each goal to the console
print(str(len(lengthG1)) + " successful solves of G1")
print(str(len(lengthG2)) + " successful solves of G2")
print(str(len(lengthModularGoals)) + " successful solves of alternating G1 and G2")

print("Time taken to complete G1 was: " + str(meanG1) + " (" + str(quartilesG1[0]) + ", " + str(quartilesG1[1]) + ")")
print("Time taken to complete G2 was: " + str(meanG2) + " (" + str(quartilesG2[0]) + ", " + str(quartilesG2[1]) + ")")
print("Time taken to complete alternating G1 and G2 was: " + str(meanModular) + " (" + str(quartilesModular[0]) + ", " + str(quartilesModular[1]) + ")")

# plot the fitness against time of a chosen run, number was varied to get an attractive looking run
chosen = 12
fig, ax = plt.subplots()
xdata = list(range(len(G1Fitness[chosen])))
ydata = G1Fitness[chosen]
ax.plot(xdata, ydata)

ax.set_xlabel("Generations", fontdict={'fontsize': 13})
ax.set_ylabel("Fitness", fontdict={'fontsize': 13})
ax.tick_params(axis='both', which='major', labelsize=13)
ax.set_title("Fitness of a typical G1 run over time", fontdict={'fontsize': 13})

plt.savefig("Figures/TypicalG1Run.png")




# initialize figure for plotting
boxFig, boxAx = plt.subplots()

# extract the average modularity of the individuals with fitness 1 from the data folder
MixedModularity = getModularity("Data/ModularGoals/Modularity/Modularity", 100)
G1modularity = getModularity("Data/FixedGoals/G1/Modularity/Modularity", 50)
G2modularity = getModularity("Data/FixedGoals/G2/Modularity/Modularity", 50)
data = [MixedModularity, G1modularity, G2modularity]
colours = ["tab:orange", "tab:blue", "tab:green"]

# generate plot and make some components transparent
bp = boxAx.boxplot(data)
plt.setp(bp['boxes'], alpha=0)
plt.setp(bp['fliers'], marker='+')
plt.setp(bp['medians'], alpha=0)

# code copied almost without modification from matplotlib documentation on box plots
num_boxes = len(data)
medians = np.empty(num_boxes)
for i in range(num_boxes):
    box = bp['boxes'][i]
    boxX = []
    boxY = []
    for j in range(5):
        boxX.append(box.get_xdata()[j])
        boxY.append(box.get_ydata()[j])
    box_coords = np.column_stack([boxX, boxY])

    # draw rectangles over the boxes
    boxAx.add_patch(Polygon(box_coords, facecolor=colours[i], zorder=2.5))

    # draw the median lines back over what we just filled in
    med = bp['medians'][i]
    medianX = []
    medianY = []
    for j in range(2):
        medianX.append(med.get_xdata()[j])
        medianY.append(med.get_ydata()[j])
        boxAx.plot(medianX, medianY, 'w', linewidth=2, zorder=2.5)

# formatting of labels and axes
boxAx.set_xticklabels(labels)
boxAx.tick_params(axis='both', which='major', labelsize=13)
boxAx.set_ylabel("Modularity of solution", fontdict={'fontsize': 13})
boxAx.yaxis.grid(True, linestyle='-', which='major', color='lightgrey', alpha=0.5)

plt.show()


"""
def animate(i):
    graphData = open("Data/data.txt", "r")
    data = graphData.read().split(",")
    data = [float(i) for i in data]
    graphData.close()

    modularityData = open("Data/data2.txt", "r")
    data2 = modularityData.read().split(",")
    data2 = [float(i) for i in data2]
    modularityData.close()
    if len(data) >= 20:
        dataLongY = data[resolution - 1::resolution]
        dataLongX = list(range(resolution - 1, len(data), resolution))

        dataLongX2 = list(range(len(data2)))

        dataShortY = data[-min(len(data), 200):]
        dataShortX = list(range(max(0, len(data) - 200), len(data)))

        ax1.clear()
        color = "tab:blue"
        ax1.plot(dataLongX, dataLongY, color=color)
        ax1.set_ylabel("Fitness", color=color)
        ax1.set_ybound(0, 1.05)
        ax1.tick_params(axis="y", labelcolor=color)

        ax2.clear()
        color = "tab:purple"
        ax2.set_xlabel("Generations")
        ax2.set_ylabel("Fitness", color=color)
        ax2.tick_params(axis="y", labelcolor=color)
        ax2.plot(dataShortX, dataShortY, color=color)
        ax2.set_ybound(0.6, 1.05)

        ax3.clear()
        color = "tab:red"
        ax3.set_ylabel("Modularity", color=color)
        ax3.scatter(dataLongX2, data2, color=color, alpha=0.1, s=5)
        ax3.tick_params(axis="y", labelcolor=color)
        ax3.set_ybound(0, 0.7)


ani = animation.FuncAnimation(fig, animate, interval=1000)
plt.show()
"""