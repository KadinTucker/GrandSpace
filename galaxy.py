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
ARTIFACT_TOTAL_PER_STAR = 0.5
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
        self.connected_star = None  # for the purpose of drawing connection lines
        self.ships = []

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

    def populate_homeworlds(self, game):
        star_ids = [i for i in range(len(self.stars))]
        random.shuffle(star_ids)
        for p in range(len(game.players)):
            # Reset the player's explored stars to nothing
            game.players[p].reset_explored_stars()
            # Select a star for the homeworld, in a way such that the same cannot be chosen for two players
            star = self.stars[star_ids[p]]
            # Home systems always have 5 planets
            while len(star.planets) < 5:
                star.planets.append(Planet(star))
            # Choose a random planet on which to place the homeworld
            planet = random.choice(star.planets)
            # Instantiate the colony object, and add it to the player's list of colonies
            new_colony = colony.HomeworldColony(game.players[p], planet)
            game.players[p].colonies.append(new_colony)
            # Set the player's unique homeworld field to be the planet chosen
            game.players[p].homeworld = planet
            # Add the colony to the planet
            planet.colony = new_colony
            # Make the player rule their home system
            game.players[p].add_ruled_star(star)
            star.ruler = game.players[p]
            # Add a ship to the homeworld, and select it immediately
            game.players[p].add_ship(planet)
            game.players[p].selected_ship = game.players[p].ships[0]
            # The player has explored its home system
            game.players[p].explored_stars[star.id] = True

    def populate_artifacts(self):
        for s in self.stars:
            for p in s.planets:
                if random.random() < float(ARTIFACT_TOTAL_PER_STAR) / AVERAGE_PLANETS:
                    p.artifacts = 1

    def populate_life(self, game):
        """
        Adds ecological life to the galaxy
        Adds three unique species to each homeworld, and then distributes species found on at least one
        homeworld randomly across the galaxy a certain number of times
        """
        species = [i for i in range(len(ecology.BIOMASS_TYPES))]
        random.shuffle(species)
        # Start by adding species to players' homeworlds
        for p in range(len(game.players)):
            for i in range(3):
                game.players[p].homeworld.ecology.species[species[p * 3 + i]] = True
                game.players[p].homeworld.ecology.habitability += 1
            game.players[p].homeworld.colony.cities = game.players[p].homeworld.colony.get_maximum_cities()
            game.players[p].homeworld.colony.development = game.players[p].homeworld.colony.get_maximum_development()//2
        num_species = len(game.players) * 3
        for _ in range(int(len(self.stars) * LIFE_DENSITY / num_species)):
            for i in range(num_species):
                star = random.choice(self.stars)
                if star.ruler is not None:
                    continue
                planet = random.choice(star.planets)
                if planet.ecology.species[species[i]]:
                    continue
                planet.ecology.habitability += 1
                planet.ecology.species[species[i]] = True
