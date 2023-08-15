from pathlib import Path

import math 
import matplotlib.pyplot as plt

import PySpice.Logging.Logging as Logging
logger = Logging.setup_logging()


from PySpice.Doc.ExampleTools import find_libraries
from PySpice.Probe.Plot import plot
from PySpice.Spice.Library import SpiceLibrary
from PySpice.Spice.Netlist import SubCircuitFactory
from PySpice.Spice.Parser import SpiceParser
from PySpice.Spice.NgSpice.Shared import NgSpiceShared
from PySpice.Unit import *

import csv

class MyNgSpiceShared(NgSpiceShared):


    def __init__(self, amplitude, frequency, **kwargs):

        super().__init__(**kwargs)

        self._amplitude = amplitude
        self._pulsation = float(frequency.pulsation)


    def get_vsrc_data(self, voltage, time, node, ngspice_id):
        self._logger.debug('ngspice_id-{} get_vsrc_data @{} node {}'.format(ngspice_id, time, node))
        voltage[0] = self._amplitude * math.sin(self._pulsation * time)
        return 0


    def get_isrc_data(self, current, time, node, ngspice_id):
        self._logger.debug('ngspice_id-{} get_isrc_data @{} node {}'.format(ngspice_id, time, node))
        current[0] = 1.
        return 0


libraries_path = find_libraries()
spice_library = SpiceLibrary(libraries_path)

# Parses the existing netlist
parser = SpiceParser(path=str("input.cir"))
circuit = parser.build_circuit()
# Models
circuit.include("AD712.mod")
# Contains AD633 Multiplier
circuit.include("analog.lib")
circuit.include("ad633.cir")
# Subcircuits
circuit.include("DelayLine.cir")
#circuit.include("JFETNL.cir")
circuit.include("PabloNL.cir")
circuit.include("InputAmp.cir")
circuit.include("Integrator.cir")

circuit.V('input', 'input', circuit.gnd, 'dc 0 external')

amplitude = 10@u_V
frequency = 50@u_Hz
ngspice_shared = MyNgSpiceShared(amplitude=amplitude, frequency=frequency, send_data=False)

simulator = circuit.simulator(temperature=25, nominal_temperature=25, simulator='ngspice-shared', ngspice_shared=ngspice_shared)
period = float(frequency.period)
analysis = simulator.transient(step_time=period/200, end_time=period*2)

with open('data.csv', 'w', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(['Time', 'Voltage'])  # Write the header row
    for t, v in zip(analysis.time, analysis.DLOut):
        writer.writerow([t, v])
figure1, ax = plt.subplots(figsize=(20, 10))

ax.set_title('Voltage Divider')
ax.set_xlabel('Time [s]')
ax.set_ylabel('Voltage [V]')
ax.grid()
ax.plot(analysis.input)
ax.legend(('input', 'output'), loc=(.05,.1))
ax.set_ylim(float(-amplitude*1.1), float(amplitude*1.1))

plt.tight_layout()
plt.show()