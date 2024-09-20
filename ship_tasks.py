import math

def find_nearest_star(position, game, blacklist=()):
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
