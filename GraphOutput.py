import numpy as np
import matplotlib.pyplot as plt
import csv 

# Define the bounds (change these values as needed)
x_min = 0
x_max = 0.1
y_min = -5
y_max = 5

plt.figure(figsize=(10, 6))

# Read from the csv file
with open('Output/run_config.csv', 'r') as file:
    reader = csv.reader(file)
    next(reader)  # Skip the header
    
    for row in reader:
        file_id, nodes_str, _, params = row
        nodes = eval(nodes_str)  # Convert string representation of list to actual list
        
        file_name = f'Output/{file_id}.txt'
        data = np.loadtxt(file_name)
        
        param_str = ' '.join(eval(params))  # Use the last column in run_config for labeling
        
        for idx, node in enumerate(nodes):
            x_col = 2 * idx  # 0, 2, 4, ...
            y_col = x_col + 1  # 1, 3, 5, ...
            
            x = data[:, x_col]
            y = data[:, y_col]
            
            label = f"{node} ({param_str})"
            plt.plot(x, y, label=label)

# Set plot parameters
plt.xlim([x_min, x_max])
plt.ylim([y_min, y_max])
plt.xlabel('Time (s)')
plt.ylabel('Voltage (V)')
plt.title('Multiple Plots')
plt.grid(True)
plt.legend(loc='best')  # Place legend at the best location

# Display the plot
plt.show()