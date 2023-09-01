import subprocess
import os

import random

from multiprocessing import Pool

import re

import csv

import numpy as np

from NetlistParser import *

#-------------------------------------------------------
# MISC INFO
#-------------------------------------------------------
# Need to have "* Title TitleOfCircuit" line in circuit file for NGSpice to like it. 

# This is for for batchprocessing. Ran once for each sim. 
def worker(params):
    nodes, command, *param_names_and_values = params
    netlist = "Subcircuits/CircuitWrapper"
    sim = Simulation(nodes, command, netlist, param_names_and_values)
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
            'fileID' : sim.temp_id,
            'node': nodes,
            'command': command,
            'parameters': param_names_and_values
        }


class Simulation: 
    
    def __init__(self, nodes, simCommand, netlist, param_names_and_values):
        # Generate strings for control command. 
        self.originalNetlist = netlist
        self.paramNamesAndValues = param_names_and_values
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

# This is for the commands to be sent to NGSpice. See NGSpice control language documentation. 
        self.control = [
            # This save command isn't for the control language, it ensures only the relevant nodes are saved.
            # Fun fact: Without this, a 3 parameter sweep tried to use 40GB of RAM. With it, about 150MB. 
            ".save " + nodes_str, 
            ".control", 
            simCommand, 
            wrdata_str, 
            "exit", 
            ".endc", 
            ".end"
        ]

        self.unwrap_include("PabloNL.cir")
        self.unwrap_include("DelayLine.cir")
        self.unwrap_include("InputAmp.cir")
        self.unwrap_include("Integrator.cir")


        # Change the Parameters. 
        for i in range(0, len(param_names_and_values), 2):
            name, value = param_names_and_values[i], param_names_and_values[i + 1]
            self.change_component(name, value)

    def setInputFeedbackMix(self, mix):
        mix = float(mix)
        # This method allows us configure the ratio of feedback  to input mix. 
        # mix: ratio of input to delay line. 
        # E.g. 2 doubles the contribution of the input, halves the feedback. 

        inputString = f"EInScale VInScaled 0 vol = '(1.9 + (V(VIn) * 3.8)) * {round(mix, 3)}'\n"
        feedbackString = f"EFBScale FeedbackScaled 0 vol = '(V(DLOut)/4.67 - 0.5) * {round(1/mix, 3)}'\n"
        self.setRangeScalingInNetlist(inputString, feedbackString)

    def setRangeScalingInNetlist(self, inputRange, outputMax):
    # Read all lines from the netlist file
        try:
            mix = round(float(self.mix), 3)
        except:
            print("Exception when trying to retrieve Mix value - assuming not provided in config file.")
            print("Defaulting to equal mix.")
            mix = 1

        with open(self.netlist_path, "r") as file:
            lines = file.readlines()

        # Iterate over lines to adjust values based on target
        for i, line in enumerate(lines):
            parts = line.strip().split()

            if len(parts) > 1 and parts[0] == "EInScale":
                #lines[i] = f"EInScale VInScaled 0 vol = '(1.9 + (V(VIn) * 3.8)) * {round(mix, 3)}'\n"
                newLine = "EInScale VInScaled 0 vol = "
                eq = "'(" + str(round(inputRange/2, 3)) + " + (V(VIn) * " + str(inputRange) +")) * " + str(mix) + "'\n"
                lines[i] = newLine + eq
                continue

            elif len(parts) > 1 and parts[0] == "EFBScale":
                newLine = "EFBScale FeedbackScaled 0 vol = "
                eq = "'(V(" + self.delayTap + ")" + "/" + str(outputMax) + "- 0.5 ) * " + str(round(1/mix, 3)) + "'\n"
                lines[i] = newLine + eq
                continue

        # Write the updated lines back to the netlist file
        with open(self.netlist_path, "w") as file:
            file.writelines(lines)

    # Currently can handle the a, b, and d resistor ratios, and changing resistors. 
    # Can also specify the source for PWL input. 
    def change_component(self, name, value):
        if name in ("a", "b", "d"):
            setNLparams(self.netlist_path, name, value)
        elif re.match(r'^R[A-Z0-9]{1,6}$', name):
            setComponentValue(self.netlist_path, name, value)
        elif "PWL" in value:
            print("PWL detected! Changing " + name + " in file.")
            setComponentValue(self.netlist_path, name, value)
        elif "mix" in name:
            # This is set along with the range scaling later
            self.mix = value
        elif "delay" in name:
            value = int(float(value))
            self.setDelayTap(value)
        else: 
            print("Error! Tried to change component, but didn't match any known format. ")
            print("Component: " + name + ", Value: " + value)
            exit()

    def setDelayTap(self, stage):
        self.delayTap = "Delay_LineDL" + str(stage)

        with open(self.netlist_path, "r") as file:
            lines = file.readlines()

        # Create a list to hold updated lines
        updated_lines = []

        # Iterate over lines to adjust
        for index, line in enumerate(lines):
            if "DLOut" in line:
                # Replace and update the line
                new_line = line.replace("DLOut", self.delayTap)
                updated_lines.append(new_line)
            else:
                # Append the original line if no replacement is made
                updated_lines.append(line)

        # Write the updated lines back to the netlist file
        with open(self.netlist_path, "w") as file:
            file.writelines(updated_lines)
    
    def unwrap_include(self, target_filename):
        new_content = []

        with open(self.netlist_path, 'r') as main_file:
            for line in main_file:
                stripped_line = line.strip()
                # Check for the .include directive
                if stripped_line.startswith(".include") and stripped_line.endswith(target_filename):
                    # Extract path from the line
                    include_path = stripped_line.split()[-1]
                    # Read the .cir file
                    with open(include_path, 'r') as include_file:
                        cir_content = include_file.readlines()
                        new_content.extend(cir_content)
                    # Ensure the last line has a newline
                        if cir_content and not cir_content[-1].endswith('\n'):
                            new_content.append('\n')
                else:
                    new_content.append(line)

        # Write the modified content back to the main file
        with open(self.netlist_path, 'w') as main_file:
            main_file.writelines(new_content)


    def calculateRangeScaling(self):
        sweepControl = self.control
        for index, value in enumerate(sweepControl):
            if "tran" in value:
                sweepControl[index] = "dc VIn 0 10 1m"
            
            elif ".save" in value:
                sweepControl[index] = ".save V(NLOut)"
            elif "wrdata" in value:
                parts = value.split()
                outputFile = parts[1]
                sweepControl[index] = parts[0] + " " + parts[1] + " " + "V(NLOut)"

        # Create the netlist with just the NL circuit. 
        sweepNetlistPath = self.originalNetlist + self.temp_id + "DCSweep" + ".cir"

        with open("Subcircuits/PabloNLSolo.cir", "r") as f:
            circuit = f.read()
                
        with open(sweepNetlistPath, "w") as file: 
            file.write(circuit)
        
        # Change the Parameters. 
        for i in range(0, len(self.paramNamesAndValues), 2):
            name, value = self.paramNamesAndValues[i], self.paramNamesAndValues[i + 1]
            if name in ("a", "b", "d"):
                setNLparams(sweepNetlistPath, name, value)
            elif re.match(r'^R[A-Z0-9]{1,6}$', name):
                setComponentValue(sweepNetlistPath, name, value)

        path = append_list_to_file(sweepNetlistPath, sweepControl)
        command = ["ngspice", path, "-b"]
        subprocess.run(command)

        # Load your data
        # Assuming your file is tab-separated and has two columns: input voltage and output voltage
        data = np.loadtxt(outputFile)
        input_voltage = data[:, 0]
        output_voltage = data[:, 1]

        # Compute the gradient of the output voltage with respect to the input voltage
        gradient = np.gradient(output_voltage, input_voltage)

        # 1. Find the maximum output voltage and its corresponding input
        max_output_index = np.argmax(output_voltage)
        max_output = output_voltage[max_output_index]
        input_at_max = input_voltage[max_output_index]

        # 2. Find the minimum input voltage that starts to produce a change
        # Look for the index where the gradient first reduces to a tenth of its maximum value
        max_gradient = np.max(np.abs(gradient))
        threshold_low = max_gradient / 10
        min_input_index_low = np.where(np.abs(gradient) >= threshold_low)[0][0]
        min_input_low = input_voltage[min_input_index_low]

        # 3. Find the input voltage where the output returns close to zero after the peak
        # Look for the index where the gradient becomes positive and changes very slightly
        for i in range(max_output_index + 1, len(gradient) - 1):
            if gradient[i] > 0 and np.abs(gradient[i] - gradient[i+1]) < 1e-3:
                min_input_high = input_voltage[i]
                break

        print(f"Maximum output voltage: {max_output} V, at input voltage: {input_at_max} V")
        print(f"Minimum input voltage that starts to produce a change: {min_input_low} V")
        print(f"Input voltage where output returns close to zero after peak: {min_input_high} V")

        return max_output, min_input_high


    def runSim(self):
        # Don't think printing system this works correctly - FIX. 
        components_to_print = ["a", "b", "d" "RNLF1", "RNLF2", "RIN1", "RIN2", "RIAF1", "RIAF2", "RINTAF1", "RINTAF2"]
        print_components(self.netlist_path, components_to_print, "Output/KeyComponentValues.txt")
        path = append_list_to_file(self.netlist_path, self.control)
        outputMax, inputRange = self.calculateRangeScaling()
        self.setRangeScalingInNetlist(inputRange, outputMax)
        command = ["ngspice", path, "-b"]
        subprocess.run(command)
        


# Guard needed for multithreading. Program entry point. 
if __name__ == "__main__":
    # Reads in sim parameters from the config file. 
    nodes, command, params = parse_config("sim.config")
    sim_params = generate_parameters(nodes, command, params)

# Run NgSpice simulation

    with Pool(processes=8) as pool:
        results = pool.map(worker, sim_params)
    with open('Output/run_config.csv', 'w', newline='') as csvfile:
        fieldnames = ['fileID', 'node', 'command', 'parameters']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        
        writer.writeheader()
        for result in results:
            writer.writerow(result)

        
