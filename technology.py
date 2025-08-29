

CATEGORY_NAMES = "Empire Combat Discovery Ecology Diplomacy Commerce".split()
DOMAINS = [0, 0, 1, 2, 2, 1]
DOMAIN_NAMES = "Power Prosperity Harmony".split()

MAIN_TREE_NAMES = [
    "Construction Security".split(),
    "Warfare Shipbuilding".split(),
    "Spacefaring Research".split(),
    "Geoengineering Astrobiology".split(),
    "Charisma Neuropsychology".split(),
    "Economics Communication".split(),
]
WILDCARD_NAMES = [
    "Orbital Defence,Singularity Storage,".split(","),
    "The Forcefield,Darkmatter Weapons,".split(","),
    "Quantum Computer,Faster Than Light,".split(","),
    "Genetic Programming,Mass Cloning,".split(","),
    "Intergalactic Ambassadors,Galactic Harmony,".split(","),
    "Nanotargeted Marketing,Hypercommerce".split(","),
]
ROMAN_NUMERALS = "I II III IV V".split()

MAIN_TECH_COSTS = [20, 30, 50, 80, 120]
WILDCARD_TECH_COSTS = [100, 150]

BASE_BUILDING_COST = 500
CONSTRUCTION_EFFECT = 50

TURRET_FIRERATE_PER_TIER = 10.0

SHIP_BASE_FIRERATE = 20.0
SHIP_BONUS_FIRERATE = 10.0

SHIP_BASE_HEALTH = 10
SHIP_BONUS_HEALTH = 5

SHIP_BONUS_SPEED_SHIPBUILDING = 150
SHIP_BASE_STAR_CHANGE = 60.0
SHIP_BONUS_STAR_CHANGE = 30.0
SHIP_BASE_PLANET_CHANGE = 120.0
SHIP_BONUS_PLANET_CHANGE = 60.0

SHIP_BASE_SPEED = 800
SHIP_BONUS_SPEED_SPACEFARING = 400

SHIP_BASE_RANGE = 90
SHIP_BONUS_RANGE = 30

SCIENCE_ARTIFACT_BASE = 2
SCIENCE_ARTIFACT_BONUS = 2

SCIENCE_MISSION_BASE = 1
SCIENCE_MISSION_BONUS = 1

TRADE_BONUS = 10

VISION_RANGE_BASE = 50
VISION_RANGE_BONUS = 25

CHARISMA_FRACTION = 0.05  # how much of spent leverage is refunded per level of charisma

SCHMOOZE_POWER = 5.0  # in leverage points per minute

BASE_RESEARCH_LEVERAGE = 2
RESEARCH_LEVERAGE_BOOST = 1

TERRAFORM_MONEY_COST_BASE = 1500
TERRAFORM_MONEY_COST_BONUS = 300

BIOMASS_COLLECTION_RATE_BASE = 5.0
BIOMASS_COLLECTION_RATE_BONUS = 1.5
BIOMASS_REFUND = 0.1

ORBITAL_SHIELD_BONUS = 1

MINERAL_STORAGE_BASE = 5
MINERAL_STORAGE_BONUS = 5
MAX_DEVELOPMENT_PER_CITY_BONUS = 1

BASE_SCIENCE_RATE = 4
IMPROVED_SCIENCE_RATE = 2

BASE_MINIMUM_PRICE = 50
IMPROVED_MINIMUM_PRICE = 100

