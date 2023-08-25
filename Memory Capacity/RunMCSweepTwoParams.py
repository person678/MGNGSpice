import csv
import numpy as np
import prepare_output as po
from mc_benchmark import mc_benchmark
import matplotlib.pyplot as plt
import seaborn as sns

# Lists to store unique parameter values
param1_values = set()
param2_values = set()

# Dictionary to store scores for combinations of RIAF1 and RIAF2
score_dict = {}

with open('Output/run_config.csv', 'r') as file:
    reader = csv.reader(file)
    next(reader)  # Skip the header
    
    for row in reader:
        file_id, nodes_str, _, params = row
        nodes = eval(nodes_str)
        file_name = f'Output/{file_id}.txt'
        param_list = eval(params)
        try:

            param1_name = param_list[0]
            param2_name = param_list[2]
            
            param2_value = float(param_list[3])
            param1_value = float(param_list[1])
            
            param2_values.add(param2_value)
            param1_values.add(param1_value)

            param_str = ' '.join(param_list)
            path = po.prepare_output(file_name, param_str)
            score = mc_benchmark(path)

            score_dict[(param2_value, param1_value)] = score
        except (ValueError, IndexError):
            continue

# Convert sets to sorted lists for consistent indexing
param1_values = sorted(list(param1_values))
param2_values = sorted(list(param2_values))

# Create a 2D array to store scores
scores = np.zeros((len(param1_values), len(param2_values)))

# Populate scores array
for i, r1 in enumerate(param1_values):
    for j, r2 in enumerate(param2_values):
        scores[i, j] = score_dict.get((r2, r1), 0)  # Default to 0 if no score available for that combination

# Create a heatmap
plt.figure(figsize=(10, 6))
sns.heatmap(scores, annot=True, cmap='viridis', xticklabels=param2_values, yticklabels=param1_values)
plt.xlabel(param2_name + ' Value')
plt.ylabel(param1_name + ' Value')
plt.title('Benchmark Score Heatmap')
plt.show()
