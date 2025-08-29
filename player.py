import math
import random

import diplomacy
import ship
import ship_tasks
import technology
import visibility

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
        # self.colonies = []
        self.ruled_stars = []
        self.explored_stars = []
        self.visibility = visibility.StarVisibility(self.game.galaxy, self)
        self.reset_explored_stars()
        self.milestone_progress = [0, 0, 0, 0, 0, 0]
        self.technology = technology.TechnologyTree(self)
        self.controller = PlayerController(self)
        self.log = []

    def add_ship(self, planet):
        self.ships.append(ship.Ship(planet.star.location, self))
        self.ships[-1].destination_star = planet.star
        self.ships[-1].destination_planet = planet
        self.ships[-1].enter_star()
        self.ships[-1].enter_planet()

    def is_ship_visible(self, ship_obj):
        if ship_obj.ruler is self:
            return True
        if ship_obj.star is not None:
            return self.visibility.get_visible(ship_obj.star)
        for s in self.ships:
            if s.star is None or s.star.ruler is not self:
                if s.get_distance_to(ship_obj.location) < self.technology.get_visibility_range():
                    return True
        return False

    def add_ruled_star(self, star):
        if star.ruler is not None:
            star.ruler.remove_ruled_star(star)
        if len(self.ruled_stars) > 0:
            star.connected_star = self.game.galaxy.get_closest_star_from_player(star.id, self)
        star.ruler = self
        self.ruled_stars.append(star)
        self.visibility.reset_permanent_visibility()

    def remove_ruled_star(self, star):
        if star in self.ruled_stars:
            self.ruled_stars.remove(star)
            for s in self.ruled_stars:
                if s.connected_star == star:
                    s.connected_star = star.connected_star
            star.ruler = None
        self.visibility.reset_permanent_visibility()

    def reset_explored_stars(self):
        self.explored_stars = [False for _ in range(len(self.game.galaxy.stars))]

    def log_message(self, message):
        self.log.append(f"[Player{self.id}] {message}")
        print(self.log[-1])

class PlayerController:

    def __init__(self, player):
        self.player = player
        self.actions = [ship_tasks.Action(item[0], item[1], item[2](self.player.technology), item[3])
                        for item in ship_tasks.SHIP_ACTIONS]

    def do_action(self, action_idx, ship_obj, time):
        self.actions[action_idx].perform(ship_obj, time)
