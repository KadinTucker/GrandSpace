import trade

MINERAL_PER_DEVELOPMENT_PER_MINUTE = 1
HOMEWORLD_PRODUCTION_FACTOR = 1  # amount by which production is divided for homeworld
MAX_DEVELOPMENT_PER_CITY_PER_HABITABILITY = 1

SHIELD_HEALTH = 20
HEALING_PER_MINUTE = 3

class Colony(object):

    def __init__(self, player, planet):
        self.ruler = player
        self.planet = planet
        self.cities = 1
        self.development = 0
        self.minerals = 0
        self.demand = trade.Demand(self)
        self.conqueror = None
        self.conquered_shields = 0
        self.damage = 0

    def get_maximum_cities(self):
        return max(1, self.planet.get_habitability())

    def get_production(self, time):
        return self.development * time * MINERAL_PER_DEVELOPMENT_PER_MINUTE
    
    def get_mineral_capacity(self):
        return self.cities * self.ruler.technology.get_mineral_storage()
    
    def get_maximum_development(self):
        return (self.planet.get_habitability() * self.cities * MAX_DEVELOPMENT_PER_CITY_PER_HABITABILITY
                + self.cities * self.ruler.technology.get_bonus_development_per_city())

    def do_tick(self, time):
        self.repair(time)
        self.produce(time)
        self.demand.progress_demand(time)
    
    def produce(self, time):
        if self.damage <= 0:
            self.minerals = min(self.get_mineral_capacity(), self.minerals + self.get_production(time))
            self.conqueror = None
            self.damage = 0

    def lose_city(self):
        self.cities -= 1
        self.development = min(self.get_maximum_development(), self.development)
        self.minerals = min(self.get_mineral_capacity(), self.minerals)
        self.damage -= SHIELD_HEALTH
        self.repair(0)
        if self.cities <= 0:
            self.planet.colony = None

    def repair(self, time):
        if self.damage > 0:
            self.damage -= HEALING_PER_MINUTE * time
            if self.damage < self.conquered_shields * SHIELD_HEALTH:
                self.conquered_shields -= 1

    def get_defense(self):
        return self.cities + self.ruler.technology.get_bonus_shields()

    def is_conquered(self):
        return self.conquered_shields >= self.get_defense()

    def receive_damage(self, dealer):
        # Start by determining the conqueror. If a different player from the original, they have to undo the progress
        # of the original conqueror first.
        if self.conqueror is None:
            self.conqueror = dealer
        if self.conqueror is dealer:
            self.damage += 1
        else:
            self.damage -= 1
        # Determine if a new shield becomes conquered
        if self.damage >= SHIELD_HEALTH * (1 + self.conquered_shields):
            self.conquered_shields += 1
            if self.get_defense() - self.conquered_shields <= self.cities:
                # Collateral damage
                # self.development = max(self.development - 1, 0)
                # Edited out for now, because of possible looping repair<->damage to make for too much damage
                pass
            self.get_conquered()

    def get_conquered(self):
        if self.conquered_shields >= self.get_defense():
            # Get conquered: check if all colonies in the system are also conquered.
            unconquered = False
            for p in self.planet.star.planets:
                if p.colony is not None and not p.colony.is_conquered():
                    unconquered = True
                    break
            if not unconquered:
                for p in self.planet.star.planets:
                    if p.colony is not None:
                        self.conqueror.game.diplomacy.lose_leverage(self.conqueror.id, p.colony.ruler.id,
                                                                    5 * p.colony.cities)
                        self.conqueror.milestone_progress[0] += 10 * p.colony.cities
                        p.colony.ruler = self.conqueror
                self.conqueror.milestone_progress[5] += 25
                self.planet.star.ruler.remove_ruled_star(self.planet.star)
                self.conqueror.add_ruled_star(self.planet.star)
                self.conqueror = None
                self.conquered_shields = 0
                self.damage = 0


class HomeworldColony(Colony):

    def __init__(self, player, planet):
        super(HomeworldColony, self).__init__(player, planet)
        self.cities = self.get_maximum_cities()
        self.development = self.get_maximum_development() // 2

    def get_maximum_cities(self):
        return 1 + 2 * self.planet.get_habitability()

    def get_maximum_development(self):
        return self.cities * (1 + self.ruler.technology.get_bonus_development_per_city())
    
    def get_production(self, time):
        return super(HomeworldColony, self).get_production(time) / HOMEWORLD_PRODUCTION_FACTOR
