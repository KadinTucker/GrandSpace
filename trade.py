import random

TRADE_MAX_DEMAND = 5
TRADE_DEMAND_INCREASE_CHANCE = 6
TRADE_DEMAND_DECREASE_CHANCE = 3
TRADE_DEMAND_RESET_CHANCE = 1
TRADE_DEMAND_CITY_BOOST = 2
TRADE_DEMAND_MODIFY_PER_MINUTE = 2.0  # in changes per minute

TRADE_PRICE_PER_DEMAND = 100

class Demand:

    def __init__(self, colony):
        self.colony = colony
        self.possible_demands = [i for i in range(6)]
        self.possible_demands.remove(self.colony.planet.mineral)
        self.change_progress = 0.0
        self.mineral_demanded = -1
        self.demand_quantity = 0

    def reset_demand(self):
        self.possible_demands.append(self.mineral_demanded)
        self.mineral_demanded = -1
        self.demand_quantity = 0

    def set_new_mineral_demand(self):
        new_demand = random.choice(self.possible_demands)
        self.possible_demands.remove(new_demand)
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
         -      1              60%              30%             10%
         -      2              67%              25%             8%          * values are rounded
         -      3              71%              21%             7%
         -      4              75%              19%             6%
         -      5              78%              17%             6%          * values are rounded
         -      6              80%              15%             5%          * values are rounded
         -      7              82%              13%             5%          * values are rounded
        """
        roll = random.random() * (TRADE_DEMAND_CITY_BOOST * (self.colony.cities - 1) + TRADE_DEMAND_INCREASE_CHANCE
                                  + TRADE_DEMAND_RESET_CHANCE)
        if roll < TRADE_DEMAND_CITY_BOOST * (self.colony.cities - 1):
            self.demand_quantity += 1
        elif roll < TRADE_DEMAND_DECREASE_CHANCE + TRADE_DEMAND_INCREASE_CHANCE * self.colony.cities:
            self.demand_quantity -= 1
        else:
            self.reset_demand()

    def progress_demand(self, time):
        self.change_progress += TRADE_DEMAND_MODIFY_PER_MINUTE * time
        if self.change_progress > 1.0:
            if self.mineral_demanded == -1:
                self.set_new_mineral_demand()
            else:
                self.modify_mineral_demand()
                if self.demand_quantity <= 0 or self.demand_quantity > TRADE_MAX_DEMAND:
                    self.reset_demand()
            self.change_progress -= 1.0

    def get_price(self, mineral, buyer):
        if self.mineral_demanded != -1 and mineral == self.mineral_demanded:
            return (buyer.technology.get_minimum_price() + (TRADE_PRICE_PER_DEMAND + buyer.technology.get_trade_bonus())
                    * self.demand_quantity)
        return buyer.technology.get_minimum_price() + buyer.technology.get_trade_bonus()
