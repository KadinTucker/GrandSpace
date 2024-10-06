# Ecology

Ecology is the path dealing with the [lifeforms](../rulebook/glossary/lifeform.md) encountered in the galaxy. Ecology is nearly necessary for developing
[mineral](../rulebook/glossary/mineral.md) production, and useful for producing [science](../rulebook/glossary/science.md) points. 

The galaxy is populated by lifeforms of a number of types based on the number of players in the game. These lifeforms
can be collected by ships in the form of [biomass](../rulebook/glossary/biomass.md). 

When a planet has biomass available to collect, it will show a green bar with a light-coloured halo around it. A ship
can then collect biomass, which takes some time. When done, the ship gets one "sample" of each lifeform on the planet 
in its [cargo](../rulebook/glossary/cargo.md). The samples that the ship has are collectively referred to as its biomass. Once biomass has been 
collected, the planet is exhausted and needs to wait until biomass can be collected there again.

A ship's biomass has a value based on the total number of samples, and the diversity of lifeforms among the samples.
The value of a biomass equals the sum of values of each group of X unique lifeforms represented in the samples, where
the value of a group of X unique lifeforms is:
 - 1, if X = 1;
 - 3, if X = 2;
 - 6, if X = 3;

and so on. For a more detailed description of how these values are obtained, see [here](../rulebook/glossary/biomass.md), or see "triangle numbers" via 
a web search or similar.

Biomass has two uses: [terraforming](../rulebook/glossary/terraforming.md), and [conversion into science points](../rulebook/actions/biology.md).

Terraforming a planet places a lifeform on that planet, according to the following rules:
 - The same lifeform cannot be placed on a planet more than once;
 - No more than three lifeforms can be present on a planet.

The cost to terraform is 1500 money, one sample of the lifeform being placed, and an amount of biomass of value varying 
with the number of existing lifeforms:
 - 10, if the planet has no lifeforms;
 - 30, if the planet already has one lifeform;
 - 60; if the planet already has two lifeforms. 

The ship will then take time to terraform the planet. Once done, the lifeform will be present on the planet. The planet 
will also need time to regenerate before biomass can be collected there.

The total number of lifeforms on a planet is called its [habitability](../rulebook/glossary/habitability.md), and determines the degree to which colonies on 
the planet can be developed:
 - The maximum number of cities on a planet equals its habitability (minimum of 1)
 - The maximum development score __per city__ equals the planet's habitability. For example, a planet with a habitability of 3 and 2 cities has a maximum of 6 development. A planet with a habitability of 2 and 2 cities has a maximum of 4 development.

Biomass can also be consumed to make Harmony science points, at a rate of 1 Harmony science point per 5 biomass value.

## [Milestones](../rulebook/glossary/milestone.md)

Collecting biomass grants 2 milestone progress per sample collected. Terraforming a planet grants 25 milestone progress. 
Consuming biomass grants milestone points equal to the biomass value consumed.
