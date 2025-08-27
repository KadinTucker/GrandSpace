# Combat

Combat refers to ships fighting each other.

During combat, each ship not performing another action with at least one [valid target](hostile_action.md) in its star system will fire upon a valid target, dealing 1 damage periodically.

The rate at which a ship fires increases with the [Weapons](../technology/weapons.md) technology:


| Technology  | Ship Fire Rate per Minute | 
|-------------|---------------------------|
| None        | 20                        |
| Weapons I   | 30                        |
| Weapons II  | 40                        |
| Weapons III | 50                        |
| Weapons IV  | 60                        |
| Weapons V   | 70                        |

A ship's valid targets depends on the [leverage](leverage.md) relationship between players. See also [hostile actions](hostile_action.md). 

| Situation                            | Opponent Leverage at Most | 
|--------------------------------------|---------------------------|
| System you [rule](rule.md)           | 0                         |
| System neither you nor opponent rule | -15                       |
| System opponent rules                | -30                       |

A ship is destroyed if its health reaches 0. When a ship is destroyed, it loses all of its [cargo](cargo.md) and reappears at its owner's [homeworld](homeworld_colony.md) with 1 health. If the ship is already located at the homeworld, it cannot be destroyed and instead returns to 1 health automatically.

When you destroy an enemy ship, you earn 100 [money](money.md), 5 Power [science](science.md), and 25 Warfare [milestone](milestone.md) progress. When one of your ships is destroyed in combat, you earn 10 Power science and 50 Warfare milestone progress.

Ship health and healing rate also improves with the [Shipbuilding](../technology/shipbuilding.md) technology:

| Technology       | Maximum Health | Idle Heal Rate         |
|------------------|----------------|------------------------|
| None             | 10             | 1 per 3 seconds        |
| Shipbuilding I   | 15             | 1 per 2 seconds        |
| Shipbuilding II  | 20             | 2 per 3 seconds        |
| Shipbuilding III | 25             | 5 per 6 seconds        |
| Shipbuilding IV  | 30             | 1 per second           |
| Shipbuilding V   | 35             | more than 1 per second |
