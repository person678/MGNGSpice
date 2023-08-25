import numpy as np
from scipy.interpolate import interp1d

# Load data from the text file
def prepare_output(filename, param):

    data = np.loadtxt(filename)

    # Assuming the first column is time and the second column is voltage
    time = data[:, 0]
    voltage = data[:, 1]

    # Removing duplicate time values and corresponding voltage values
    _, unique_indices = np.unique(time, return_index=True)
    time = time[unique_indices]
    voltage = voltage[unique_indices]

    # Define the desired timestep
    theta = 30e-6

    # Define the times where you want to estimate voltage
    time_query = np.arange(0, np.max(time), theta)

    # Interpolate the voltage values at the desired times
    interpolator = interp1d(time, voltage, fill_value="extrapolate")
    voltage_interp = interpolator(time_query)

    # Take only the desired portion of the voltage data
    N = 100
    voltage_interp = voltage_interp[:N * 1000]

    # Remove the first 100 values
    voltage_interp = voltage_interp[100:]

    # Write the interpolated voltage data to a new text file
    path = param + "_processed.txt"
    np.savetxt(path, voltage_interp, fmt="%.15f")
    return path