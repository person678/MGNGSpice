import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import Normalize
from scipy.signal import resample

# This script graphs a heatmap of the voltage values fed in (measured from the input to the NL ideally)
# and maps them on the the measured NL curve, to predict the NL circuit operating region.  

experimentName = "MoreAccurateThetaTest1"
file_id = "18579"
data = np.loadtxt(f"Output/{experimentName}/{file_id}DCSweep.txt")
x_dc = data[:,0]
y_dc = data[:,1]

# Pad 500 zeroes to the begining - Comment out if including negative half of cycle
# in the DC sweep
neg_x = np.linspace(-10, 0, 1000)
x_dc = np.concatenate((neg_x, x_dc))
y_dc = np.pad(y_dc, (1000, 0), 'constant', constant_values=0)

# Resample y_dc to have the same number of points as x_dc
y_dc = resample(y_dc, len(x_dc))

# Generate some example voltage readings (replace with your real data)
#voltage_readings = np.random.normal(0, 5, 1000)  # Random data centered around 0
voltage_readings = np.loadtxt(f"Output/{experimentName}/{file_id}.txt")
voltage_readings = voltage_readings[:, 1]
# Initialize an array to store the counts
counts = np.zeros_like(x_dc)

# Tolerance value
tolerance = 0.05

# Step 1: Count occurrences within tolerance around each DC voltage value
for i, x_val in enumerate(x_dc):
    counts[i] = np.sum(np.abs(voltage_readings - x_val) < tolerance)

# Step 2: Normalize the counts
norm = Normalize(vmin=0, vmax=counts.max())

# Step 3: Plot the DC curve with heatmap
plt.figure()
plt.rc('axes', axisbelow=True)
plt.grid()
sc = plt.scatter(x_dc, y_dc, c=counts, cmap='inferno', norm=norm)
plt.colorbar(sc, label='Frequency')
plt.xlabel('DC Voltage')
plt.ylabel('Response')
plt.title('DC Curve with Heatmap')
plt.show()
