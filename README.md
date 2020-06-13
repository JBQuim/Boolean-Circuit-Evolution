# Spontaneous evolution of modularity in logic gate networks

Some of the findings outlined in [this](https://doi.org/10.1073/pnas.0503610102) paper by Nadav Kashtan and Uri Alon are replicated. See the paper for more detailed exploration of the results in more scenarios. This was intended only as a learning exercise inspired by [this](https://youtu.be/cdaynA0PyPU) lecture by Uri Alon.

## Goals

Evolution in nature has produced no shortage in diversity of the design of biological systems. A common feature of most of these systems is that they are *modular*. Modular meaning they can be decomposed into self-contained parts that interact with each other. Signalling networks, for example, are made up of modules that can be changed or rewired by the synthetic biologist to alter the response to some stimuli. Intriguingly, when evolution is simulated it tends not to produce such modular systems. Here, evolutionary algorithms are applied to networks of logic gates to explore the modularity of solutions under different selection pressures.

## Components

### Networks of logic gates

Networks of logic gates are used as a model problem. Networks of NAND gates can encode any boolean function of various inputs. These gates take in two inputs and output `True` if either of them is `False`. The problem statement is therefore to find the smallest such network that implements a given boolean function. Each potential solution is encoded by a genome. Every two numbers in the genome represent the inputs of a gate (see Fig. 1). Negative numbers represent the inputs of the network and the output of the network is given by the output of gate 0.

<p align="center">
  <img width="460"src="https://user-images.githubusercontent.com/63521540/84573077-adc49100-ad9e-11ea-8d3a-7ab29387021e.png">
</p>

<p align="center">
  Fig. 1 - Example of a genome and the network it represents
</p>



The quality of a solution is judged by the similarity of the network's output to the desired output, for every combination of inputs (see Table 1).

<p align="center">
  <img width="460" src="https://user-images.githubusercontent.com/63521540/84573608-e6199e80-ada1-11ea-8b7e-e7f8d5768a9d.JPG">
</p>

<p align="center">
  Table 1 - Evaluating the network in Fig. 1 to obtain a value of 0.25 for its accuracy.
</p>

### Evolutionary algorithm 

To reach a solution, the evolutionary algorithm works as follows. At the beginning of the simulation, a population of random networks is produced. This is the first generation. To produce the next generation, the fitness of every individual is evaluated and an elite fraction selected from the most fit individuals. The individuals in the elite fraction pass to the next generation unmutated. The elite fraction is also mutated slightly to form new individuals, which then pass to the new generation. By repeating this process iteratively, the fitness of the population slowly increases, representing better and better solutions.

Mutations can be point mutations, which switch the input of a single gate for another input; deletions, which delete a gate and rewire everything that was connected to it; additions, which produce a new randomly wired gate; and crossovers, which swap parts of two genomes to produce two new genomes.

### Modularity measure

Modularity is a property of a partition of a network into modules. The modularity of a partition is the fraction of the edges that lie within a module minus the expected number for this quantity, summed over all modules. For information on how to find the partition and then calculate its modularity refer to [this](https://doi.org/10.1103/PhysRevE.69.066133) paper. Here, the algorithm is implemented by the python library `networkx`.

The modularity thus obtained, `Qreal`, can be normalized with respect to randomly generated networks to obtain `Qm`. This measure can be found from the expression:

`Qm = (Qreal-Qrand)/(Qmax-Qreal)`

Where `Qrand` is the modularity of a randomly generated network and `Qmax` the maximum modularity of a network. Both measures refer to networks with connectivity matching that of the possible solutions, i.e. with at least 10 gates connected to gate 0. `Qrand` was found by generating many random networks, finding their modularity and taking the average. `Qmax` was found by applying the evolutionary algorithm with the fitness of a genome being its modularity. In this scheme, a network with `Qm` of 1 has the maximum possible modularity and `Qm` of 0 has the modularity of a randomly generated network. Networks with negative `Qm` are nonetheless possible.

## Results

The evolutionary algorithm was challenged with creating a network of NAND gates that would take four boolean inputs and output the same value as some function `G`. The fitness function was the fraction of all inputs that produced the correct output, with a small penalty for size being over a certain cutoff. This ensured that networks would remain small. 

The first boolean functions attempted were `G1 = I₁ XOR I₂ AND I₃ XOR I₄` and `G2 = I₁ XOR I₂ OR I₃ XOR I₄`. Over the 50 runs, 35 and 38 reached solutions for the target function within 10⁵ generations. Over the runs that did reach a solution, the number of generations taken to reach a solution was 1620 (-884, 2768) and 12773 (-7016, 26286) for G1 and G2, respectively. It is interesting that despite G2 seemingly being of the same complexity it took about eight times as many generations to reach. The fitness of the most fit individual over time in a typical run is shown in Fig. 2.

<p align="center">
  <img width="460" src="Figures/TypicalG1Run.png">
</p>

<p align="center">
  Fig. 2 - the increase in fitness shows logarithmic slowdown, a common feature of evolutionary algorithms
</p>

Despite both goals being strictly modular, being made out of two XOR modules and an AND/OR module, the solutions that were found had very low modularity. They had values of Qm of -0.06 ± 0.21 and 0.12 ± 0.19 for G1 and G2, respectively.

The paper suggests, and confirms, that evolving networks under "modularly varying goals" would produce modular solutions. The key insight is that if the goal is varied every few generations, *but the goals have shared subgoals*, those individuals that had evolved modules dedicated to solving one of the subproblems would find it easier to adapt to the new goal.

Here the goal is switched every 20 generations between G1 and G2. All 100 runs terminated within 10⁵ generations and took 1870 (-1010, 1355) generations. A typical run can be seen in Fig. 3. As expected, the modularity of solutions under time-varying modular goals was much higher than that evolved under fixed goals, with Qm = 0.42 ± 0.08 (see Fig. 4).
