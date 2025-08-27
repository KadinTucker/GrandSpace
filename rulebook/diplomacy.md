# Diplomacy

Unlike the previous four paths covered, the final two are exclusive to player on player interactions. 

Diplomacy works through a system of [leverages](../rulebook/glossary/leverage.md). Each player has a leverage value over each other player. 

Leverage is asymmetrical. For example, Player A can have 15 leverage over Player B, and Player B can have 25 leverage
over Player A. 

Leverage can be positive or negative. For example, Player A can have -10 leverage over Player B, and Player B can have 
5 leverage over Player A.

Leverage has a maximum value of 100 and a minimum value of -100.

Players can gain leverage over other players in the following ways:
 - Giving a gift of [money](../rulebook/glossary/money.md). 50 money buys 1 leverage point. Notably, gifts cannot be refused.
 - Granting [access](../rulebook/glossary/access.md) to a player, if accepted, grants leverage equal to the leverage value of the access granted. Access will be covered later in this section.
 - Cooperative research, which works similarly to the normal [research](../rulebook/actions/research.md) action of a ship, but grants [science](../rulebook/glossary/science.md) to both players and grants the researching player 5 leverage over the other per minute.
 - "[Schmoozing](../rulebook/actions/schmooze.md)", which is a ship's task, is unlocked with [technology](../rulebook/glossary/technology.md), and grants between 10 and 60 leverage per minute over another player, if they allow such access.
 - [Terraforming](../rulebook/glossary/terraforming.md) another player's planet grants 50 leverage.

Leverage is used for asking favours of other players, which can include:
 - Money, at a cost of 1 leverage per 50 money.
 - Access, at cost of the value of that access.
 - Military aid, in the form of one of the other player's ships spending 1 minute per 25 leverage at a chosen planet and participating in any [battles](../rulebook/glossary/combat.md) there.

When leverage is used to ask for a favour, it is lost. The player of whom the favour is asked may refused the favour. However, doing so
causes them to lose double the amount of leverage spent to ask for a favour. 

A favour cannot be asked if the player's leverage is lower than the cost. In other words, you cannot ask a favour from a player over whom you have negative leverage.

Several actions also cause leverage to be reduced:
- Revoking access causes you to lose leverage equal to the access value
- Entering a player's system or planet when passage (access) is not allowed causes you to lose 1 leverage over them
- Refusing a favour loses leverage as described previously
- Taking [hostile actions](../rulebook/glossary/hostile_action.md), which are covered in detail in [Warfare](../rulebook/warfare.md), against a player:
  - Stealing minerals: lose 2 leverage per mineral taken
  - Stealing biomass: lose 5 leverage (no matter how many samples)
  - Damaging ships: lose 10 leverage per damage dealt as a fraction of the ship's max health
  - Conquering a city: lose 15 leverage
  - Destroying a city (in addition to having conquered it): lose 10 leverage

In general, hostile actions can only be taken against a player with negative leverage. 

Lastly, two players can agree to "reset relations", by adding or subtracting a fixed amount from both of their leverages against each other. Note that this can effectively be replicated by repeatedly exchanging gifts. 

## Access

*Access* refers to what a player allows other players to do in their systems. There are four access types, with their 
values in parentheses:
 - Ecological operations (25): can [collect biomass](../rulebook/actions/collect_biomass.md) and [terraform](../rulebook/actions/terraform.md) in your systems
 - Diplomatic operations (20): can do [research](../rulebook/actions/research.md) and [schmooze](../rulebook/actions/schmooze.md) in your systems
 - Trade (15): can [sell minerals](../rulebook/actions/sell_minerals.md) in your systems
 - Passage (15): can freely move through your systems without incurring a penalty

Access is absolute: if a player does not have access to take an action in another's systems, they __cannot__ take those actions. Note that this is literal: not allowing the right of passage means players can still enter your systems, but incur a leverage penalty by doing so. Additionally, while one cannot collect biomass without permission, one can steal the biomass with a [raid](../rulebook/actions/raid.md) action.

Access can be offered to a player, if not already granted. If accepted, you gain leverage over them equal to the leverage value of the access. 

Access can be revoked at any time, but doing so causes you to lose leverage equal to the value of the access revoked.

Access can be requested as a favour, at the cost of its value, but, as with all favours, it need not be granted.

## [Milestones](../rulebook/glossary/milestone.md)

Gain +1 diplomacy milestone point per 5 leverage earned from research with other players and schmoozing.

Diplomacy milestones work a little bit differently from all other paths. Due to the potential to exploit a milestone that would grant points for earning leverage, a player's Diplomatic milestone progress is a measure of how much more leverage a player has earned over their rivals than their rivals have earned over them.

See a more detailed description of how this is calculated [here](../rulebook/reference/diplomacy_milestones.md).
