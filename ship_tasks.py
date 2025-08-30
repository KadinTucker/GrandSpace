import math

import colony
import ecology

FULL_HEAL_RATE = 2.0
COLONY_PLACEMENT_RATE = 15.0
CITY_PLACEMENT_RATE = 30.0
DEVELOPMENT_PLACEMENT_RATE = 30.0
CARGO_TRANSFER_RATE = 180.0
RESEARCH_RATE = 1.0
MINERAL_RAID_RATE = 20.0
RESEARCH_MONEY = 100

SCIENCE_PER_BIOLOGY = 1
MONEY_MILESTONE_VALUE = 500
MINERAL_SALE_MILESTONE_MODIFIER = 5

def find_nearest_star(position, galaxy, blacklist=()):
    """
    Finds the nearest star to the ship, except for a possible blacklist
    To be used only when the ship is not currently located at a star
    """
    nearest = None
    min_distance = -1
    for s in galaxy.stars:
        if s in blacklist:
            continue
        distance = math.hypot(s.location[0] - position[0], s.location[1] - position[1])
        if min_distance < 0 or distance < min_distance:
            nearest = s
            min_distance = distance
    return nearest

def find_stars_in_range(star, travel_range, galaxy):
    """
    Finds all the stars in travel range of the current star at which a ship might be found
    Can also be used to find which stars are visible
    Returns a list of star ids that are in range
    """
    search_index = 0
    while galaxy.star_distance_matrix[star.id][galaxy.star_distance_hierarchy[star.id][search_index]] < travel_range:
        search_index += 1
    return galaxy.star_distance_hierarchy[star.id][0:search_index]

def get_explored_stars(player, galaxy):
    explored = []
    for e in range(len(player.explored_stars)):
        if player.explored_stars[e]:
            explored.append(galaxy.stars[e])
    return explored

def has_enough_money(ship, requirement):
    return ship.ruler.money >= requirement

def has_buildings(ship, requirement):
    return ship.cargo.buildings >= requirement

def has_enough_biomass(ship, requirement):
    return ship.cargo.biomass.value >= requirement

def has_enough_biomass_to_terraform(ship):
    return ship.planet is not None and has_enough_biomass(ship, ship.planet.ecology.get_terraform_cost())

def has_active_access(ship, access_index):
    return (ship.star is not None and (ship.star.ruler is None
            or ship.ruler.game.diplomacy.get_active_access(ship.star.ruler.id, ship.ruler.id, access_index)))

def has_hostile_access_versus(ship, other_player, access_index):
    return ship.ruler.game.diplomacy.get_hostile_access(other_player.id, ship.ruler.id, access_index)

def is_system_neutral(ship):
    return ship.star is not None and ship.star.ruler is None

def is_at_colony(ship):
    return ship.planet is not None and ship.planet.colony is not None

def rules_system(ship):
    return ship.star is not None and ship.ruler is ship.star.ruler

def rules_planet(ship):
    return ship.planet is not None and ship.planet.colony is not None and ship.planet.colony.ruler is ship.ruler

def planet_has_species(ship, species_index):
    return ship.planet.ecology.species[species_index] > 0

def can_be_terraformed(ship):
    return ship.planet is not None and ship.planet.ecology.habitability < ecology.MAX_HABITABILITY

def can_terraform(ship):
    return (can_be_terraformed(ship) and has_enough_biomass_to_terraform(ship)
            and not planet_has_species(ship, ship.cargo.biomass.selected)
            and ship.cargo.biomass.selected != -1)

def has_colony(ship):
    return ship.planet is not None and ship.planet.colony is not None

def has_space_for_city(ship):
    return (has_colony(ship) and rules_system(ship)
            and ship.planet.colony.cities < ship.planet.colony.get_maximum_cities())

def has_space_for_development(ship):
    return (has_colony(ship) and rules_system(ship)
            and ship.planet.colony.development < ship.planet.colony.get_maximum_development())

def is_enemy_ship(ship, other):
    # Both ships have to be in the same star
    # Either: this ship has access to battle the other everywhere, or this ship is at a home system
    # and the ship's ruler has right to trespass (other's access is "blocked")
    return ship.star is other.star and (has_hostile_access_versus(ship, other.ruler, 2)
                                        or (rules_system(ship) and has_hostile_access_versus(ship, other.ruler, 0)))

