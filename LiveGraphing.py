import matplotlib;

matplotlib.use("TkAgg")
import matplotlib.animation as animation
from matplotlib import style
import matplotlib.pyplot as plt
import numpy as np

style.use("seaborn-dark")

fig, (ax1, ax2) = plt.subplots(2, 1, gridspec_kw={'height_ratios': [2, 1]})
ax3 = ax1.twinx()

resolution = 20


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
