import random

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

        self.explored_stars = []
        self.reset_explored_stars()

    def reset_explored_stars(self):
        self.explored_stars = [False for _ in range(len(self.game.galaxy.stars))]