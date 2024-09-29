import trade

MINERAL_PER_DEVELOPMENT_PER_MINUTE = 1
HOMEWORLD_PRODUCTION_FACTOR = 1  # amount by which production is divided for homeworld
MAX_DEVELOPMENT_PER_CITY_PER_HABITABILITY = 1
MINERAL_CAPACITY_PER_CITY = 5

class Colony(object):

    def __init__(self, player, planet):
        self.ruler = player
        self.planet = planet
        self.cities = 1
        self.development = 0
        self.minerals = 0
        self.demand = trade.Demand(self)

    def get_maximum_cities(self):
        return max(1, self.planet.get_habitability())

    def get_production(self, time):
        return self.development * time * MINERAL_PER_DEVELOPMENT_PER_MINUTE
    
    def get_mineral_capacity(self):
        return self.cities * MINERAL_CAPACITY_PER_CITY
    
    def get_maximum_development(self):
        return self.planet.get_habitability() * self.cities * MAX_DEVELOPMENT_PER_CITY_PER_HABITABILITY
    
    def produce(self, time):
        self.minerals = min(self.get_mineral_capacity(), self.minerals + self.get_production(time))

    def get_defense(self):
        return self.cities


class HomeworldColony(Colony):

    def __init__(self, player, planet):
        super(HomeworldColony, self).__init__(player, planet)
        self.cities = self.get_maximum_cities()
        self.development = self.get_maximum_development() // 2

    def get_maximum_cities(self):
        return 1 + 2 * self.planet.get_habitability()

    def get_maximum_development(self):
        return self.cities
    
    def get_production(self, time):
        return super(HomeworldColony, self).get_production(time) / HOMEWORLD_PRODUCTION_FACTOR
