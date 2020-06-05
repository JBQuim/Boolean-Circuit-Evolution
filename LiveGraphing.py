import matplotlib; matplotlib.use("TkAgg")
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib import style

style.use("seaborn-dark")

fig, (ax1, ax2) = plt.subplots(2, 1, gridspec_kw={'height_ratios': [2, 1]})



def animate(i):
    graphData = open("data.txt", "r").read()
    data = graphData.split(",")
    data = [float(i) for i in data]
    if len(data) >= 20:
        dataLongY = data[19::20]
        dataLongX = list(range(19,len(data),20))

        dataShortY = data[-min(len(data),200):]
        dataShortX = list(range(max(0,len(data)-200),len(data)))

        ax1.clear()
        ax2.clear()
        ax1.plot(dataLongX, dataLongY)
        ax2.plot(dataShortX, dataShortY)
        ax2.set_xlabel("Generations")
        ax1.set_ylabel("Fitness")
        ax2.set_ylabel("Fitness")
        ax1.set_ybound(0, 1.05)
        ax2.set_ybound(0.6, 1.05)

ani = animation.FuncAnimation(fig, animate, interval=1000)
plt.show()
