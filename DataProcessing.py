import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Polygon
from math import ceil

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


maxLength = int(1E5)

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

print("Time taken to complete G1: " + str(meanG1) + " (" + str(quartilesG1[0]) + ", " + str(quartilesG1[1]) + ")")
print("Time taken to complete G2: " + str(meanG2) + " (" + str(quartilesG2[0]) + ", " + str(quartilesG2[1]) + ")")
print("Time taken to complete alternating G1 and G2: " + str(meanModular) + " (" + str(quartilesModular[0]) + ", " + str(quartilesModular[1]) + ")")


# plot the fitness against time of a chosen run, number was varied to get an attractive looking run
chosen = 0
chosen = G1Fitness[chosen]
fig, ax = plt.subplots()
xdata = list(range(len(chosen)))
ydata = chosen
ax.plot(xdata, ydata)

ax.set_xlabel("Generations", fontdict={'fontsize': 13})
ax.set_ylabel("Fitness", fontdict={'fontsize': 13})
ax.tick_params(axis='both', which='major', labelsize=13)
ax.set_title("Fitness of a typical G1 run over time", fontdict={'fontsize': 13})

plt.savefig("Figures/TypicalG1Run.png")


# plot the fitness against time of a chosen run, number was varied to get an attractive looking run
chosen = 30
chosen = MixedFitness[chosen][~np.isnan(MixedFitness[chosen])]
chosenLength = len(chosen)

# for the long plot, plot every resolution item so only the very end of the epoch is shown
resolution = 20
start = resolution - 1
zoomWidth = 100
zoomStart = max(chosenLength-zoomWidth, 0)

fig, (ax1, ax2) = plt.subplots(2, 1, gridspec_kw={'height_ratios': [2, 1]})
xdata = list(range(start, chosenLength, resolution))
xdataZoom = list(range(zoomStart, chosenLength))
ydata = chosen[start::resolution]
ydataZoom = chosen[zoomStart:]
ax1.plot(xdata, ydata)
ax2.plot(xdataZoom, ydataZoom)

# format axes
ax1.set_ylim(0.69,1.05)
ax2.set_ylim(0.69, 1.05)
ax1.set_ylabel("Fitness", fontdict={'fontsize': 13})
ax2.set_ylabel("Fitness", fontdict={'fontsize': 13})
ax2.set_xlabel("Generations", fontdict={'fontsize': 13})
ax1.set_title("Fitness as a function of time under time varying modular goals", fontdict={'fontsize': 13})
ax1.tick_params(axis='both', which='major', labelsize=11)
ax2.tick_params(axis='both', which='major', labelsize=11)

plt.savefig("Figures/TypicalModularRun.png")


# extract the average modularity of the individuals with fitness 1 from the data folder
MixedModularity = getModularity("Data/ModularGoals/Modularity/Modularity", 100)
G1modularity = getModularity("Data/FixedGoals/G1/Modularity/Modularity", 50)
G2modularity = getModularity("Data/FixedGoals/G2/Modularity/Modularity", 50)

# find the average modularity across all runs
meanG1, stdG1 = np.round(np.mean(G1modularity), 2), np.round(np.std(G1modularity), 2)
meanG2, stdG2 = np.round(np.mean(G2modularity), 2), np.round(np.std(G2modularity), 2)
meanMixed, stdMixed = np.round(np.mean(MixedModularity), 2), np.round(np.std(MixedModularity), 2)

# print the average with its standard deviation to the console
print("Modularity of G1: " + str(meanG1) + " ± " + str(stdG1))
print("Modularity of G2: " + str(meanG2) + " ± " + str(stdG2))
print("Modularity of alternating G1 and G2: " + str(meanMixed) + " ± " + str(stdMixed))

# initialize figure for plotting
boxFig, boxAx = plt.subplots()
data = [MixedModularity, G2modularity, G1modularity]
colours = ["tab:orange", "tab:blue", "tab:green"]
labels = ["Modular goals", "G2 fixed goal", "G1 fixed goal", ]

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
boxAx.set_title("Modularity under different sets of goals", fontdict={'fontsize': 13})
boxAx.set_ylim(-0.35,0.65)

plt.savefig("Figures/BoxPlotModularity.png")

max = 4999
samplingPeriod = 100
chosen = [4, 5, 8, 43]
chosenCount = len(chosen)
fileCount = 20

# get the modularity over time of all experiments
# for the chosen runs
history = np.full((chosenCount, fileCount, max), np.nan)
for i in range(chosenCount):
    for j in range(fileCount):
        with open("Data/ModularityDecay/Modularity/Modularity" + str(chosen[i]) + "-" + str(j) + ".txt") as file:
            data = np.array(file.readlines())
            data = np.array([line.split(",") for line in data]).T
        history[i][j] = data[0]

# find the average and error for every timepoint
avgTraj = np.full((chosenCount, ceil(max/samplingPeriod)), np.nan)
stdTraj = np.full((chosenCount, ceil(max/samplingPeriod)), np.nan)

for i, trajectory in enumerate(history):
    avgTraj[i] = np.array([np.mean(timepoint) for timepoint in trajectory.T[::samplingPeriod]])
    stdTraj[i] = np.array([np.std(timepoint) for timepoint in trajectory.T[::samplingPeriod]])

# initialize figure
fig, axes = plt.subplots(2, 2, sharex=True, sharey=True)
axes = axes.flatten()
colour = "tab:blue"

# plot the data with its errors
xdata = list(range(0, max, samplingPeriod))
for i in range(len(chosen)):
    axes[i].errorbar(xdata, avgTraj[i], stdTraj[i], alpha=0.5, color=colour)
    axes[i].plot(xdata, avgTraj[i], "-o", color=colour)
    axes[i].tick_params(axis='both', which='major', labelsize=13)

axes[0].set_ylim(0.1, 0.65)

# place axis labels around the outside and add title
axes[2].set_xlabel("Generations", fontdict={'fontsize': 13})
axes[3].set_xlabel("Generations", fontdict={'fontsize': 13})
axes[0].set_ylabel("Modularity", fontdict={'fontsize': 13})
axes[2].set_ylabel("Modularity", fontdict={'fontsize': 13})
plt.suptitle("Modularity over time", fontsize=16)

plt.savefig("Figures/ModularityDecay.png")
