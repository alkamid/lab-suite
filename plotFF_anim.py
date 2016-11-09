import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import numpy as np
from time import sleep
from matplotlib import animation

#plt.ion()
data = np.loadtxt('test.dat')
fig = plt.figure()
#ax = fig.add_subplot(111)

image = plt.imshow(data, cmap='viridis', interpolation='none')
#fig.canvas.draw()

def updatefig(*args):
    data = np.loadtxt('test.dat')
    image.set_data(data)
    return image,

ani = animation.FuncAnimation(fig, updatefig, interval=500, blit=True)
plt.show()