def exists_enemy_ship(ship, star):
    for s in star.ships:
        if is_enemy_ship(ship, s):
            return True
    return False

def cond_collect_minerals(ship):
    if rules_planet(ship):
        if ship.planet.colony.minerals >= 1:
            return True
        else:
            ship.ruler.log_message("Cannot collect minerals: no minerals to collect")
    else:
        ship.ruler.log_message("Cannot collect minerals: not at planet/planet not ruled by player")
    return False

def cond_sell_minerals(ship, mineral_index):
    if is_at_colony(ship):
        if has_active_access(ship, 2):
            if ship.cargo.minerals[mineral_index] > 0:
                return True
            else:
                ship.ruler.log_message("Cannot sell minerals: no such minerals in cargo")
        else:
            ship.ruler.log_message("Cannot sell minerals: no trade access in this system")
    else:
        ship.ruler.log_message("Cannot sell minerals: not at colony")
    return False

def cond_sell_artifact(ship):
    if rules_planet(ship):
        if ship.cargo.artifacts > 0:
            return True
        else:
            ship.ruler.log_message("Cannot sell artifacts: no artifacts to sell")
    else:
        ship.ruler.log_message("Cannot sell artifacts: not at own colony")
    return False

def cond_buy_building(ship):
    if rules_planet(ship):
        if has_enough_money(ship, ship.ruler.technology.get_building_cost()):
            return True
        else:
            ship.ruler.log_message("Cannot buy building: not enough money")
    else:
        ship.ruler.log_message("Cannot buy building: not at own colony")
    return False

def cond_establish_colony(ship):
    if ship.planet is not None:
        if is_system_neutral(ship) or rules_system(ship) and not has_colony(ship):
            if has_buildings(ship, 2):
                return True
            else:
                ship.ruler.log_message("Cannot establish colony: not enough buildings in cargo")
        else:
            ship.ruler.log_message("Cannot establish colony: must be in a neutral system or own system at a planet "
                                   "without an existing colony")
    else:
        ship.ruler.log_message("Cannot establish colony: must be at planet")
    return False

def cond_collect_biomass(ship):
    if ship.planet is not None:
        if has_active_access(ship, 0):
            if ship.planet.ecology.biomass_level >= 1:
                return True
            else:
                ship.ruler.log_message("Cannot collect biomass: biomass on planet still regenerating")
        else:
            ship.ruler.log_message("Cannot collect biomass: need biological access")
    else:
        ship.ruler.log_message("Cannot collect biomass: must be at planet")
    return False

def cond_build_city(ship):
    if has_space_for_city(ship):
        if has_buildings(ship, 2):
            return True
        else:
            ship.ruler.log_message("Cannot build city: not enough buildings")
    else:
        ship.ruler.log_message("Cannot build city: number of cities cannot exceed habitability")

def cond_develop_colony(ship):
    if has_space_for_development(ship):
        if has_buildings(ship, 1):
            return True
        else:
            ship.ruler.log_message("Cannot develop: not enough buildings")
    else:
        ship.ruler.log_message("Cannot develop: must be at own colony with space for more development")

def cond_terraform(ship):
    if ship.planet is not None:
        if ship.planet.ecology.habitability < ecology.MAX_HABITABILITY:
            if ship.star.ruler is None or has_active_access(ship, 0):
                if ship.cargo.biomass.selected != -1:
                    if has_enough_biomass_to_terraform(ship):
                        if not planet_has_species(ship, ship.cargo.biomass.selected):
                            if has_enough_money(ship, ship.ruler.technology.get_terraform_monetary_cost()):
                                return True
                            else:
                                ship.ruler.log_message("Cannot terraform: not enough money")
                        else:
                            ship.ruler.log_message("Cannot terraform: selected species already present")
                    else:
                        ship.ruler.log_message("Cannot terraform: not enough biomass value in cargo")
                else:
                    ship.ruler.log_message("Cannot terraform: must select a species to add to planet")
            else:
                ship.ruler.log_message("Cannot terraform: need ecological access to terraform")
        else:
            ship.ruler.log_message("Cannot terraform: planet already at maximum habitability")
    else:
        ship.ruler.log_message("Cannot terraform: not at planet")
    return False

def cond_biology(ship):
    if has_enough_biomass(ship, 1):
        return True
    else:
        ship.ruler.log_message("Cannot do biology: minimum 1 biomass in cargo required")
    return False

