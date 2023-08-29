import csv
import numpy as np
import prepare_output as po
import mc_benchmark as mc
import matplotlib.pyplot as plt
import os

# Lists to store parameter values and corresponding scores
param_values = []
scores = []

with open('Output/run_config.csv', 'r') as file:
    reader = csv.reader(file)
    next(reader)  # Skip the header
    
    for row in reader:
        file_id, nodes_str, _, params = row
        nodes = eval(nodes_str)  # Convert string representation of list to actual list
        
        file_name = f'Output/{file_id}.txt'
        param_list = eval(params)
        
        # Find index of 'RIAF2' in the parameter list
        try:
            param_name = param_list[0] # Extract the parameter name
            param_value = float(param_list[1])  # Extract the value for the parameter
            param_values.append(param_value)
            
            param_str = ' '.join(param_list)
            path = po.prepare_output(file_name, param_str)
            score = mc.mc_benchmark(path)
            os.remove(path)
            scores.append(score)
        except (ValueError, IndexError):
            # This will skip cases where the value after 'RIAF2' is not a float or there's no value after 'RIAF2'
            continue

# Now that you have the parameter values and scores, you can plot them
plt.figure(figsize=(10, 6))
plt.plot(param_values, scores, '-o')
plt.xlabel(param_name + ' Value')
plt.ylabel('Benchmark Score')
plt.title('Benchmark Score vs ' + param_name + ' Value')
plt.grid(True)
plt.show()