class TechnologyTree:
    """
    A player's personal technological progress
    It is from here that the Player's attributes are retrieved
    """
    def __init__(self, player):
        # TODO: fix tech references after the reindexing!
        self.player = player
        # tech level, indexed first by category, next by tech type: first, second, wildcard
        self.tech_level = [[0, 0, 0] for _ in range(6)]
        # science available: power, prosperity, harmony, neutral
        self.science = [0, 0, 0, 0]

    def has_prerequisites(self, category, tech_type, level):
        if tech_type == 2:
            if level == 1:
                return self.tech_level[category][0] >= 2 or self.tech_level[category][1] >= 2
            elif level == 2:
                return (self.tech_level[category][2] == 1
                        and (self.tech_level[category][0] >= 4 or self.tech_level[category][1] >= 4))
        else:
            return self.tech_level[category][tech_type] == level - 1
        return False

    def has_science(self, category, tech_type, level):
        cost = MAIN_TECH_COSTS[level - 1]
        if tech_type == 2:
            cost = WILDCARD_TECH_COSTS[level + 2]
        total_science = self.science[3] + self.science[DOMAINS[category]]
        return total_science >= cost

    def try_research(self, category, tech_type, level):
        if self.has_prerequisites(category, tech_type, level):
            if self.has_science(category, tech_type, level):
                cost = MAIN_TECH_COSTS[level - 1]
                if tech_type == 2:
                    cost = MAIN_TECH_COSTS[level + 2]
                    name = WILDCARD_NAMES[category][level]
                else:
                    name = MAIN_TREE_NAMES[category][tech_type] + " " + ROMAN_NUMERALS[level - 1]
                domain_science_used = min(cost, self.science[DOMAINS[category]])
                neutral_science_used = cost - domain_science_used
                self.tech_level[category][tech_type] = level
                self.science[DOMAINS[category]] -= domain_science_used
                self.science[3] -= neutral_science_used
                self.player.milestone_progress[1] += cost
                self.player.visibility.reset_permanent_visibility()
                self.player.log_message(f"Researched {name} for {domain_science_used} {DOMAIN_NAMES[DOMAINS[category]]}"
                                        f" and {neutral_science_used} Neutral science.")

    def get_building_cost(self):
        return BASE_BUILDING_COST - CONSTRUCTION_EFFECT * self.tech_level[0][0]

    def get_turret_firerate(self):
        return TURRET_FIRERATE_PER_TIER * self.tech_level[0][1]

    def get_ship_firerate(self):
        return SHIP_BASE_FIRERATE + SHIP_BONUS_FIRERATE * self.tech_level[1][0]

    def get_ship_max_health(self):
        return SHIP_BASE_HEALTH + SHIP_BONUS_HEALTH * self.tech_level[1][1]

    def get_ship_star_change_rate(self):
        return SHIP_BASE_STAR_CHANGE + SHIP_BONUS_STAR_CHANGE * self.tech_level[1][1]

    def get_ship_planet_change_rate(self):
        return SHIP_BASE_PLANET_CHANGE + SHIP_BONUS_PLANET_CHANGE * self.tech_level[1][1]

    def get_ship_speed(self):
        return (SHIP_BASE_SPEED + SHIP_BONUS_SPEED_SPACEFARING * self.tech_level[2][0] + SHIP_BONUS_SPEED_SHIPBUILDING
                * self.tech_level[1][1])

    def get_ship_range(self):
        return SHIP_BASE_RANGE + SHIP_BONUS_RANGE * self.tech_level[2][0]

    def get_artifact_science(self):
        return SCIENCE_ARTIFACT_BASE + SCIENCE_ARTIFACT_BONUS * self.tech_level[2][1]

    def get_mission_science(self):
        return SCIENCE_MISSION_BASE + SCIENCE_MISSION_BONUS * self.tech_level[2][1]

    def get_trade_bonus(self):
        return TRADE_BONUS * self.tech_level[5][0]

    def get_visibility_range(self):
        return VISION_RANGE_BASE + VISION_RANGE_BONUS * self.tech_level[5][1]

    def get_leverage_refund(self):
        return CHARISMA_FRACTION * self.tech_level[4][0]

    def get_schmooze_power(self):
        return SCHMOOZE_POWER * self.tech_level[4][1]

    def get_research_leverage(self):
        return BASE_RESEARCH_LEVERAGE + RESEARCH_LEVERAGE_BOOST * self.tech_level[4][1]

    def get_terraform_monetary_cost(self):
        return TERRAFORM_MONEY_COST_BASE - TERRAFORM_MONEY_COST_BONUS * self.tech_level[3][0]

    def get_biomass_collection_rate(self):
        return BIOMASS_COLLECTION_RATE_BASE * BIOMASS_COLLECTION_RATE_BONUS ** self.tech_level[3][1]

    def get_biomass_refund(self):
        return BIOMASS_REFUND * self.tech_level[3][1]

    def get_bonus_shields(self):
        if self.tech_level[0][2] >= 1:
            return ORBITAL_SHIELD_BONUS
        return 0

    def get_mineral_storage(self):
        if self.tech_level[0][2] >= 2:
            return MINERAL_STORAGE_BASE + MINERAL_STORAGE_BONUS
        return MINERAL_STORAGE_BASE

    def get_bonus_development_per_city(self):
        if self.tech_level[0][2] >= 2:
            return MAX_DEVELOPMENT_PER_CITY_BONUS
        return 0

    def has_forcefields(self):
        return self.tech_level[1][2] >= 1

    def has_dark_matter(self):
        return self.tech_level[1][2] >= 2

    def get_science_trade_rate(self):
        if self.tech_level[2][2] >= 1:
            return IMPROVED_SCIENCE_RATE
        return BASE_SCIENCE_RATE

    def has_lightspeed(self):
        return self.tech_level[2][2] >= 2

    def get_minimum_price(self):
        if self.tech_level[5][2] >= 1:
            return IMPROVED_MINIMUM_PRICE
        return BASE_MINIMUM_PRICE

    def has_hypercommerce(self):
        return self.tech_level[5][2] >= 2

    def has_embassy(self):
        return self.tech_level[4][2] >= 1

    def has_harmony(self):
        return self.tech_level[4][2] >= 2

    def has_genetics(self):
        return self.tech_level[3][2] >= 1

    def has_cloning(self):
        return self.tech_level[3][2] >= 2
