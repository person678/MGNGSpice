import subprocess
import os
import numpy as np
import matplotlib.pyplot as plt

import tempfile
import shutil
import random

from multiprocessing import Pool
from PySpice.Spice.Netlist import Circuit
from PySpice.Spice.Parser import SpiceParser

def worker(params):
    nodes, command = params
    sim = Simulation(nodes, command, "PabloNL")
    sim.runSim()
class Simulation: 
    
    def __init__(self, nodes, simCommand, netlist):
        nodes_str = "" .join(["V(" + node + ")" for node in nodes])
        temp_id = str(random.randint(1, 100000))
        wrdata_str = "wrdata Output/outputData" + temp_id + ".txt " + nodes_str
        print(wrdata_str)
        self.netlist = "Subcircuits/temp/" + netlist + temp_id + ".cir"
        circuit = SpiceParser("Subcircuits/PabloNL.cir").build_circuit()
        circuit.include("Subcircuits/ad633.cir")
        circuit.include("Subcircuits/analog.lib")
        print(circuit)
        with open(self.netlist, "w") as file: 
            file.write(str(circuit))

        self.control = [
            ".control", 
            simCommand, 
            wrdata_str, 
            "exit", 
            ".endc", 
            ".end"
        ]

    def setA(a):
        test = 5
    
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
        path = self.append_control(self.netlist, self.control)
        command = ["ngspice", path]
        subprocess.run(command)
        

if __name__ == "__main__":
    nodes = ["VIn"]
    parameters = [
        (nodes, "dc v1 -5 5 1m"), 
    ]
# Run NgSpice simulation
    with Pool(processes=3) as pool:
        pool.map(worker, parameters)

# data = np.loadtxt('Output/outputData.txt')

# # Calculate the number of plots
# num_plots = len(nodes)

# # Configure plot bounds (change these values as needed)
# x_min = -10
# x_max = 10
# y_min = -10
# y_max = 10

# # Create a plot
# plt.figure(figsize=(10, 6))

# # Iterate over each pair of columns and plot them
# for i in range(num_plots):
#     x = data[:, 2*i]
#     y = data[:, 2*i + 1]
#     plt.plot(x, y, label=nodes[i])

# # Set bounds for the plot
# plt.xlim([x_min, x_max])
# plt.ylim([y_min, y_max])

# plt.xlabel('X Values')
# plt.ylabel('Y Values')
# plt.title('Multiple Plots')
# plt.grid(True)
# plt.legend()

# # Display the plot
# plt.show()