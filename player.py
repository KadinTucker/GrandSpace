import random

import galaxy
import ship

class Game:

    def __init__(self, n_players, galaxy_obj):
        self.galaxy = galaxy_obj
        self.players = [Player(self, i) for i in range(n_players)]
        self.leverages = [[0 for _ in range(n_players)] for _ in range(n_players)]

class Player:

    def __init__(self, game, p_id):
        self.game = game
        self.id = p_id
        self.money = 0
        self.color = (random.randint(20, 255), random.randint(20, 255), random.randint(20, 255))
        self.ships = []
        self.selected_ship = None
        self.homeworld = None
        self.colonies = []
        self.ruled_stars = []
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
        if star.ruler is not None:
            star.ruler.remove_ruled_star(star)
        star.connected_star = galaxy.get_closest_star(star, self.ruled_stars)
        self.ruled_stars.append(star)
        star.ruler = self

    def remove_ruled_star(self, star):
        if star in self.ruled_stars:
            self.ruled_stars.remove(star)
            for s in self.ruled_stars:
                if s.connected_star == star:
                    s.connected_star = star.connected_star
            star.ruler = None

    def reset_explored_stars(self):
        self.explored_stars = [False for _ in range(len(self.game.galaxy.stars))]
