import random

TRADE_MAX_DEMAND = 9
TRADE_DEMAND_INCREASE_CHANCE = 0.62
TRADE_DEMAND_DECREASE_CHANCE = 0.32
TRADE_DEMAND_MODIFY_PER_MINUTE_CITY = 1.0  # in changes per minute and city

TRADE_PRICE_PER_DEMAND = 50
TRADE_PRICE_NON_DEMAND = 10

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
        roll = random.random()
        if roll < TRADE_DEMAND_INCREASE_CHANCE:
            self.demand_quantity += 1
        elif roll < TRADE_DEMAND_DECREASE_CHANCE + TRADE_DEMAND_INCREASE_CHANCE:
            self.demand_quantity -= 1
        if (self.demand_quantity < 1 or self.demand_quantity > TRADE_MAX_DEMAND or
                roll >= TRADE_DEMAND_INCREASE_CHANCE + TRADE_DEMAND_DECREASE_CHANCE):
            self.reset_demand()

    def progress_demand(self, time):
        self.change_progress += TRADE_DEMAND_MODIFY_PER_MINUTE_CITY * self.colony.cities * time
        if self.change_progress > 1.0:
            if self.mineral_demanded == -1:
                self.set_new_mineral_demand()
            else:
                self.modify_mineral_demand()
            self.change_progress -= 1.0

    def get_price(self, mineral):
        if mineral == self.mineral_demanded:
            return TRADE_PRICE_PER_DEMAND * self.demand_quantity
        return TRADE_PRICE_NON_DEMAND
