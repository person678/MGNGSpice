# MGNGSpice
This library is a wrapper around NGSpice for running batches of simulations for a Mackey-Glass reservoir.

#Features
Can sweep any component's value. 
Can set component to specific value before sweeping others.
Can graph two parameter sweeps MC scores on a heatmap. 
Can graph three parameter sweeps MC scores by outputting multiple heatmaps.
Can graph single parameter sweep,
Can specify PWL file for a voltage input, not normally supported by NGSpice. 

## Automated Range Scaling
Automated range scaling maths is applied to ensure the voltage levels of the circuit are operating in the correct range. 
This is all located in the "NGSpice Direct Full" file, in the Simulation class. 

# How to use
Specify simulation settings in sim.config. This is used for specifying: 
	sim type (transient, dc sweep, etc)
	nodes to measure
	what delay line stage output to tap (not fully implmented - will change, but some scripts as such as graphing need manual tweaks to support)
	Path to PWL File
	Can also specify a, d, and b as components. These refer to resistor ratios. See files in "Misc" for details on what these are. 

See comments in sim.config for examples on syntax. 

## entry point
run "NGSpice Direct Full" (full means full circuit). Ensure config is configured correctly. 
Must specify experimentName here. 
## Output
Output results will be saved to the folder Output/"ExperimentName"
A copy of the modified netlist will be exported there. There will be data from the DC sweep used for range scaling, the output file, and a file called run_config.csv.

 run_config.csv contains information on the parameters applied to a paticular run, and the file id of that run. This is parsed for many of the graphing classes. Currently this is overwritten if another run is ran with the same experiment name - make sure to save it if needed, or use a new experiment folder, or have it append a number to run_config. 
 
 More detailed information on the setup for a given run is contained in the netlist file. Looking at this is very useful for debugging and ensuring changes were properly applied. 
 
## Batching Sims
Using the python pool library to run multiple sims. Set the value of the "processes" argument in NGSpiceDirect Full to be equal to the number of sims you want to run. Probably don't want to run more than the number of physical cores in your system. 
# Support scripts
Support scripts include:
## NetlistParser
Includes methods for modifying the netlist and parsing the config file. 
## RunMCSweepTwoParams/ThreeParams/OneParam
These scripts can be ran (specify the experiment folder) to graph memory capacity benchmark scores. 
Make sure that the theta of the circuit is set correctly in "prepare_output.py"
Supports scores between 0 to 15. 
Sensible scores I've had range from around 5-11. If you beat 11.3, well done, you've exceeded me. 
	
## Graph NL Voltage Spread
Takes readings from the input to the NL circuit and graphs them against the DC sweep of the NL, so you can see what range it's operating in. I was planning to extend this to seperate out the contribution of the input / feedback at some point. Useful for seeing the effects of range scaling tweaks, or just to ensure the circuit is operating in a vaguely sensible range. 

To use, take a transient simulation measuring IAOut, the input node to the NL circuit. Seems to work well with a fraction of the data needed for a MC run - I generally did a tenth of the MC run (0.4s for my setup). 

# Help
This is some of the first serious python coding I've done - it's held together with spit and hope and just about works. If you are having trouble getting it setup, please feel free to open an issue or email me at paulpickering678@gmail.com. I do not promise to respond, but will try to if time allows.

# Misc Advice
The system currently works by editing the netlist directly before running. In hindsight, making use of the NGSpice control language might have been better. Might be worth investigating if you want to extend this. 
 


	
