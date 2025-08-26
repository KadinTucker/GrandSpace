# Demand

Demand is a property of a [colony](colony.md) determining the [price](money.md) of [minerals](mineral.md) sold to that colony.

Demand has two components: colour, and degree.

Each colony demands at most one colour of minerals at a time. Selling minerals of the demanded colour yields more money than selling other colours of minerals to that colony. 

The degree of demand determines how much higher the price for the demanded colour is compared to the base price of 50. 

Degree ranges from 1 to 9, and each degree increases the price by 50. If the player has researched [Economics](../technology/economics.md), this amount increases by 5 per tier, up to a maximum of 75.

Demand changes every 30 seconds, and either increases in degree, decreases in degree, or resets entirely. 
If the degree of the demand is increased above 9 or decreased below 1, the demand will reset.

When demand is reset, no mineral colour is demanded. When the demand changes again, it will choose a new colour to demand, with a starting degree of 1.

The chances of demand increasing, decreasing, and resetting depends on the number of cities the colony has. 
In general, with more *cities*, the chance of demand increasing is higher, and the chances of demand decreasing or resetting are lower.

The odds of each possible change are summarised below:

| Number of Cities | Increase Chance | Decrease Chance | Reset Chance |
|------------------|-----------------|-----------------|--------------|
| 1                | 50%             | 40%             | 10%          |
| 2                | 67%             | 26%             | 7%           |
| 3                | 75%             | 20%             | 5%           |
| 7**              | 87%             | 11%             | 2%           |

** The demand values for 4-6 cities are not shown due to these numbers of cities occurring very rarely in the game. The formula for the chances is, for N cities:
  * Increase: (5 * N + 5) / (5 * N + 10);
  * Decrease: 4 / (5 * N + 10)
  * Reset: 1 / (5 * N + 10)

In general, colonies with higher numbers of cities have more stable demand that is more likely to higher and more likely to keep the same colour.
Colonies with fewer cities are likely to have low degree demands and change colour often.
