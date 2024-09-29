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
LIFE_DENSITY = 0.5  # approximate fraction of stars one expects to have life (in reality, less if higher)

def generate_galaxy_boxes(width, height, radius):
    stars = []
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
            stars.append(Star(i, (int(basex), int(basey)), random.randint(1, 5)))
            i += 1
    return stars

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
    def __init__(self, stars):
        # list of Star objects, indexed by their id fields
        self.stars = stars
        # a matrix (symmetric square) giving the distance as the space-crow flies between all stars
        self.star_distance_matrix = []
        # once initialised, entry i consists of a sorted list of the star id numbers by distance to the star
        # with id i, excluding the star i itself
        self.star_distance_hierarchy = []
        self.init()

    def generate_star_distance_matrix(self):
        self.star_distance_matrix = [[-1.0 for _ in range(len(self.stars))] for _ in range(len(self.stars))]
        for i in range(len(self.stars)):
            for j in range(len(self.stars)):
                self.star_distance_matrix[i][j] = math.hypot(self.stars[i].location[0] - self.stars[j].location[0],
                                                             self.stars[i].location[1] - self.stars[j].location[1])

    def generate_star_distance_hierarchy(self):
        for i in range(len(self.stars)):
            self.star_distance_hierarchy.append(sorted([j for j in range(len(self.stars)) if j != i],
                                                key=lambda k: self.star_distance_matrix[i][k]))

    def init(self):
        self.generate_star_distance_matrix()
        self.generate_star_distance_hierarchy()

    def get_closest_star(self, origin_id):
        return self.stars[self.star_distance_hierarchy[origin_id][0]]

    def get_closest_star_from_player(self, origin_id, player):
        for star_id in self.star_distance_hierarchy[origin_id]:
            if self.stars[star_id].ruler is player:
                return self.stars[star_id]
        return self.stars[origin_id]