def cond_fund_science(ship):
    return has_enough_money(ship, 100)

def cond_schmooze(ship):
    if ship.planet is not None and ship.planet.colony is not None:
        if ship.ruler is not ship.planet.colony.ruler:
            if has_active_access(ship, 1):
                return True
            else:
                ship.ruler.log_message("Cannot schmooze: need diplomatic access")
        else:
            ship.ruler.log_message("Cannot schmooze: cannot schmooze at own colonies")
    else:
        ship.ruler.log_message("Cannot schmooze: ship not at colony")
    return False

def cond_research(ship):
    if ship.planet is not None and ship.planet.colony is not None:
        if has_active_access(ship, 1):
            return True
        else:
            ship.ruler.log_message("Cannot research: need diplomatic access")
    else:
        ship.ruler.log_message("Cannot research: ship not at colony")
    return False

def cond_raid_minerals(ship):
    if ship.planet is not None and ship.planet.colony is not None:
        if has_hostile_access_versus(ship, ship.planet.colony.ruler, 1):
            if ship.planet.colony.minerals >= 1:
                return True
            else:
                ship.ruler.log_message("Cannot raid minerals: no minerals to take")
        else:
            ship.ruler.log_message("Cannot raid minerals: need piracy access")
    else:
        ship.ruler.log_message("Cannot raid minerals: ship not at colony")
    return False

def cond_raid_biomass(ship):
    if ship.planet is not None:
        if has_hostile_access_versus(ship, ship.planet.colony.ruler, 1):
            if ship.planet.ecology.biomass_level >= 1:
                return True
            else:
                ship.ruler.log_message("Cannot steal biomass: no biomass to take")
        else:
            ship.ruler.log_message("Cannot steal biomass: need piracy access")
    else:
        ship.ruler.log_message("Cannot steal biomass: ship not at planet")
    return False

def cond_besiege(ship):
    if ship.planet is not None and ship.planet.colony is not None:
        if has_hostile_access_versus(ship, ship.planet.colony.ruler, 3):
            return True
        else:
            ship.ruler.log_message("Cannot besiege: need siege access")
    else:
        ship.ruler.log_message("Cannot besiege: ship not at planet")
    return False

def cond_plunder(ship):
    if ship.planet is not None and ship.planet.colony is not None:
        if has_hostile_access_versus(ship, ship.planet.colony.ruler, 3):
            if ship.planet.colony.conqueror is ship.ruler:
                # If number of unconquered shields is less than the number of cities
                if ship.planet.colony.get_defense() - ship.planet.colony.conquered_shields < ship.planet.colony.cities:
                    return True
                else:
                    ship.ruler.log_message("Cannot plunder: cities must exceed number of unconquered shields")
            else:
                ship.ruler.log_message("Cannot plunder: another player is conquering the system")
        else:
            ship.ruler.log_message("Cannot plunder: need siege access")
    else:
        ship.ruler.log_message("Cannot plunder: ship not at planet")
    return False

def cond_consolidate(ship):
    if ship.planet is not None:
        if len(ship.planet.ships) > 1:
            return True
        else:
            ship.ruler.log_message("Cannot consolidate cargo: no other ships to take cargo from")
    else:
        ship.ruler.log_message("Cannot consolidate cargo: ship not at planet")
    return False


def act_collect_minerals(ship):
    ship.cargo.minerals[ship.planet.mineral] += 1
    ship.planet.colony.minerals -= 1

def act_sell_minerals(ship, mineral_index):
    ship.cargo.minerals[mineral_index] -= 1
    price = (ship.planet.colony.demand.get_price(mineral_index, ship.ruler))
    ship.ruler.money += price
    ship.ruler.milestone_progress[4] += price * MINERAL_SALE_MILESTONE_MODIFIER / MONEY_MILESTONE_VALUE + 1

def act_sell_artifact(ship):
    ship.cargo.artifacts -= 1
    ship.ruler.money += 500
    ship.ruler.technology.science[3] += ship.ruler.technology.get_artifact_science()
    ship.ruler.milestone_progress[4] += 500 / MONEY_MILESTONE_VALUE

def act_buy_building(ship):
    ship.ruler.money -= ship.ruler.technology.get_building_cost()
    ship.cargo.buildings += 1

