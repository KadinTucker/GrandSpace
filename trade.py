import random

TRADE_MAX_DEMAND = 9

TRADE_DEMAND_INCREASE_CHANCE = 65
TRADE_DEMAND_DECREASE_CHANCE = 25
TRADE_DEMAND_RESET_CHANCE = 5
TRADE_DEMAND_CITY_BOOST = 5

TRADE_DEMAND_BASE_PROB = 0.25
TRADE_DEMAND_PROB_CITY_BOOST = 0.1

TRADE_DEMAND_MODIFY_PER_MINUTE = 1.0  # in changes per minute

TRADE_PRICE_PER_DEMAND = 25
TRADE_MINIMUM_PRICE = 25
TRADE_WHOLESALE_PRICE = 50

class Demand:

    def __init__(self, colony):
        self.colony = colony
        self.possible_demands = [i for i in range(6)]
        self.possible_demands.remove(self.colony.planet.mineral)
        self.change_progress = 0.0
        self.mineral_demanded = -1
        self.demand_quantity = 0

    def reset_demand(self):
        # self.possible_demands.append(self.mineral_demanded)
        self.mineral_demanded = -1
        self.demand_quantity = 0

    def set_new_mineral_demand(self):
        new_demand = random.choice(self.possible_demands)
        # self.possible_demands.remove(new_demand)
        self.mineral_demanded = new_demand
        self.demand_quantity = 1

    def modify_mineral_demand(self):
        """
        Modify the mineral demand randomly, as happens periodically
        The chance for demand to increase increases with number of cities
        (THE FOLLOWING TABLE IS DEPRECATED)
        The following table is for base increase change of 5, base decrease of 4, base reset of 1:
         - num cities | increase chance | decrease chance | reset chance
         -      1              50%              40%             10%
         -      2              67%              27%             7%          * values are rounded
         -      3              75%              20%             5%
         -      4              80%              16%             4%
         -      5              83%              13%             3%          * values are rounded
         -      6              86%              11%             3%          * values are rounded
         -      7              87%              11%             2%          * values are rounded
        (CURRENT TABLE)
        The following table is for base increase change of 6, base decrease of 3, base reset of 1:
         - num cities | increase chance | decrease chance | reset chance
         -      1              60%              35%             5%
         -      2              67%              29%             4%
         -      3              71%              25%             4%
         -      ≥4             75%              22%             3%
        """
        roll = random.random()
        increase = TRADE_DEMAND_CITY_BOOST * min(3, (self.colony.cities - 1)) + TRADE_DEMAND_INCREASE_CHANCE
        decrease = TRADE_DEMAND_DECREASE_CHANCE
        reset = TRADE_DEMAND_RESET_CHANCE
        total = increase + decrease + reset
        if roll < increase / total:
            self.demand_quantity += 1
        elif roll < (decrease + increase) / total:
            self.demand_quantity -= 1
        else:
            self.reset_demand()

    def progress_demand_deprecated(self, time):
        self.change_progress += TRADE_DEMAND_MODIFY_PER_MINUTE * time
        if self.change_progress > 1.0:
            if self.mineral_demanded == -1:
                self.set_new_mineral_demand()
            else:
                self.modify_mineral_demand()
                if self.demand_quantity <= 0 or self.demand_quantity > TRADE_MAX_DEMAND:
                    self.reset_demand()
            self.change_progress -= 1.0

    def progress_demand(self, time):
        """
        New demand progression function
        Instead resets the demand to a random mineral color, with a higher probability of higher demand with more cities.
        Expected demand:
         - 1 city: 3.8
         - 2 cities: 4.6
         - 3 cities: 5.4
         - 4+ cities: 6.2
        """
        self.change_progress += TRADE_DEMAND_MODIFY_PER_MINUTE * time
        if self.change_progress > 1.0:
            self.set_new_mineral_demand()
            new_demand = 1
            increase_chance = TRADE_DEMAND_BASE_PROB + TRADE_DEMAND_PROB_CITY_BOOST * min(self.colony.cities, 4)
            for i in range(TRADE_MAX_DEMAND - 1):
                if random.random() < increase_chance:
                    new_demand += 1
            self.demand_quantity = new_demand
            self.change_progress -= 1.0

    def get_price(self, mineral, buyer):
        if self.mineral_demanded != -1 and mineral == self.mineral_demanded:
            return (buyer.technology.get_minimum_price() + (TRADE_PRICE_PER_DEMAND + buyer.technology.get_trade_bonus())
                    * self.demand_quantity) * (2 if buyer.technology.has_nanomarketing() else 1)
        return buyer.technology.get_minimum_price()
