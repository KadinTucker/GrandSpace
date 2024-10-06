# Warfare

Warfare consists of players taking hostile actions against each other. 

[Hostile actions](../rulebook/glossary/hostile_action.md) are actions against another player that reduce [leverage](../rulebook/glossary/leverage.md) over that player, and that also require that __other__ player to have below a certain threshold.

For example, If Player A has 10 leverage over Player B while Player B has -15 leverage over Player A, then Player A has the right to take certain hostile actions. 

The following hostile actions are possible, with their thresholds in parentheses, below which the other player's leverage needs to be:
 - (0) [Attack](../rulebook/actions/battle.md) a rival ship in one of [your systems](../rulebook/glossary/rule.md)
 - (-10) Raid systems, stealing [minerals](../rulebook/glossary/mineral.md) or [biomass](../rulebook/glossary/biomass.md)
 - (-15) [Attack](../rulebook/actions/battle.md) a rival ship in a third-party system
 - (-30) [Attack](../rulebook/actions/battle.md) a rival ship in one of their systems
 - (-40) [Besiege](../rulebook/actions/siege.md) cities, either conquering them or looting them

The effective logic of the warfare system is the logic of "they started it". As soon as another player does something to drop their leverage, you can then take hostile actions against them. If you do, you will lose leverage over them, until they get the right to take similarly hostile actions against you.

## Mechanics of Combat

When a ship and an enemy ship that is a valid target (as in the above list of hostile actions) are in the same system, the ship may [attack](../rulebook/actions/battle.md) the other ship. The ship will attack the other so long as it is not preoccupied with another task. 

When a ship attacks, it deals 1 damage. Without any technological advances, ships have a maximum of 5 health, and fire 1 shot every three seconds. 

When a ship runs out of health points, it loses all cargo and reappears at its owner's homeworld with 1 health point. Ships that are [idle](../rulebook/actions/idle.md) on planets ruled by their owner slowly recover their missing health points.

Destroying an enemy ship yields 100 [money](../rulebook/glossary/money.md) as a reward. 

Ships raiding a planet and stealing minerals take the minerals at a fairly slow rate of 1 mineral per 5 seconds. Ships that steal biomass take it at the same rate as they would harvest it otherwise. 

To besiege a planet, click on one of the [shield](../rulebook/glossary/shield.md) icons of the planet wished to be besieged. The ship will attack the shield until it is conquered. A shield has 15 health points. When a shield is conquered, the colony loses one development (to a minimum of 0) as collateral damage. When all shields are conquered, the planet as a whole is conquered. 

When all shields in a star system are conquered, the whole system is conquered. All colonies in the system transfer to the conquering player.

Additionally, you may destroy conquered cities as a ship task. If you besiege an already conquered city, it will, in short time, be looted, yielding 500 money. 

Shields slowly regenerate health over time. Shields become unconquered only when they reach their hit point maximum. Shields do not regenerate as long as any enemy ships with the ability to besiege are located in their system. Friendly ships can also actively repair shields to speed up the process. 

## [Milestones](../rulebook/glossary/milestone.md)

Stealing minerals or biomass grants +1 Warfare milestone progress per mineral and sample stolen.

Destroying an enemy ship grants +25 Warfare milestone progress. Having one of your own ships destroyed in combat grants +50 Warfare milestone progress.

Conquering a *shield* grants +25 Warfare milestone progress. Having a shield conquered grants +50 Warfare milestone progress.
