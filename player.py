import random

import galaxy
import ship

class Game():

    def __init__(self, n_players, galaxy):
        self.galaxy = galaxy
        self.players = [Player(self, i) for i in range(n_players)]
        self.leverages = [[0 for _ in range(n_players)] for _ in range(n_players)]

class Player():

    def __init__(self, game, id):
        self.game = game
        self.id = id
        self.money = 99999999
        self.color = (random.randint(20, 255), random.randint(20, 255), random.randint(20, 255))
        self.ships = []
        self.selected_ship = None
        self.colonies = []
        self.ruled_stars = []
        self.star_network = []
        self.explored_stars = []
        self.reset_explored_stars()
        self.status_updated = False

    def add_ship(self, planet):
        self.ships.append(ship.Ship(planet.star.location, self))
        self.ships[-1].destination_star = planet.star
        self.ships[-1].enter_star()
        self.ships[-1].destination_planet = planet
        self.ships[-1].enter_planet()

    def add_ruled_star(self, star):
        # TODO: if there is a previous ruler, remove the star from their previous rule
        self.star_network.append(galaxy.get_closest_star_index(star, self.ruled_stars))
        self.ruled_stars.append(star)

    def reset_explored_stars(self):
        self.explored_stars = [False for _ in range(len(self.game.galaxy.stars))]