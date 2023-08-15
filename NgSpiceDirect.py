import subprocess
import os
import numpy as np
import matplotlib.pyplot as plt

import tempfile
import shutil

class Simulation: 
    
    def __init__(self, nodes, simCommand):
        nodes_str = "" .join(["V(" + node + ")" for node in nodes])
        wrdata_str = "wrdata Output/outputData.txt " + nodes_str
        print(wrdata_str)

        self.control = [
            ".control", 
            simCommand, 
            wrdata_str, 
            "exit", 
            ".endc", 
            ".end"
        ]
    
    def append_control(self, filename, content_list):
        """
        Copy contents of the given file and append a list of strings to a temporary file.

        Parameters:
        - filename (str): The path of the source file.
        - content_list (List[str]): A list of strings to be appended to the file.

        Returns:
        - str: The path to the temporary file.
        """
    
        # Create a temporary file
        temp_file = tempfile.NamedTemporaryFile(delete=False, mode='w+t')

        # Copy contents of the original file to the temp file
        with open(filename, 'r') as f:
            shutil.copyfileobj(f, temp_file)

        # Add content from the list to the temp file
        for line in content_list:
            temp_file.write('\n' + line)

        # Get the name of the temp file and close it
        temp_file_path = temp_file.name
        temp_file.close()

        return temp_file_path

    def runSim(self):
        path = self.append_control("Subcircuits/PabloNL.cir", self.control)
        command = ["ngspice", path]
        subprocess.run(command)\
        

nodes = ["NLOut", "Non-LinearityNLA1Out"]
sim = Simulation(nodes, "dc v1 -10 10 1m")
sim.runSim()
# Run NgSpice simulation


data = np.loadtxt('Output/outputData.txt')

# Calculate the number of plots
num_plots = data.shape[1] // 2

# Configure plot bounds (change these values as needed)
x_min = -10
x_max = 10
y_min = -10
y_max = 10

# Create a plot
plt.figure(figsize=(10, 6))

# Iterate over each pair of columns and plot them
for i in range(num_plots):
    x = data[:, 2*i]
    y = data[:, 2*i + 1]
    plt.plot(x, y, label=f'Plot {i+1}')

# Set bounds for the plot
plt.xlim([x_min, x_max])
plt.ylim([y_min, y_max])



plt.xlabel('X Values')
plt.ylabel('Y Values')
plt.title('Multiple Plots')
plt.grid(True)
plt.legend(nodes)

# Display the plot
plt.show()