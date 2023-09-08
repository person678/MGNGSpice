import csv
import numpy as np
import prepare_output as po
from mc_benchmark import mc_benchmark
import matplotlib.pyplot as plt
import seaborn as sns
import os

def save_heatmap(scores, param1_values, param2_values, param1_name, param2_name, fixed_param_name, fixed_param_value):
    plt.figure(figsize=(10, 6))
    sns.heatmap(scores, annot=True, cmap='viridis', xticklabels=param2_values, yticklabels=param1_values)
    plt.xlabel(param2_name + ' Value')
    plt.ylabel(param1_name + ' Value')
    plt.title(f'Benchmark Score Heatmap (Fixed {fixed_param_name} = {fixed_param_value})')
    plt.savefig(f'Output/{EXPERIMENT_NAME}/Heatmaps/{fixed_param_name}_{fixed_param_value}.png')
    plt.close()


EXPERIMENT_NAME = "ShiftScalingSweepBDMixCheckingSpread"

# Generates a heatmap using the two varying parameters in a run. Will not work correctly 
# if more or less are present. 
# Lists to store unique parameter values
param1_values = set()
param2_values = set()
param3_values = set()

# Dictionary to store scores
score_dict = {}

with open(f"Output/{EXPERIMENT_NAME}/run_config.csv", 'r') as file:
    reader = csv.reader(file)
    next(reader)  # Skip the header
    
    for row in reader:
        file_id, nodes_str, _, params = row
        nodes = eval(nodes_str)
        file_name = f'Output/{EXPERIMENT_NAME}/{file_id}.txt'
        param_list = eval(params)
        try:
            # Looks for the first and third column for the parameter being varied. 
            # Might be worth adding logic to make sure it ignores any constant parameters. 
        
            param1_name = param_list[0]
            param2_name = param_list[2]
            param3_name = param_list[4]
            
            param2_value = float(param_list[3])
            param1_value = float(param_list[1])
            param3_value = float(param_list[5])
            
            param2_values.add(param2_value)
            param1_values.add(param1_value)
            param3_values.add(param3_value)

            param_str = ' '.join(param_list)
            path = po.prepare_output(file_name, param_str)
            score = mc_benchmark(path)
            os.remove(path)

            score_dict[(param2_value, param1_value, param3_value)] = score
        except (ValueError, IndexError) as e:
            print(e)
            continue

# Convert sets to sorted lists for consistent indexing
param1_values = sorted(list(param1_values))
param2_values = sorted(list(param2_values))
param3_values = sorted(list(param3_values))

# Create a 2D array to store scores
scores = np.zeros((len(param1_values), len(param2_values), len(param3_values)))

# Populate scores array
for k, r3 in enumerate(param3_values):
    for i, r1 in enumerate(param1_values):
        for j, r2 in enumerate(param2_values):
            scores[i, j, k] = score_dict.get((r2, r1, r3), 0)  # Default to 0 if no score available for that combination

# Create a heatmap
for k in param3_values:
    plt.figure(figsize=(10, 6))
    scores_for_fixed_param = scores[::, ::, param3_values.index(k)]
    sns.heatmap(scores_for_fixed_param, annot=True, cmap='viridis', xticklabels=param2_values, yticklabels=param1_values)
    plt.xlabel(param2_name + ' Value')
    plt.ylabel(param1_name + ' Value')
    plt.title('MC Score - Sweep B D & Mix, Mix fixed')
    plt.savefig(f'Output/{EXPERIMENT_NAME}/Heatmaps/{param3_name}={k}_param1_{param1_name}_param2_{param2_name}.png')
    plt.close()


for k in param1_values:
    plt.figure(figsize=(10, 6))
    scores_for_fixed_param = scores[::, param1_values.index(k), ::]
    sns.heatmap(scores_for_fixed_param, annot=True, cmap='viridis', xticklabels=param2_values, yticklabels=param3_values)
    plt.xlabel(param2_name + ' Value')
    plt.ylabel(param3_name + ' Value')
    plt.title('MC Score - Sweep B D & Mix, Mix fixed')
    plt.savefig(f'Output/{EXPERIMENT_NAME}/Heatmaps/{param1_name}={k}_param2_{param2_name}_param3_{param3_name}.png')
    plt.close()


for k in param2_values:
    plt.figure(figsize=(10, 6))
    scores_for_fixed_param = scores[::, param2_values.index(k), ::]
    sns.heatmap(scores_for_fixed_param, annot=True, cmap='viridis', xticklabels=param3_values, yticklabels=param1_values)
    plt.xlabel(param3_name + ' Value')
    plt.ylabel(param1_name + ' Value')
    plt.title('MC Score - Sweep B D & Mix, Mix fixed')
    plt.savefig(f'Output/{EXPERIMENT_NAME}/Heatmaps/{param2_name}={k}_param1_{param1_name}_param3_{param3_name}.png')
    plt.close()

