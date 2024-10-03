# Shields

Shields are units of defence on *colonies*. A colony typically has a number of shields equal to its number of *cities*.

When a ship besieges a city, it "places" itself on a shield and gradually damages the shield. Each shield has 15 health points, which does __not__ change with technology. When a shield is brought down to 0 health points, it is said to be conquered. When a shield is conquered, the colony suffers collateral damage in the form of losing 1 *development* score.

After a shield has been conquered, it slowly regenerates health, at a rate of 3 per minute. If the shield reaches 15 health again, it is unconquered. Friendly ships can work to speed up this rate to 10 per minute.

After conquering a shield, a ship may choose to "loot" a city. If they choose to do so, after 5 seconds, the city is destroyed and the conquering player earns 500 money. If the last city in a colony is looted, the colony is destroyed.

If all shields in a system are conquered, then the conquering player takes control of the system and all of its colonies. 

### Orbital Defences

One of the Imperial Bonus technologies is called Orbital Defences, and purportedly adds one shield to each colony. 
However, how does this actually work in practice, given that shields seem to correspond to cities?

In effect, the bonus shield is a "dummy" shield that needs to be conquered before any cities can be reached. The concrete effects of this are:

- No collateral damage takes place unless the number of unconquered shields is less than, or equal to, the number of cities. In particular, the first shield conquered does no cause collateral damage on a planet with Orbital Defences
- Similarly, cities cannot be looted until the number of unconquered shields is less than the number of cities. In particular, at least two shields need to be conquered to loot a city. 
