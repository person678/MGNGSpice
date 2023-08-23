import itertools
import os 
import csv

# Parses the file specifying simulation parameters. 
def parse_config(file_name):
    """
    Parses the config file, specifying simulation commmands. 
    Supports: 
    Resistor stepping: syntax "Rx start value end value step value" "RX start 1000 end 2000 step 100"
    sim command: syntax "sim tran interval end" i.e. "sim tran 1m 1s"
    a, b or d resistor ratios: syntax "a start 1000 end 2000 step 100"
    """
    params = {}
    nodes = []
    command = ""
    
    with open(file_name, 'r') as file:
        for line in file:
            line = line.strip()
            parts = line.split()
            
            # Allows for comment lines begininng with *
            if line.startswith("*"): 
                continue
            # Handles sim command. 
            elif line.startswith("sim"):
                if command != "":
                    print("Error! Seccond sim command detected.")
                    exit()
                command = line.replace("sim", "", 1).strip()
            elif line.startswith("measure"):
                for part in parts[1:]:
                    nodes.append(part)

            elif "FILE=" in line and "V" in parts[0]:
                voltage_name = parts[0]
                filepath = line.split("FILE=")[1].strip("{}")
                
                # Read the PWL file and format it for NGSpice
                with open(filepath, 'r') as pwl_file:
                    formatted_data = ["PWL("]
                    for pwl_line in pwl_file:
                        time, voltage = pwl_line.strip().split()
                        formatted_data.append(f"{time} {voltage}")
                    formatted_data.append(")")

                params[voltage_name] = ' '.join(formatted_data)  # Adding to params

            else:
                name, _, start_value, _, end_value, _, step_value = parts
                params[name] = (float(start_value), float(end_value), float(step_value))
    
    return nodes, command, params

 # Generates the list of parameters needed for the worker multithreading. 
def generate_parameters(nodes, command, config_params):
    sim_params = []
    all_ranges = []
    param_names = []
    pwl = []
    
    for name, value in config_params.items():
        if isinstance(value, tuple) and len(value) == 3:  # It's a ranged parameter
            start, end, step = value
            all_ranges.append(list(frange(start, end, step)))
            param_names.append(name)
        else:  # It's the PWL data
            pwl.append([value])
            pwl.append(name)

    # Ensures PWL data always at end of parameter list.
    if pwl:        
        all_ranges.append(pwl[0])
        param_names.append(pwl[1])
    for combination in itertools.product(*all_ranges):
        combination_str = [str(val) for val in combination]
        param_and_values = list(itertools.chain(*zip(param_names, combination_str)))
        sim_params.append((nodes, command, *param_and_values))
    print(sim_params)

    return sim_params

# Support method for generating list. Needed for handing stepped parameters. 
def frange(start, end, step):
    current = start
    while current <= end:
        yield round(current, 10)  # round to 10 decimal places for precision
        current += step

# Ensures any includes in netlist point to absolute path. 
def replace_with_absolute_paths(file_name):
    # Get the directory containing the netlist file
    base_dir = os.path.dirname(os.path.abspath(file_name))
    
    new_lines = []
    
    with open(file_name, 'r') as file:
        for line in file:
            # Check if the line starts with .include
            if line.strip().startswith(".include"):
                # Split the line and get the path
                parts = line.split()
                if len(parts) > 1:
                    relative_path = parts[1]
                    # Create an absolute path
                    absolute_path = os.path.join(base_dir, relative_path)
                    # Replace the relative path with the absolute path in the line
                    line = line.replace(relative_path, absolute_path)
            
            new_lines.append(line)
    
    # Write the modified lines back to the file
    with open(file_name, 'w') as file:
        file.writelines(new_lines)

def write_to_csv(params, result_filepath, csv_filepath="simulations.csv"):
    with open(csv_filepath, 'a', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(params + [result_filepath])

