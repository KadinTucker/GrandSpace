import random
import math

import colony
import ecology

"""
Galaxy Generation Procedures:
 - Boxes: star systems are located in "boxes", then moved around within their boxes with some noise. Boxes are placed 
          in a "circle packing" manner.
"""

SQRT3 = math.sqrt(3)

DISTANCE_RATIO_TOLERANCE = 1.5

MINERAL_COLORS = [(200, 20, 20), (20, 200, 20), (20, 20, 200), (20, 200, 200), (200, 20, 200), (200, 200, 20)]
# Expected number of artifacts in the galaxy
ARTIFACT_TOTAL = 25
AVERAGE_PLANETS = 3
LIFE_DENSITY = 2.5  # approximate fraction of stars one expects to have life (in reality, less if higher)

def generate_galaxy_boxes(galaxy, width, height, radius):
    i = 0
    for x in range(width):
        for y in range(height):
            basex = radius * (1 + 2 * x)
            basey = radius * (1 + SQRT3 * y)
            if y % 2 == 1:
                basex += radius
            random_radius = random.random()**2 * radius
            random_angle = random.random() * 2 * math.pi
            basex += math.cos(random_angle) * random_radius
            basey += math.sin(random_angle) * random_radius
            galaxy.stars.append(Star(i, (int(basex), int(basey)), random.randint(1, 5)))
            i += 1

def populate_homeworlds(galaxy, game):
    species = [i for i in range(len(ecology.BIOMASS_TYPES))]
    random.shuffle(species)
    for p in range(len(game.players)):
        game.players[p].reset_explored_stars()
        star = random.choice(galaxy.stars)
        while len(star.planets) < 5:
            star.planets.append(Planet(star))
        planet = random.choice(star.planets)
        planet.ecology.habitability = 3
        for i in range(3):
            planet.ecology.species[species[3 * p + i]] = True
        new_colony = colony.HomeworldColony(game.players[p], planet)
        game.players[p].colonies.append(new_colony)
        game.players[p].homeworld = planet
        planet.colony = new_colony
        game.players[p].add_ruled_star(star)
        star.ruler = game.players[p]
        game.players[p].add_ship(planet)
        game.players[p].selected_ship = game.players[p].ships[0]
        game.players[p].explored_stars[star.id] = True
    populate_life(galaxy, len(game.players) * 3, species, int(LIFE_DENSITY * len(galaxy.stars) / len(game.players) / 3))

def populate_artifacts(galaxy):
    for s in galaxy.stars:
        for p in s.planets:
            if random.random() < float(ARTIFACT_TOTAL) / AVERAGE_PLANETS / len(galaxy.stars):
                p.artifacts = 1

def populate_life(galaxy, num_species, species_list, num_repeats):
    for _ in range(num_repeats):
        for i in range(num_species):
            star = random.choice(galaxy.stars)
            planet = random.choice(star.planets)
            planet.ecology.habitability += 1
            planet.ecology.species[species_list[i]] = True

def get_closest_star_index(target, star_domain):
    min_distance = -1
    min_star_index = -1
    for s in range(len(star_domain)):
        if s != target:
            distance = math.hypot(star_domain[s].location[0] - target.location[0],
                                  star_domain[s].location[1] - target.location[1])
            if min_star_index == -1 or distance < min_distance:
                min_star_index = s
                min_distance = distance
    return min_star_index

def get_closest_star(target, star_domain):
    index = get_closest_star_index(target, star_domain)
    if index == -1:
        return None
    return star_domain[index]

class Planet:
    def __init__(self, star):
        self.star = star  # Star object
        self.mineral = random.randint(0, 5)
        self.artifacts = 0  # Integer number of artifacts
        self.colony = None
        self.ecology = ecology.Ecology(self)
        self.ships = []
    
    def get_habitability(self):
        return self.ecology.habitability
    
class Star:
    def __init__(self, s_id, location, num_planets):
        self.id = s_id
        self.location = location  # tuple
        self.planets = []  # list of Planet objects
        for _ in range(num_planets):
            self.planets.append(Planet(self))
        self.ruler = None  # Player object
        self.ships = []
        self.connected_star = None  # Connected star, for drawing purposes

class Galaxy:
    def __init__(self):
        self.stars = []  # list of Star objects
