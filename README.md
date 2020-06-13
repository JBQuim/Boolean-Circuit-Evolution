# Spontaneous evolution of modularity in logic gate networks

Some of the findings outlined in [this](https://doi.org/10.1073/pnas.0503610102) paper by Nadav Kashtan and Uri Alon are replicated. See the paper for more detailed exploration of the results in more scenarios. This is intended only as a learning exercise inspired by [this](https://youtu.be/cdaynA0PyPU) lecture by Uri Alon.

## Goals

Evolution in nature has produced no shortage in diversity of the design of biological systems. A common feature of most of these systems is that they are *modular*. Modular meaning they can be decomposed into self-contained parts that interact with each other. Signalling networks, for example, are made up of modules that can be changed or rewired by the synthetic biologist to alter the response to some stimuli. Intriguingly, when evolution is simulated it tends not to produce such modular systems. Here, evolutionary algorithms are applied to networks of logic gates to explore the modularity of solutions under different selection pressures.

## Methods

### Networks of logic gates

Networks of logic gates are used as a model problem. Networks of NAND gates can encode any boolean function of various inputs. The problem statement is therefore to find the smallest such network that implements a given boolean function. Each potential solution is encoded by a genome. Here, the genome represents a network of up to 13 NAND gates. Every two numbers in the genome represent the inputs of a gate (see Fig. 1). Negative numbers represent the inputs of the network and the output of the network is given by the output of gate 0.

<p align="center">
  <img width="460"src="https://user-images.githubusercontent.com/63521540/84573077-adc49100-ad9e-11ea-8d3a-7ab29387021e.png">
</p>

<p align="center">
  Fig. 1 - Example of a genome and the network it represents
</p>



The quality of a solution is judged by the similarity of the network's output to the desired output, for every combination of inputs (see Table 1).

<p align="center">
  <img width="460 src="https://user-images.githubusercontent.com/63521540/84573608-e6199e80-ada1-11ea-8b7e-e7f8d5768a9d.JPG">
</p>

<p align="center">
  Table 1 - Evaluating the network in Fig. 1 to obtain a value of 0.25 for its accuracy.
</p>


