import subprocess
import os
import numpy as np
import matplotlib.pyplot as plt

import tempfile
import shutil
import random

from multiprocessing import Pool, Process, Queue

import re

import time

from NetlistParser import *

# This is for for batchprocessing. Ran once for each sim. 
def worker(params):
    nodes, command, *param_names_and_values = params
    print(command)
    sim = Simulation(nodes, command, "Subcircuits/ParamTest", param_names_and_values)
    sim.runSim()
    os.remove(sim.netlist_path)

    if any("PWL" in item for item in param_names_and_values):
        
        print("PWL detected! not writing values to CSV.")
        return {
            'fileID' : sim.temp_id,
            'node': nodes,
            'command': command,
            'parameters': param_names_and_values[:-1]
        }
    else: 
        return {
            'filename' : sim.temp_id,
            'node': nodes,
            'command': command,
            'parameters': param_names_and_values
        }


class Simulation: 
    
    def __init__(self, nodes, simCommand, netlist, param_names_and_values):
        param_str = ""
        nodes_str = "" .join(["V(" + node + ")" for node in nodes])
        # Generates the temp file for the altered netlist. 
        self.temp_id = str(random.randint(1, 100000))
        wrdata_str = "wrdata Output/" + self.temp_id + ".txt " + nodes_str
        self.netlist_path = netlist + self.temp_id + ".cir"
        netlist = netlist + ".cir"

        with open(netlist, "r") as f:
            circuit = f.read()
        with open(self.netlist_path, "w") as file: 
            file.write(circuit)
        self.control = [
            ".control", 
            simCommand, 
            wrdata_str, 
            "exit", 
            ".endc", 
            ".end"
        ]

        # Change the Parameters. 
        for i in range(0, len(param_names_and_values), 2):
            name, value = param_names_and_values[i], param_names_and_values[i + 1]
            self.change_component(name, value)

    def setNLparams(self, target, value):
        # This method allows us to configure key parameters of the NL circuit. 
        # Targets: 
        # a, b, d: ratio of two resistors, see circuit diagram

        # Define configurable values
        b_base_value = 10.0  # 10k for b components
        d_base_value = 2.0  # 2k for d components

        # Read all lines from the netlist file
        with open(self.netlist_path, "r") as file:
            lines = file.readlines()

        # Iterate over lines to adjust values based on target
        for i, line in enumerate(lines):
            parts = line.strip().split()

            # Adjust values for target 'a'
            if target == 'a':
                if len(parts) > 1 and parts[0] == "RF2":
                    lines[i] = "RF2 NLA2Neg 0 1k\n"
                elif len(parts) > 1 and parts[0] == "RF1":
                    lines[i] = f"RF1 Mult1In NLA2Neg {value}k\n"

            # Adjust values for target 'b'
            elif target == 'b':
                if len(parts) > 1 and parts[0] == "R2":
                    lines[i] = f"R2 RtoPot NLA3Pos {b_base_value * (1-value)}k\n"
                elif len(parts) > 1 and parts[0] == "R3":
                    lines[i] = f"R3 NLA3Pos 0 {b_base_value * value}k\n"

            # Adjust values for target 'd'
            elif target == 'd':
                if len(parts) > 1 and parts[0] == "R4":
                    lines[i] = f"R4 0 Mult3Y2 {d_base_value * value}k\n"
                elif len(parts) > 1 and parts[0] == "R5":
                    lines[i] = f"R5 Mult3Y2 R5toR6 {d_base_value * (1-value)}k\n"

        # Write the updated lines back to the netlist file
        with open(self.netlist_path, "w") as file:
            file.writelines(lines)


    # Currently can handle the a, b, and d resistor ratios, and changing resistors. 
    # Can also specify the source for PWL input. 
    def change_component(self, name, value):
        if name in ("a", "b", "d"):
            self.setNLparams(name, value)
        elif re.match(r'^R[A-Z0-9]{1,3}$', name):
            self.setComponentValue(name, value)
        elif "PWL" in value:
            print("PWL detected! Changing " + name + " in file.")
            self.setComponentValue(name, value)


    def setComponentValue(self, name, value):
    # Changes a component value in the netlist. 
    # Name must be the label at the start of th line, i.e. "R2"
    # Note that scientific units will be left untouched. 
    # Read all lines from the netlist file
        with open(self.netlist_path, "r") as file:
            lines = file.readlines()

        # Check if the value provided has a unit (like 'k', 'm', etc.)
        value_str = str(value)
        if not value_str[-1].isdigit():
            unit = value_str[-1]
            numeric_part = value_str[:-1]
        else:
            unit = ""
            numeric_part = value_str

        # Iterate over lines to adjust values based on the provided name
        for i, line in enumerate(lines):
            parts = line.strip().split()

            # Check if the first part of the line matches the provided name
            if len(parts) > 1 and parts[0] == name:
                # Replace the value in the circuit with the provided value
                parts[-1] = numeric_part + unit
                lines[i] = ' '.join(parts) + '\n'
                break

        # Write the updated lines back to the netlist file
        with open(self.netlist_path, "w") as file:
            file.writelines(lines)

        
    
    def append_control(self, filename, content_list):
        """
        Copy contents of the given file and append a list of strings to a temporary file.

        Parameters:
        - filename (str): The path of the source file.
        - content_list (List[str]): A list of strings to be appended to the file.

        Returns:
        - str: The path to the temporary file.
        """
        print(content_list)
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
        print(self.control)
        path = self.append_control(self.netlist_path, self.control)
        command = ["ngspice", path]
        subprocess.run(command)
        


# Guard needed for multithreading. Program entry point. 
if __name__ == "__main__":
    nodes, command, params = parse_config("sim.config")
    sim_params = generate_parameters(nodes, command, params)

# Run NgSpice simulation
    with Pool(processes=3) as pool:
        results = pool.map(worker, sim_params)
    with open('Output/run_config.csv', 'w', newline='') as csvfile:
        fieldnames = ['fileID', 'node', 'command', 'parameters']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        
        writer.writeheader()
        for result in results:
            writer.writerow(result)

        
