import math

import ship_tasks

"""
Ship tasks:
 - Trade
   - Pick-up, Drop-off
   - Cargo (Minerals)
   - Destination
 - Warfare
   - Attack, Defend
   - Destination
 - Colonize
   - Establish, Manage
   - Funds/Cargo
   - Destination
 - Explore
   - Destination
 - Terraform
   - Collect Biomass, Terraform
   - Destination
   - Biomass
   - Atmospheric Tools
 - Diplomat
   - Destination
 - Research
   - Destination
"""

"""
Task Enumeration:
0 - Idle
1 - Trade
2 - Attack
3 - Defend
4 - Establish Colony
5 - Explore
6 - Collect Biomass
7 - Terraform
8 - Conduct Diplomacy
9 - Research
"""

# Assuming average distance of 80 units between stars and it taking 2 seconds to traverse 80 units
SHIP_SPEED_PER_MINUTE = 2400 
STAR_ENTRY_DISTANCE = 10

# TODO: make these tasks (or above constants) vary with technology
TASKS = [ship_tasks.task_null, ship_tasks.task_explore_superficial]

class Ship():

    def __init__(self, location, ruler):
        self.health = 0
        self.energy = 0
        self.ruler = ruler
        self.star = None # Star object, or None if travelling interstellar
        self.planet = None # Planet object, or None if not at a planet
        self.location = location # tuple
        self.cargo = Cargo() # Cargo object
        self.task = 0
        self.destination = location
        self.destination_star = None
        self.destination_planet = None

    def move(self, time):
        x_dist = self.destination[0] - self.location[0]
        y_dist = self.destination[1] - self.location[1]
        distance_to_destination = math.hypot(x_dist, y_dist)
        moved = False
        if distance_to_destination != 0:
            distance_travelled = min(time * SHIP_SPEED_PER_MINUTE, distance_to_destination)
            self.location = (self.location[0] + x_dist * distance_travelled / distance_to_destination, 
                            self.location[1] + y_dist * distance_travelled / distance_to_destination)
            moved = True
        entered_s = False
        if self.destination_star != None:
            entered_s = self.try_enter_star()
        entered_p = False
        if self.destination_planet != None:
            entered_p = self.try_enter_planet()
        return moved, entered_s or entered_p
    
    def set_destination_star(self, star):
        self.destination_star = star
        self.destination = star.location
        self.exit_star()

    def set_destination_planet(self, planet):
        self.destination_planet = planet
        self.destination_star = planet.star
        self.destination = planet.star.location
        self.exit_planet()

    def do_task(self):
        TASKS[self.task](self, self.ruler.game)

    def try_enter_star(self):
        if self.destination_star != None:
            distance = math.hypot(self.destination_star.location[0] - self.location[0], self.destination_star.location[1] - self.location[1])
            if distance <= STAR_ENTRY_DISTANCE:
                self.enter_star()
                return True
        return False

    def try_enter_planet(self):
        if self.star != None and self.destination_planet in self.star.planets:
            self.enter_planet()
            return True
        return False

    def enter_star(self):
        if self.destination_star != None:
            self.exit_star()
            self.star = self.destination_star
            self.star.ships.append(self)
            self.destination_star = None
            self.ruler.explored_stars[self.star.id] = True

    def exit_star(self):
        if self.star != None:
            self.exit_planet()
            self.star.ships.remove(self)
            self.star = None

    def enter_planet(self):
        if self.destination_planet != None:
            self.exit_planet()
            self.planet = self.destination_planet
            self.planet.ships.append(self)
            self.destination_planet = None

            if self.planet.artifacts > 0:
                self.planet.artifacts -= 1
                self.cargo.artifacts += 1

    def exit_planet(self):
        if self.planet != None:
            self.planet.ships.remove(self)
            self.planet = None


class Cargo():

    def __init__(self):
        self.minerals = [0, 0, 0, 0, 0, 0]
        self.artifacts = 0
        self.biomass = {} # keys: origins; values: biomass total
        self.buildings = 0
    
    def get_fullness(self):
        total = 0
        for c in self.minerals:
            if c > 0:
                total += 20 + c
        total += self.artifacts * 20
        for b in self.biomass:
            if self.biomass[b] > 0:
                total += 20 + self.biomass[b]
        total += self.buildings
        return total