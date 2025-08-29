

BIOMASS_TYPES = "A B C D E F G H I J K L M N O P Q R S T U V W X Y Z".split()

MAX_HABITABILITY = 3
BASE_TERRAFORM_COST = 10
TERRAFORM_MONETARY_COST = 1500
BIOMASS_REGENERATION_PER_MINUTE = 1.0  # In fraction of full capacity per minute - recommended 1.0

class Biomass:

    def __init__(self, ship):
        self.ship = ship
        self.quantities = [0 for _ in range(len(BIOMASS_TYPES))]
        self.selected = -1
        self.value = self.get_biological_value()

    def add(self, other):
        for i in range(len(self.quantities)):
            self.quantities[i] += other.quantities[i]
        self.value = self.get_biological_value()

    def select(self, new_selection):
        self.selected = new_selection
        self.value = self.get_biological_value()

    def get_fullness(self):
        return sum(self.quantities) * 20 + len(self.quantities) - self.quantities.count(0)

    def change_quantity(self, species, amount):
        self.quantities[species] += amount
        if self.selected == species and self.quantities[species] <= 0:
            self.selected = -1
        self.value = self.get_biological_value()

    def get_biological_value(self):
        if self.selected != -1:
            self.quantities[self.selected] -= 1
        highest = max(self.quantities)
        total = 0
        for i in range(highest):
            count = 0
            for j in range(len(self.quantities)):
                if self.quantities[j] > i:
                    count += 1
            total += (count * (count + 1)) // 2
        if self.selected != -1:
            self.quantities[self.selected] += 1
        return total

    def empty(self):
        value = self.get_biological_value()
        for i in range(len(self.quantities)):
            self.quantities[i] = 0
        self.value = 0
        self.selected = -1
        return value

class Ecology:
    """
    An object representing the ecology, or lack thereof, on a planet
    Is directly associated to an existing Planet object
    Gives the habitability level of a planet, defining the extent to which colonies can be developed
    Also stores which species are present on the planet
    and the current biomass level on the planet, for the purpose of harvesting
    """
    def __init__(self, planet):
        self.planet = planet
        self.habitability = 0
        self.species = [False for _ in range(len(BIOMASS_TYPES))]
        self.biomass_level = 0.0

    def get_terraform_cost(self):
        """
        Gets the biomass cost to terraform this Ecology to the next habitability tier
        This is in addition to the base cost of "seeding" the planet
        First level: N biomass
        Second level: 3N biomass
        Third level: 6N biomass
        where N is the base terraform cost constant
        """
        return BASE_TERRAFORM_COST * (self.habitability + 1) * (self.habitability + 2) // 2

    def regenerate_biomass(self, time):
        """
        Given an elapsed time, in minutes, find how much total biomass regenerates in this ecology
        Does not let biomass regenerate above 1.0
        """
        if self.habitability > 0:
            self.biomass_level = min(1.0, self.biomass_level + BIOMASS_REGENERATION_PER_MINUTE * time)