def act_establish_colony(ship):
    new_colony = colony.Colony(ship.ruler, ship.planet)
    ship.planet.colony = new_colony
    # ship.ruler.colonies.append(new_colony)
    if ship.star.ruler is None:
        ship.ruler.milestone_progress[5] += 25
        ship.ruler.add_ruled_star(ship.star)
    ship.cargo.buildings -= 2
    ship.ruler.milestone_progress[5] += 15 + 10

def act_collect_biomass(ship):
    for i in range(len(ship.planet.ecology.species)):
        if ship.planet.ecology.species[i]:
            ship.cargo.biomass.change_quantity(i, 1)
    ship.planet.ecology.biomass_level = ship.ruler.technology.get_biomass_refund()
    ship.ruler.milestone_progress[2] += 2 * ship.planet.ecology.habitability

def act_build_city(ship):
    ship.planet.colony.cities += 1
    ship.cargo.buildings -= 2
    ship.ruler.milestone_progress[5] += 10

def act_develop_colony(ship):
    ship.planet.colony.development += 1
    ship.cargo.buildings -= 1
    ship.ruler.milestone_progress[5] += 5

def act_terraform(ship):
    ship.planet.ecology.species[ship.cargo.biomass.selected] = True
    cost = ship.planet.ecology.get_terraform_cost()
    ship.planet.ecology.habitability += 1
    ship.planet.ecology.biomass_level = ((ship.ruler.technology.get_biomass_refund() +
                                         (ship.planet.ecology.habitability - 1) * ship.planet.ecology.biomass_level)
                                         / ship.planet.ecology.habitability)
    spent = ship.cargo.biomass.empty()
    ship.ruler.money -= ship.ruler.technology.get_terraform_monetary_cost()
    ship.ruler.milestone_progress[2] += spent + 25
    ship.ruler.technology.science[2] += (spent - cost) * SCIENCE_PER_BIOLOGY

def act_biology(ship):
    spent = ship.cargo.biomass.empty()
    ship.ruler.milestone_progress[2] += spent
    ship.ruler.technology.science[2] += spent * SCIENCE_PER_BIOLOGY

def act_fund_science(ship):
    ship.ruler.money -= 100
    ship.ruler.technology.science[1] += 1

def act_schmooze(ship):
    ship.ruler.game.diplomacy.gain_leverage(ship.ruler.id, ship.star.ruler.id, 1)
    ship.ruler.milestone_progress[3] += 1

def act_research(ship):
    if ship.star.ruler is not ship.ruler:
        ship.ruler.game.diplomacy.gain_leverage(ship.ruler.id, ship.star.ruler.id,
                                                ship.ruler.technology.get_research_leverage())
        ship.ruler.milestone_progress[3] += ship.ruler.technology.get_research_leverage()
    ship.ruler.money += RESEARCH_MONEY
    ship.ruler.milestone_progress[4] += RESEARCH_MONEY / MONEY_MILESTONE_VALUE
    ship.ruler.technology.science[3] += ship.ruler.technology.get_mission_science()
    ship.star.ruler.technology.science[3] += ship.ruler.technology.get_mission_science()

def act_raid_minerals(ship):
    act_collect_minerals(ship)
    ship.ruler.milestone_progress[0] += 1
    ship.ruler.game.diplomacy.lose_leverage(ship.ruler.id, ship.star.ruler.id, 2)

def act_raid_biomass(ship):
    act_collect_biomass(ship)
    ship.ruler.milestone_progress[0] += ship.planet.ecology.habitability
    ship.ruler.game.diplomacy.lose_leverage(ship.ruler.id, ship.star.ruler.id, 2)

def act_besiege(ship):
    ship.planet.colony.receive_damage(ship.ruler)
    pass

def act_plunder(ship):
    ship.planet.colony.lose_city()
    ship.ruler.money += 500
    ship.ruler.milestone_progress[4] += 500 / MONEY_MILESTONE_VALUE
    ship.ruler.milestone_progress[0] += 10
    ship.ruler.game.diplomacy.lose_leverage(ship.ruler.id, ship.star.ruler.id, 10)

def act_consolidate(ship):
    for s in ship.planet.ships:
        if s is not ship and s.ruler is ship.ruler:
            ship.cargo.take_from(s.cargo)

def task_null(ship, game):
    pass

