# Spontaneous evolution of modularity in logic gate networks

Some of the findings outlined in [this](https://doi.org/10.1073/pnas.0503610102) paper by Nadav Kashtan and Uri Alon are replicated. See the paper for more detailed exploration of the results in more scenarios. This is intended only as a learning exercise inspired by [this](https://youtu.be/cdaynA0PyPU) lecture by Uri Alon.

## Goals

Evolution in nature has produced no shortage in diversity of the design of biological systems. A common feature of most of these systems is that they are *modular*. Modular meaning they can be decomposed into self-contained parts that interact with each other. Signalling networks, for example, are made up of modules that can be changed or rewired by the synthetic biologist to alter the response to some stimuli. Intriguingly, when evolution is simulated it tends not to produce such modular systems. Here, evolutionary algorithms are applied to networks of logic gates to explore the modularity of solutions under different selection pressures.

## Methods

### Networks of logic gates

Networks of logic gates are used as a model problem. Networks of NAND gates can encode any boolean function of various inputs. Each individual's genome represents a network of up to 13 NAND gates. Every two numbers in the genome represent a new gate, with each number representing the inputs of the gate. Negative numbers represent the inputs of the network and the output is represented by the output of gate 0.

