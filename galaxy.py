import random
import math

import colony
import ship

"""
Galaxy Generation Procedures:
 - Boxes: star systems are located in "boxes", then moved around within their boxes with some noise. Boxes are placed in a "circle packing" manner.
"""

SQRT3 = math.sqrt(3)

#SPICE_COLORS = [(200, 75, 20), (160, 200, 25), (50, 75, 200), (50, 200, 75), (200, 100, 160), (120, 20, 160)]
MINERAL_COLORS = [(200, 20, 20), (20, 200, 20), (20, 20, 200), (200, 200, 20), (200, 20, 200), (20, 200, 200)]
# Expected number of artifacts in the galaxy
ARTIFACT_TOTAL = 25
AVERAGE_PLANETS = 3

def generateGalaxyBoxes(galaxy, width, height, radius):
    i = 0
    for x in range(width):
        for y in range(height):
            basex = radius * (1 + 2 * x)
            basey = radius * (1 + SQRT3 * y)
            if y % 2 == 1:
                basex += radius
            randomRadius = random.random()**2 * radius
            randomAngle = random.random() * 2 * math.pi
            basex += math.cos(randomAngle) * randomRadius
            basey += math.sin(randomAngle) * randomRadius
            galaxy.stars.append(Star(i, (int(basex), int(basey)), random.randint(1, 5)))
            i += 1

def populate_homeworlds(galaxy, game):
    for p in range(len(game.players)):
        game.players[p].reset_explored_stars()
        star = galaxy.stars[int((len(galaxy.stars) - 1) * float(p) / len(game.players))]
        while len(star.planets) < 5:
            star.planets.append(Planet(star))
        star.planets[0].colony = colony.HomeworldColony(game.players[p], star.planets[0])
        star.ruler = game.players[p]
        game.players[p].explored_stars[int((len(galaxy.stars) - 1) * float(p) / len(game.players))] = True
        game.players[p].ships.append(ship.Ship(star.location, game.players[p]))
        game.players[p].ships[-1].destination_star = star
        game.players[p].ships[-1].enter_star()
        game.players[p].ships[-1].destination_planet = star.planets[0]
        game.players[p].ships[-1].enter_planet()

def populate_artifacts(galaxy):
    for s in galaxy.stars:
        for p in s.planets:
            if random.random() < float(ARTIFACT_TOTAL) / AVERAGE_PLANETS / len(galaxy.stars):
                p.artifacts = 1

class Planet():
    def __init__(self, star):
        self.star = star # Star object
        self.mineral = random.randint(0, 5)
        self.artifacts = 0 # Integer number of artifacts
        self.colony = None
        self.ships = []
    
    def get_habitability(self):
        return 0 # Remains to be implemented
    
class Star():
    def __init__(self, id, location, numPlanets):
        self.id = id
        self.location = location # tuple
        self.planets = [] # list of Planet objects
        for _ in range(numPlanets):
            self.planets.append(Planet(self))
        self.ruler = None # Player object
        self.ships = []

class Galaxy():
    def __init__(self):
        self.stars = [] # list of Star objects