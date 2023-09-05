import itertools
import os 
import csv
import tempfile
import shutil

# This file contains various methods for handling:
# Parsing the config file. 
# Generating parameters. 
# Editing the netlist. 

# Parses the file specifying simulation parameters. 
def parse_config(file_name):
    """
    Parses the config file, specifying simulation commmands. 
    Supports: 
    Resistor stepping: syntax "Rx start value end value step value" "RX start 1000 end 2000 step 100"
    sim command: syntax "sim tran interval end" i.e. "sim tran 1m 1s"
    a, b or d resistor ratios: syntax "a start 1000 end 2000 step 100"
    set commands: syntax "R1 set 1000" sets a component to that value for all runs
    set input / feedback mix: syntax "mix set 0.5" or "mix start 0.1 stop 1 step 0.2", 
    default is 1, higher number is more input lower feedback
    """
    params = {}
    nodes = []
    command = ""
    
    with open(file_name, 'r') as file:

        try: 
            for line in file:
                line = line.strip()
                parts = line.split()

                # Allows for comment lines begininng with *, or empty spacing lines
                if line.startswith("*") or line == "": 
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
                
                # Handles the case "Component set X"
                elif "set" in line:
                    name, _, value = parts
                    params[name] = (float(value),) 

                else:

                    name, _, start_value, _, end_value, _, step_value = parts
                    params[name] = (float(start_value), float(end_value), float(step_value))
        except Exception as e: 
            print("Error parsing config file! Check for typos/syntax errors?")
            exit(1)

    return nodes, command, params

 # Generates the list of parameters needed for the worker multithreading. 
def generate_parameters(nodes, command, config_params):
    sim_params = []
    all_ranges = []
    param_names = []
    pwl = []
    
    for name, value in config_params.items():

        try: 

            if isinstance(value, tuple) and len(value) == 3:  # It's a ranged parameter
                start, end, step = value
                all_ranges.append(list(frange(start, end, step)))
                param_names.append(name)

            elif isinstance(value, tuple) and len(value) == 1: # It's a set command.
                all_ranges.append(value)
                param_names.append(name)

            elif "PWL" in value:  # It's the PWL data
                pwl.append([value])
                pwl.append(name)

        # Ensures PWL data always at end of parameter list.
            if pwl:        
                all_ranges.append(pwl[0])
                param_names.append(pwl[1])
        except Exception as e:
            print("Error generating parameter list! Check config file syntax?")
            exit(1)

    for combination in itertools.product(*all_ranges):
        combination_str = [str(val) for val in combination]
        param_and_values = list(itertools.chain(*zip(param_names, combination_str)))
        sim_params.append((nodes, command, *param_and_values))

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

def parse_value(value_str):
    """
    Converts a value from string with possible engineering notation to float.
    
    Parameters:
    - value_str (str): A string representation of the value (like '1k', '5M', etc.)
    
    Returns:
    - float: The value in float format.
    """
    
    multiplier = 1
    if value_str[-1].lower() == 'k':
        multiplier = 1e3
    elif value_str[-1].lower() == 'm':
        multiplier = 1e6
    return float(value_str[:-1]) * multiplier if multiplier != 1 else float(value_str)

def print_components(netlist_path, components, output_file):


    extracted_data = []
    special_components = {"a": ["RNLF1", "RNLF2"], 
                           "b": ["RNL2", "RNL3"], 
                           "d": ["RNL4", "RNL5"]}
    
    resistors_values = {comp: [] for comp in special_components}

    with open(netlist_path, 'r') as f:
        for line in f:
            tokens = line.split()
            
            # Regular components extraction
            if tokens and tokens[0] in components and tokens[0] not in special_components:
                component_name = tokens[0]
                component_value = tokens[-1]
                extracted_data.append((component_name, component_value))
            
            # Check for the special components' resistors
            for special, related_resistors in special_components.items():
                if tokens and tokens[0] in related_resistors:
                    resistors_values[special].append(parse_value(tokens[-1]))

    # Compute the special values based on the resistor values
    for special, values in resistors_values.items():
        if len(values) == 2:
            if special == 'a':
                resistors_values['a'] = values[1] / values[0]
            elif special == 'b' or special == 'd':
                resistors_values[special] = values[0] / (values[0] + values[1])
    
    # Write to the output file
    with open(output_file, 'w') as f:
        for name, value in extracted_data:
            f.write(f"{name} {value}\n")
        
        for name, value in resistors_values.items():
            if type(value) is not list:
                f.write(f"{name} {value}\n")

def setComponentValue(path, name, value):
    # Changes a component value in the netlist. 
    # Name must be the label at the start of th line, i.e. "R2"
    # Note that scientific units will be left untouched. 
    # Read all lines from the netlist file
        with open(path, "r") as file:
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
        with open(path, "w") as file:
            file.writelines(lines)

def setNLparams(path, target, value):
        value = float(value)
        # This method allows us to configure key parameters of the NL circuit. 
        # Targets: 
        # a, b, d: ratio of two resistors, see circuit diagram

        # Define configurable values
        b_base_value = 10.0  # 10k for b components
        d_base_value = 2.0  # 2k for d components

        # Read all lines from the netlist file
        with open(path, "r") as file:
            lines = file.readlines()

        # Iterate over lines to adjust values based on target
        for i, line in enumerate(lines):
            parts = line.strip().split()

            # Adjust values for target 'a'
            if target == 'a':
                if len(parts) > 1 and parts[0] == "RNLF2":
                    lines[i] = "RNLF2 NLA2Neg 0 1k\n"
                elif len(parts) > 1 and parts[0] == "RNLF1":
                    lines[i] = f"RNLF1 Mult1In NLA2Neg {value}k\n"

            # Adjust values for target 'b'
            elif target == 'b':
                if len(parts) > 1 and parts[0] == "RNL2":
                    lines[i] = f"RNL2 RtoPot NLA3Pos {b_base_value * (1-value)}k\n"
                elif len(parts) > 1 and parts[0] == "RNL3":
                    lines[i] = f"RNL3 NLA3Pos 0 {b_base_value * value}k\n"

            # Adjust values for target 'd'
            elif target == 'd':
                if len(parts) > 1 and parts[0] == "RNL4":
                    lines[i] = f"RNL4 0 Mult3Y2 {d_base_value * value}k\n"
                elif len(parts) > 1 and parts[0] == "RNL5":
                    lines[i] = f"RNL5 Mult3Y2 R5toR6 {d_base_value * (1-value)}k\n"

        # Write the updated lines back to the netlist file
        with open(path, "w") as file:
            file.writelines(lines)

def append_list_to_file(filename, content_list):
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