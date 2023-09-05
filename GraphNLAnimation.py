import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import Normalize
from scipy.signal import resample

from matplotlib.animation import FuncAnimation


# Generate some example DC curve data (replace with your real data)
#x_dc = np.linspace(0, 1, 1000)  # DC voltage sweep
#y_dc = x_dc * 2
data = np.loadtxt("Output/VisualisationMixD/20902DCSweep.txt")
x_dc = data[:,0]
y_dc = data[:,1]

# Create arrays of 500 zeroes
neg_x = np.linspace(-5, 0, 500)

# Pad 500 zeroes to the beginning
x_dc = np.concatenate((neg_x, x_dc))
y_dc = np.pad(y_dc, (500, 0), 'constant', constant_values=0)

# Resample y_dc to have the same number of points as x_dc
y_dc = resample(y_dc, len(x_dc))

# Generate some example voltage readings (replace with your real data)
#voltage_readings = np.random.normal(0, 5, 1000)  # Random data centered around 0
data = np.loadtxt("Output/VisualisationMixD/20902.txt")
time_readings = data[:, 0]  # Assuming that time is in the first column
voltage_readings = data[:, 1]  # Assuming that voltage readings are in the second column

step_size = 50
reduced_time_readings = time_readings[::step_size]
reduced_voltage_readings = voltage_readings[::step_size]
# Initialize the plot
fig, ax = plt.subplots()
# Plot the static DC curve
ax.plot(x_dc, y_dc, label="DC Curve")
time_text = ax.text(0.05, 0.9, '', transform=ax.transAxes)
# Initial point
point, = ax.plot([], [], 'bo', label="Voltage Reading")  # The 'bo' makes it a blue circle

# Set the x and y axis limits
ax.set_xlim(np.min(x_dc), np.max(x_dc))
ax.set_ylim(np.min(y_dc), np.max(y_dc))
ax.set_xlabel('X')
ax.set_ylabel('Y')
ax.legend()

def init():
    point.set_data([], [])
    return point,

def update(frame):
    x_point = reduced_voltage_readings[frame]  # assuming time is the first column
    y_point = np.interp(x_point, x_dc, y_dc)  # assuming voltage is the second column
    point.set_data(x_point, y_point)
    time_text.set_text('Time: {:.2f}s'.format(reduced_time_readings[frame]))
    return point,

# Create the animation object
ani = FuncAnimation(fig, update, frames=range(len(reduced_voltage_readings)), init_func=init, blit=True)

# Save the animation
ani.save('overlay_animation_slow.mp4', fps=10)