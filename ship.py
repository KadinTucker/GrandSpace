import math

import ecology
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

# Average distance of 80 units between stars and taking 2 seconds to traverse 80 units requires a speed of 2400
SHIP_SPEED_PER_MINUTE = 800
STAR_ENTRY_DISTANCE = 1

# TODO: make these tasks (or above constants) vary with technology
TASKS = [ship_tasks.task_null, ship_tasks.task_explore_superficial]

class Ship:

    def __init__(self, location, ruler):
        self.health = 0
        self.energy = 0
        self.ruler = ruler
        self.star = None  # Star object, or None if travelling interstellar
        self.planet = None  # Planet object, or None if not at a planet
        self.location = location  # tuple
        self.cargo = Cargo(self)  # Cargo object
        self.task = 0
        self.destination = location
        self.destination_star = None
        self.destination_planet = None

    def get_distance_to(self, position):
        x_dist = position[0] - self.location[0]
        y_dist = position[1] - self.location[1]
        return math.hypot(x_dist, y_dist)

    def move(self, time):
        """
        Moves the ship, depending on where the ship currently is
        First, the ship moves between any planets, if applicable (`move_in_system`)
        Then, the ship moves between a system and the galaxy, if applicable (`move_between_system`)
        Lastly, the ship moves in the galaxy (`move_in_galaxy`)
        """
        self.move_in_system()
        self.move_between_system()
        self.move_in_galaxy(time)

    def move_in_galaxy(self, time):
        """
        Causes the ship to move, in the galaxy, toward its destination
        The ship moves the most direct path toward its destination
        The ship does not move if it is at its destination
        """
        x_dist = self.destination[0] - self.location[0]
        y_dist = self.destination[1] - self.location[1]
        distance_to_destination = math.hypot(x_dist, y_dist)
        if distance_to_destination != 0:
            distance_travelled = time * SHIP_SPEED_PER_MINUTE
            if distance_travelled >= distance_to_destination:
                self.location = self.destination
            else:
                self.location = (self.location[0] + x_dist * distance_travelled / distance_to_destination,
                                 self.location[1] + y_dist * distance_travelled / distance_to_destination)

    def move_between_system(self):
        """
        The ship attempts to move between the galaxy and a star system, if it wishes
        Three cases are distinguished:
         - The ship has no star, and is thus in the galaxy. The ship then checks if it has a destination, and then if it
           is close enough to enter its destination star. It enters the star if so
         - The ship has a star, but it is different from its destination (possibly none).
           The ship then exits its current star.
           The ship will orient itself to get to its destination star accordingly via the `orient` method
         - The ship has a star, and it is also the ship's destination. No actions need to be taken
        """
        if self.star is None:
            if self.destination_star is not None:
                distance = math.hypot(self.destination_star.location[0] - self.location[0],
                                      self.destination_star.location[1] - self.location[1])
                if distance <= STAR_ENTRY_DISTANCE:
                    self.enter_star()
        elif self.destination_star is not self.star:
            self.exit_star()

    def move_in_system(self):
        """
        The ship attempts to move between planets within its own system.
         - The ship does not have a planet, but does have a destination planet. The ship then checks
           if it is in the correct star system, and, if so, enters the planet
         - The ship has a planet, but it is different from its destination (possibly none).
           Then the ship exits its current planet.
         - The ship has a planet, and it is also the ship's destination. No actions need to be taken
        """
        if self.planet is None:
            if self.destination_planet is not None:
                if self.star is not None and self.star is self.destination_planet.star:
                    self.enter_planet()
        elif self.destination_planet is not self.planet:
            self.exit_planet()

    def orient(self):
        """
        Orients the ship so that, based on its destinations, it works out the intermediate destinations to get there
        Any planet destinations are the highest priority, then any star destinations, then galaxy destinations
        With a planet destination, the ship sets its star destination to be the planet's star.
        With a star destination, the ship sets its galaxy destination to be the star's location.
        """
        if self.destination_planet is not None:
            self.destination_star = self.destination_planet.star
        if self.destination_star is not None:
            self.destination = self.destination_star.location

    def set_destination_planet(self, planet):
        """
        Sets the destination of the ship to be a planet,
        then orients the ship to get the correct route there through galaxy and stars
        """
        self.destination_planet = planet
        self.orient()

    def set_destination_star(self, star):
        """
        Sets the destination of the ship to be a star with no planet as the destination,
        then orients the ship to get to that star through the galaxy if necessary
        """
        self.destination_star = star
        self.destination_planet = None
        self.orient()

    def set_galaxy_destination(self, destination):
        """
        Sets the destination of the ship to be a point in the galaxy,
        outside any star system, thus making for no planet or star as its destination
        """
        self.destination = destination
        self.destination_star = None
        self.destination_planet = None

    def do_task(self):
        TASKS[self.task](self, self.ruler.game)

    def reset_task(self):
        self.task = 0

    def explore_location(self):
        if self.star is not None:
            self.ruler.explored_stars[self.star.id] = True
        if self.planet is not None:
            if self.planet.artifacts > 0:
                self.cargo.artifacts += 1
                self.planet.artifacts -= 1

    def enter_star(self):
        """
        Causes the ship to enter its destination star
        Registers that the ship is now at the star,
        and adds the ship to that star's register
        For this method to be called, the ship must not have a current star,
        and the ship must have a destination star
        """
        assert self.star is None and self.destination_star is not None, \
            "to enter a star, a ship must both have no current star and have a valid destination star"
        self.star = self.destination_star
        self.star.ships.append(self)
        self.explore_location()

    def exit_star(self):
        """
        Causes the ship to exit its current star
        The star de-registers this ship, and the ship registers that it has no star
        Additionally, this also causes the ship to exit its current planet, if it has one
        For this method to be called, the ship must have a current star
        """
        assert self.star is not None, "to exit a star, ship must have a current star"
        if self.planet is not None:
            self.exit_planet()
        self.star.ships.remove(self)
        self.star = None

    def enter_planet(self):
        """
        Causes the ship to enter its destination planet
        Registers that the ship is now at the planet,
        and adds the ship to the register of that planet
        For this method to be called, the ship must not have a current planet,
        and the ship must have a destination planet
        """
        assert self.planet is None and self.destination_planet is not None, \
            "to enter a planet, ship must both have no current planet and have a valid destination planet"
        self.planet = self.destination_planet
        self.planet.ships.append(self)
        self.explore_location()

    def exit_planet(self):
        """
        Causes the ship to exit its current planet
        The planet de-registers this ship, and the ship registers that it has no planet
        For this method to be called, the ship must have a current planet
        """
        assert self.planet is not None, "to exit a planet, ship must have a current planet"
        self.planet.ships.remove(self)
        self.planet = None

    def collect_biomass(self, ecology_obj):
        if ecology_obj is not None and ecology_obj.biomass_level == 1:
            for i in range(len(ecology_obj.species)):
                if ecology_obj.species[i]:
                    self.cargo.biomass.change_quantity(i, 1)
            ecology_obj.biomass_level = 0


class Cargo:

    def __init__(self, ship):
        self.ship = ship
        self.minerals = [0, 0, 0, 0, 0, 0]
        self.artifacts = 0
        self.biomass = ecology.Biomass(ship)
        self.buildings = 0
    
    def get_fullness(self):
        total = 0
        for c in self.minerals:
            if c > 0:
                total += 20 + c
        total += self.artifacts * 20
        total += self.biomass.get_fullness()
        total += self.buildings
        return total
