import pygame

# Action Indices
# See ship_tasks.py for a list of the actions

ACTION_ZERO = 0
ACTION_ONE = 1
ACTION_BUILD_CITY = 2
ACTION_DEVELOP = 3
ACTION_COLONISE = 4
ACTION_COLLECT_BIOMASS = 5
ACTION_TERRAFORM = 6
ACTION_COLLECT = 7
ACTION_SELL_RED = 8
ACTION_SELL_GREEN = 9
ACTION_SELL_BLUE = 10
ACTION_SELL_CYAN = 11
ACTION_SELL_MAGENTA = 12
ACTION_SELL_YELLOW = 13
ACTION_SELL_ARTIFACT = 14
ACTION_BUY_BUILDING = 15
ACTION_BIOLOGY = 16
ACTION_FUND_SCIENCE = 17

# Key Controls
ACTION_KEYCONTROL_DICT = {
    pygame.K_y: ACTION_BUILD_CITY,
    pygame.K_d: ACTION_DEVELOP,
    pygame.K_c: ACTION_COLONISE,
    pygame.K_b: ACTION_COLLECT_BIOMASS,
    pygame.K_t: ACTION_TERRAFORM,
    pygame.K_m: ACTION_COLLECT,
    pygame.K_l: ACTION_BUY_BUILDING,
    pygame.K_a: ACTION_SELL_ARTIFACT,
    pygame.K_1: ACTION_SELL_RED,
    pygame.K_2: ACTION_SELL_GREEN,
    pygame.K_3: ACTION_SELL_BLUE,
    pygame.K_4: ACTION_SELL_CYAN,
    pygame.K_5: ACTION_SELL_MAGENTA,
    pygame.K_6: ACTION_SELL_YELLOW
}

# Game icons

ICONS = {
    "milestone_frame": pygame.image.load("assets/milestone-frame.png"),
    "mineral_r": pygame.image.load("assets/minerals-red.png"),
    "mineral_g": pygame.image.load("assets/minerals-green.png"),
    "mineral_b": pygame.image.load("assets/minerals-blue.png"),
    "mineral_c" : pygame.image.load("assets/minerals-cyan.png"),
    "mineral_m": pygame.image.load("assets/minerals-magenta.png"),
    "mineral_y" : pygame.image.load("assets/minerals-yellow.png"),
    "sell_mineral_r": pygame.image.load("assets/icon-sell-red.png"),
    "sell_mineral_g": pygame.image.load("assets/icon-sell-green.png"),
    "sell_mineral_b": pygame.image.load("assets/icon-sell-blue.png"),
    "sell_mineral_c": pygame.image.load("assets/icon-sell-cyan.png"),
    "sell_mineral_m": pygame.image.load("assets/icon-sell-magenta.png"),
    "sell_mineral_y": pygame.image.load("assets/icon-sell-yellow.png"),
    "diplomacy": pygame.image.load("assets/icon-diplomacy.png"),
    "empire": pygame.image.load("assets/icon-colonial.png"),
    "discovery": pygame.image.load("assets/icon-explore.png"),
    "trade": pygame.image.load("assets/icon-trade.png"),
    "battle": pygame.image.load("assets/icon-battle.png"),
    "ecology": pygame.image.load("assets/icon-ecology.png"),
    "science": pygame.image.load("assets/icon-research-gold.png"),
    "science_red": pygame.image.load("assets/icon-research-red.png"),
    "science_green": pygame.image.load("assets/icon-research-green.png"),
    "science_blue": pygame.image.load("assets/icon-research-blue.png"),
    "sell_artifact": pygame.image.load("assets/icon-sell-artifact.png"),
    "build_city": pygame.image.load("assets/icon-build-city.png"),
    "develop": pygame.image.load("assets/icon-build-development.png"),
    "colonise": pygame.image.load("assets/icon-colonial.png"),
    "collect_biomass": pygame.image.load("assets/icon-collect-biomass.png"),
    "terraform": pygame.image.load("assets/icon-terraform.png"),
    "collect_minerals": pygame.image.load("assets/icon-collect.png"),
    "buy_building": pygame.image.load("assets/icon-buy-building.png"),
    "biology": pygame.image.load("assets/icon-biology.png"),
    "fund_science": pygame.image.load("assets/icon-fund-science.png"),
}

