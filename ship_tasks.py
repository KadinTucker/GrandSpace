import math

# TODO: implement a fast pathing system, implementing Dijkstra's algorithm and storing, in stars, sorted lists
#  of stars' distances to each other from shortest to longest, to quickly easily find the best path to follow
#  and initialising that pathing information before game run
def find_nearest_star(position, game, blacklist=()):
    """
    Finds the nearest star to the ship, except for a possible blacklist
    To be used only when the ship is not currently located at a star
    """
    nearest = None
    min_distance = -1
    for s in game.galaxy.stars:
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

def task_null(ship, game):
    pass

def task_explore_superficial(ship, game):
    if ship.destination_star is None or ship.ruler.explored_stars[ship.destination_star.id]:
        explored = get_explored_stars(ship.ruler, game.galaxy)
        destination = find_nearest_star(ship.location, game, explored)
        if destination is not None:
            ship.set_destination_star(destination)
        else:
            ship.task = 0
