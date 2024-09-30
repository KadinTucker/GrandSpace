import math

import ecology

# TODO: implement a fast pathing system, implementing Dijkstra's algorithm and storing, in stars, sorted lists
#  of stars' distances to each other from shortest to longest, to quickly easily find the best path to follow
#  and initialising that pathing information before game run
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
