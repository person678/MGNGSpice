from PySpice.Spice.Netlist import Circuit
from PySpice.Spice.Parser import SpiceParser
import random
circuit = SpiceParser("Subcircuits/PabloNL.cir").build_circuit()
print(circuit)
circuit
circuit.R3.resistance = 10000
print(circuit)
filename = "Subcircuits/temp/PabloNL" + str(random.randint(1, 1000000)) + ".cir"
with open(filename, "w") as file: 
    file.write(str(circuit))
