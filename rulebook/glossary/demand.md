# Demand

Demand is a property of a [colony](colony.md) determining the [price](money.md) of [minerals](mineral.md) sold to that colony.

Demand has two components: colour, and degree.

Each colony demands at most one colour of minerals at a time. Selling minerals of the demanded colour yields more money than selling other colours of minerals to that colony. 

The degree of demand determines how much higher the price for the demanded colour is compared to the base price of 50. 

Degree ranges from 1 to 9, and each degree increases the price by 50. If the player has researched [Economics](../technology/economics.md), this amount increases by 5 per tier, up to a maximum of 75.

The demand of a colony changes every minute. When the demand changes, a mineral colour is randomly chosen, excepting the colour of the colony's planet. 
The degree of demand is also randomly chosen, with a tendency to larger values the more cities a colony has. 

The degree of demand is chosen according to a binomial distribution. 8 trials are simulated, and the degree of demand equals 1 plus the number of successful trials. 
The probability of success changes with the number of cities; exceeding 4 cities does not further increase the probability of success. 

The likelihood of each demand degree outcome is summarised in the following table:

| Number of Cities | Probability of Trial Success | Expected Demand | Demand 1 | Demand 2 | Demand 3 | Demand 4 | Demand 5 | Demand 6 | Demand 7 | Demand 8 | Demand 9 | 
|------------------|------------------------------|-----------------|----------|----------|----------|----------|----------|----------|----------|----------|----------|
| 1                | 35%                          | 3.8             | 3%       | 14%      | 26%      | 28%      | 19%      | 8%       | 2%       | 0%       | 0%       |
| 2                | 45%                          | 4.6             | 1%       | 5%       | 16%      | 26%      | 26%      | 17%      | 7%       | 2%       | 0%       |
| 3                | 55%                          | 5.4             | 0%       | 2%       | 7%       | 17%      | 26%      | 26%      | 16%      | 5%       | 1%       |
| ≥4               | 65%                          | 6.2             | 0%       | 0%       | 2%       | 8%       | 19%      | 28%      | 26%      | 14%      | 3%       |
