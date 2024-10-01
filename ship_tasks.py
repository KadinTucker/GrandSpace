import math

import colony
import ecology
import technology

FULL_HEAL_RATE = 3.0
SYSTEM_CHANGE_RATE = 120.0
PLANET_CHANGE_RATE = 180.0
COLONY_PLACEMENT_RATE = 60.0
CITY_PLACEMENT_RATE = 120.0
DEVELOPMENT_PLACEMENT_RATE = 120.0
TERRAFORM_RATE = 6.0

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

def has_access(ship, access_index):
    return (ship.star is not None and (ship.star.ruler is None
            or ship.ruler.game.diplomacy.access_matrix[ship.ruler.id][ship.star.ruler.id][access_index]))

def is_system_neutral(ship):
    return ship.star.ruler is None

def is_at_colony(ship):
    return ship.planet is not None and ship.planet.colony is not None

def rules_system(ship):
    return ship.star is not None and ship.ruler is ship.star.ruler

def rules_planet(ship):
    return ship.planet is not None and ship.planet.colony is not None and ship.planet.colony.ruler is ship.ruler

def has_species(ship, species_index):
    return species_index != -1 and ship.planet is not None and ship.planet.ecology.species[species_index]

def can_be_terraformed(ship):
    return ship.planet is not None and ship.planet.ecology.habitability < ecology.MAX_HABITABILITY

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
    # Either: this ship has access to battle the other, or the other ship does not have passage and we are in a
    # system ruled by this ship
    return ship.star is other.star and (ship.ruler.game.diplomacy.access_matrix[other.ruler.id][ship.ruler.id][5]
                                        or (rules_system(ship) and not has_access(other, 3)))

def cond_establish_colony(ship):
    return ((is_system_neutral(ship) or rules_system(ship) and not has_colony(ship))
            and has_buildings(ship, 2) and ship.planet is not None)

def cond_collect_biomass(ship):
    return has_access(ship, 0) and ship.planet is not None and ship.planet.ecology.biomass_level >= 1

def cond_build_city(ship):
    return has_space_for_city(ship) and has_buildings(ship, 2)

def cond_develop_colony(ship):
    return has_space_for_development(ship) and has_buildings(ship, 1)

def cond_terraform(ship):
    return (ship.planet is not None and has_enough_biomass_to_terraform(ship) and can_be_terraformed(ship)
            and has_enough_money(ship, ship.ruler.technology.get_terraform_monetary_cost()))
def act_establish_colony(ship):
    new_colony = colony.Colony(ship.ruler, ship.planet)
    ship.planet.colony = new_colony
    ship.ruler.colonies.append(new_colony)
    if ship.star.ruler is None:
        ship.ruler.milestone_progress[5] += 25
        ship.ruler.add_ruled_star(ship.star)
    ship.cargo.buildings -= 2
    ship.ruler.milestone_progress[5] += 15 + 10

def act_collect_biomass(ship):
    for i in range(len(ship.planet.ecology.species)):
        if ship.planet.ecology.species[i]:
            ship.cargo.biomass.change_quantity(i, 1)
    ship.planet.ecology.biomass_level = 0

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
    ship.planet.ecology.habitability += 1
    spent = ship.cargo.biomass.empty()
    ship.ruler.money -= ship.ruler.technology.get_terraform_monetary_cost()
    ship.ruler.milestone_progress[2] += spent + 25

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

    def __init__(self, condition, action, rate):
        self.condition = condition
        self.action = action
        self.rate = rate

    def perform(self, ship, time):
        if self.condition(ship):
            ship.action_progress += time * self.rate()
            if ship.action_progress >= 1.0:
                self.action(ship)
                ship.set_action(0)
        else:
            ship.set_action(0)


# TODO: make it possible to vary with tech
SHIP_ACTIONS = [
    Action(lambda a: False, lambda a: None, lambda: 0),
    Action(lambda a: False, lambda a: None, lambda: 0),
    Action(cond_build_city, act_build_city, lambda: CITY_PLACEMENT_RATE),
    Action(cond_develop_colony, act_develop_colony, lambda: DEVELOPMENT_PLACEMENT_RATE),
    Action(cond_establish_colony, act_establish_colony, lambda: COLONY_PLACEMENT_RATE),
    Action(cond_collect_biomass, act_collect_biomass, lambda: technology.BIOMASS_COLLECTION_RATE_BASE),
    Action(cond_terraform, act_terraform, lambda: TERRAFORM_RATE)
]
