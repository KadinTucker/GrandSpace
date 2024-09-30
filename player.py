import math
import random

import diplomacy
import ship
import technology

STARTING_MONEY = 1000
BASE_MILESTONE_COST = 50

class Game:

    def __init__(self, n_players, galaxy_obj):
        self.galaxy = galaxy_obj
        self.players = [Player(self, i) for i in range(n_players)]
        self.diplomacy = diplomacy.Diplomacy(self)

def get_milestone_cost(milestone):
    return BASE_MILESTONE_COST * milestone * (milestone + 1)

def get_milestone_from_progress(cost):
    return (math.sqrt(1 + 4 * cost / BASE_MILESTONE_COST) - 1) / 2

class Player:

    def __init__(self, game, p_id):
        self.game = game
        self.id = p_id
        self.money = STARTING_MONEY
        self.color = (random.randint(20, 255), random.randint(20, 255), random.randint(20, 255))
        self.ships = []
        self.selected_ship = None
        self.homeworld = None
        self.colonies = []
        self.ruled_stars = []
        self.explored_stars = []
        self.reset_explored_stars()
        self.milestone_progress = [0, 0, 0, 0, 0, 0]
        self.technology = technology.TechnologyTree(self)

    def add_ship(self, planet):
        self.ships.append(ship.Ship(planet.star.location, self))
        self.ships[-1].destination_star = planet.star
        self.ships[-1].destination_planet = planet

    def add_ruled_star(self, star):
        if star.ruler is not None:
            star.ruler.remove_ruled_star(star)
        if len(self.ruled_stars) > 0:
            star.connected_star = self.game.galaxy.get_closest_star_from_player(star.id, self)
        star.ruler = self
        self.ruled_stars.append(star)

    def remove_ruled_star(self, star):
        if star in self.ruled_stars:
            self.ruled_stars.remove(star)
            for s in self.ruled_stars:
                if s.connected_star == star:
                    s.connected_star = star.connected_star
            star.ruler = None

    def reset_explored_stars(self):
        self.explored_stars = [False for _ in range(len(self.game.galaxy.stars))]
