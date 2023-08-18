
import random

from NgSpiceDirect import *
#circuit = SpiceParser("Subcircuits/PabloNL.cir").build_circuit()
#print(circuit)
#circuit
#circuit.R3.resistance = 10000

nodes, command, params = parse_config("sim.config")
result = generate_parameters(nodes, command, params)
print(result)