def task_explore_superficial(ship, game):
    if ship.destination_star is None or ship.ruler.explored_stars[ship.destination_star.id]:
        if ship.star is None:
            ship.set_destination_star(find_nearest_star(ship.location, game.galaxy))
        else:
            destination = None
            available_stars = find_stars_in_range(ship.star, 90, game.galaxy)
            for star_id in available_stars:
                if not ship.ruler.explored_stars[star_id]:
                    destination = game.galaxy.stars[star_id]
                    break
            if destination is not None:
                ship.set_destination_star(destination)
            else:
                ship.task = 0

class Action:

    def __init__(self, condition_fn, action_fn, rate_fn, repeat=False):
        self.condition_fn = condition_fn
        self.action_fn = action_fn
        self.rate_fn = rate_fn
        self.repeat = repeat

    def perform(self, ship, time):
        if self.condition_fn(ship):
            ship.action_progress += time * self.rate_fn()
            if ship.action_progress >= 1.0:
                self.action_fn(ship)
                if not self.repeat:
                    ship.set_action(0)
                else:
                    ship.action_progress = 0.0
        else:
            ship.set_action(0)


# Ship action macros consist of four elements:
# 0 - A function that takes a ship and returns a boolean - this is the condition needed to be fulfilled to do the action
# 1 - A function that takes a ship and has no return value - this is the effect of the action, once completed
# 2 - A function that takes a TechnologyTree object and returns a function which gives the rate, per minute, of the
#     action being completed. Many might not use the TechnologyTree passed, but it will be passed.
# 3 - A boolean value that says whether or not the action automatically repeats after completion
SHIP_ACTIONS = [
    (lambda a: False, lambda a: None, lambda t: lambda: 0, False),
    (lambda a: False, lambda a: None, lambda t: lambda: 0, False),
    (cond_build_city, act_build_city, lambda t: lambda: CITY_PLACEMENT_RATE, False),
    (cond_develop_colony, act_develop_colony, lambda t: lambda: DEVELOPMENT_PLACEMENT_RATE, False),
    (cond_establish_colony, act_establish_colony, lambda t: lambda: COLONY_PLACEMENT_RATE, False),
    (cond_collect_biomass, act_collect_biomass, lambda t: t.get_biomass_collection_rate, False),
    (cond_terraform, act_terraform, lambda t: t.get_terraform_rate, False),
    (cond_collect_minerals, act_collect_minerals, lambda t: t.get_cargo_transfer_rate, True),
    (lambda ship: cond_sell_minerals(ship, 0), lambda ship: act_sell_minerals(ship, 0),
     lambda t: t.get_cargo_transfer_rate, True),
    (lambda ship: cond_sell_minerals(ship, 1), lambda ship: act_sell_minerals(ship, 1),
     lambda t: t.get_cargo_transfer_rate, True),
    (lambda ship: cond_sell_minerals(ship, 2), lambda ship: act_sell_minerals(ship, 2),
     lambda t: t.get_cargo_transfer_rate, True),
    (lambda ship: cond_sell_minerals(ship, 3), lambda ship: act_sell_minerals(ship, 3),
     lambda t: t.get_cargo_transfer_rate, True),
    (lambda ship: cond_sell_minerals(ship, 4), lambda ship: act_sell_minerals(ship, 4),
     lambda t: t.get_cargo_transfer_rate, True),
    (lambda ship: cond_sell_minerals(ship, 5), lambda ship: act_sell_minerals(ship, 5),
     lambda t: t.get_cargo_transfer_rate, True),
    (cond_sell_artifact, act_sell_artifact, lambda t: t.get_cargo_transfer_rate, False),
    (cond_buy_building, act_buy_building, lambda t: t.get_cargo_transfer_rate, False),
    (cond_biology, act_biology, lambda t: t.get_cargo_transfer_rate, False),
    (cond_fund_science, act_fund_science, lambda t: lambda: 2400.0, False),
    (cond_schmooze, act_schmooze, lambda t: t.get_schmooze_power, True),
    (cond_research, act_research, lambda t: lambda: RESEARCH_RATE, True),
    (cond_raid_minerals, act_raid_minerals, lambda t: t.get_raid_rate, True),
    (cond_raid_biomass, act_raid_biomass, lambda t: t.get_biomass_collection_rate, False),
    (cond_besiege, act_besiege, lambda t: t.get_ship_firerate, True),
    (cond_plunder, act_plunder, lambda t: t.get_raid_rate, False),
    (cond_consolidate, act_consolidate, lambda t: t.get_cargo_transfer_rate, False),
]
