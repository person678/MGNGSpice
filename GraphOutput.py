import numpy as np
import matplotlib.pyplot as plt

data = np.loadtxt('Output/outputData66066.txt')

# Configure plot bounds (change these values as needed)
x_min = 0
x_max = 0.01
y_min = -2
y_max = 2

# Create a plot
plt.figure(figsize=(10, 6))

# Iterate over each pair of columns and plot them
x = data[:, 0]
y = data[:, 1]
plt.plot(x, y)

# Set bounds for the plot
plt.xlim([x_min, x_max])
plt.ylim([y_min, y_max])

plt.xlabel('X Values')
plt.ylabel('Y Values')
plt.title('Multiple Plots')
plt.grid(True)
plt.legend()

# Display the plot
plt.show()