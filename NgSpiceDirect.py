import subprocess
import os
import numpy as np
import matplotlib.pyplot as plt


# Run NgSpice simulation
command = ["ngspice", "PabloNL.cir"]
subprocess.run(command)

input_file = "output.txt"
temp_file = "temp_output.txt"

# Flag to identify if the desired line is found
found = False

data = np.loadtxt('Output/outputData.txt')

# Split the data into two arrays for X and Y axes
x = data[:, 0]
y = data[:, 1]

# Create a plot
plt.plot(x, y)
plt.xlabel('Voltage 1')
plt.ylabel('Voltage 2')
plt.title('Voltage 1 vs Voltage 2')
plt.grid(True)

# Display the plot
plt.show()