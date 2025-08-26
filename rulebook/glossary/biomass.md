# Biomass

Biomass refers to a ship's collection of samples of [lifeforms](lifeform.md). 

Biomass consists of a collection of samples, and a value, based on the number and diversity of its samples. 

The value of a set of biomass is given by the sum of biomass values of groups of samples all with distinct lifeforms. 
For example, if there are two samples of A, two samples of B, and one sample of C, then there are two groups: A, B, C, and A, B. 

Each group then has a value determined in the following way:
- A group with just 1 sample has a value of 1
- A group with 2 samples has the value of a group of 1 sample, plus the number of samples, 2, for a total of 3.
- A group with 3 samples has the value of a group of 2 samples, plus the number of samples, for a total of 6.
- A group with X samples has the value of a group of X - 1 samples, plus the number of samples. The value of a group of X samples equals N * (N + 1) / 2.

The biomass value of the above example, with one group of 3 and one group of 2, is 9.

One needs not now exactly how to determine the biomass value of one's cargo, but it is instructive to know that diversity of samples yields more value per sample than quantity of samples.

Biomass has two main uses:
 - [Terraforming](terraforming.md) requires 10-60 biomass value, depending on the level to be terraformed to.
 - Biomass value can be converted into Harmony [science](science.md) at a rate of 5 to 1. 

There are two additional uses of biomass, both of which are unlocked by the Ecology bonus [technologies](technology.md).
 - [Genetic Programming](../technology/genetic_programming.md) allows one to spend 30 biomass to produce a single sample of any one lifeform (including lifeforms that do not exist in the galaxy)
 - [Mass Cloning](../technology/genetic_programming.md) allows one to convert 30 biomass into one [building](building.md).

There are two ways biomass can be consumed:
 - Sample-efficient: this is the default way biomass is consumed. The largest groups are consumed first, then the next largest groups, and so on. If a smaller group would produce enough biomass to fulfil the task, then only that smaller group is consumed.
 - Rare-efficient: The most common lifeforms represented in samples are consumed first. This method consumes more samples overall, but preserves rarer samples in the cargo.

Consuming biomass value earns that many Ecology [milestone](milestone.md) points. 
