import math
import pygame

import drawable
import ecology

import font
import snapshot
import system_display
import trade
import uiframe

SYSTEM_PLANET_RADIUS = 20
TEXT_WIDTH = 12
TEXT_HEIGHT = 16

MINERAL_WIDTH = 20
MINERAL_HEIGHT = 20
MINERAL_FILENAMES = ["assets/minerals-red.png", "assets/minerals-green.png", "assets/minerals-blue.png",
                     "assets/minerals-cyan.png", "assets/minerals-magenta.png", "assets/minerals-yellow.png",
                     "assets/minerals-blank.png"]
MINERAL_IMAGES = [pygame.image.load(fn) for fn in MINERAL_FILENAMES]

SYSTEM_COLONY_RADIUS = 30
SYSTEM_ARTIFACT_RING_WIDTH = 2
COLOR_ARTIFACT_RING = (150, 125, 35)
MINERAL_COLORS = [(200, 20, 20), (20, 200, 20), (20, 20, 200), (200, 200, 20), (200, 20, 200), (20, 200, 200)]

PLANET_RING_OFFSET = -4
INDICATOR_HABITAT_IMG = pygame.image.load("assets/indicator-habitat-new.png")
INDICATOR_CITY_IMG = pygame.image.load("assets/indicator-city-new.png")
INDICATOR_DEVELOPMENT_IMG = pygame.image.load("assets/indicator-development-new.png")

ECOLOGY_SPECIES_WIDTH = 12
ECOLOGY_SPECIES_HEIGHT = 16
ECOLOGY_BIOMASS_SPACING = 6
ECOLOGY_BIOMASS_HEIGHT = 10
ECOLOGY_BIOMASS_WIDTH = 30
ECOLOGY_BIOMASS_HALO_WIDTH = 2
ECOLOGY_SPECIES_FILENAMES = ["assets/typeface/eco-serif/" + letter + ".png" for letter in ecology.BIOMASS_TYPES]
ECOLOGY_SPECIES_IMAGES = [pygame.image.load(fn) for fn in ECOLOGY_SPECIES_FILENAMES]
COLOR_BIOMASS_EMPTY = (95, 35, 15)
COLOR_BIOMASS_FULL = (25, 110, 15)
COLOR_BIOMASS_HALO = (110, 220, 110)

COLONY_MARGIN = 20
COLONY_ICON_WIDTH = 26
COLONY_ICON_HEIGHT = 26
COLONY_SUMMARY_SPACING = 8
COLONY_VERTICAL_SPACING = 8
COLONY_DEMAND_PROGRESS_WIDTH = 3
COLONY_DEMAND_PROGRESS_HEIGHT = 16
COLONY_CITY_ICON_IMG = uiframe.create_button("assets/icon-city.png")
COLONY_DEVELOPMENT_ICON_IMG = uiframe.create_button("assets/icon-development.png")
COLOR_DEMAND_PROGRESS = (180, 180, 180)

PRODUCTION_SPACING = 8
PRODUCTION_TIME_IMG = font.get_text_surface("/min")

DEFENSE_ICON_HEIGHT = 24
DEFENSE_ICON_WIDTH = 24
DEFENSE_STACK_WIDTH = 4
DEFENSE_STACK_HEIGHT = 2
DEFENSE_ICON_IMG = pygame.image.load("assets/defense-slot.png")

def get_ring_distribution_coordinates(center, radius, num_items):
    coordinates = [[0, 0] for _ in range(num_items)]
    num_rings = math.ceil(math.sqrt(num_items))
    current_item = 0
    for i in range(num_rings - 1):
        ring_plots = 2 * i + 1
        for j in range(ring_plots):
            coordinates[current_item][0] = int(center[0] + radius * math.cos(2 * math.pi * j / ring_plots)
                                               * i / num_rings)
            coordinates[current_item][1] = int(center[1] + radius * math.sin(2 * math.pi * j / ring_plots)
                                               * i / num_rings)
            current_item += 1
    remaining_items = num_items - current_item
    for i in range(remaining_items):
        coordinates[current_item][0] = int(center[0] + radius * math.cos(2 * math.pi * i / remaining_items)
                                           * (num_rings - 1) / num_rings)
        coordinates[current_item][1] = int(center[1] + radius * math.sin(2 * math.pi * i / remaining_items)
                                           * (num_rings - 1) / num_rings)
        current_item += 1
    return coordinates


def get_linear_stack_positions(start_boundary, end_boundary, num_items):
    return [start_boundary + ((i + 1) / (num_items + 1) * (end_boundary - start_boundary)) for i in range(num_items)]


class PlanetSnapshot(snapshot.Snapshot):

    def __init__(self, game, planet):
        self.planet = planet
        super().__init__(game, (3 * SYSTEM_PLANET_RADIUS, 3 * SYSTEM_PLANET_RADIUS),
                         system_display.COLOR_BACKGROUND)

    def update(self):
        super().update()
        # Draw artifact background
        if self.planet.artifacts > 0:
            pygame.draw.circle(self.surface, COLOR_ARTIFACT_RING, (self.dimensions[0] // 2, self.dimensions[1] // 2),
                               SYSTEM_PLANET_RADIUS + SYSTEM_ARTIFACT_RING_WIDTH * 2, SYSTEM_ARTIFACT_RING_WIDTH)
            pygame.draw.circle(self.surface, COLOR_ARTIFACT_RING, (self.dimensions[0] // 2, self.dimensions[1] // 2),
                               SYSTEM_PLANET_RADIUS + SYSTEM_ARTIFACT_RING_WIDTH * 4, SYSTEM_ARTIFACT_RING_WIDTH)
        # Draw cities, development pips, then trees, in a spiral fashion
        num_cities = 0
        num_development = 0
        if self.planet.colony is not None:
            num_cities = self.planet.colony.cities
            num_development = self.planet.colony.development
        num_habit = self.planet.ecology.habitability ** 2
        pip_locations = get_ring_distribution_coordinates((self.dimensions[0] // 2 + PLANET_RING_OFFSET,
                                                          self.dimensions[1] // 2 + PLANET_RING_OFFSET),
                                                          SYSTEM_PLANET_RADIUS, num_cities + num_development
                                                          + num_habit)
        for i in range(len(pip_locations)):
            if i < num_cities:
                self.surface.blit(INDICATOR_CITY_IMG, pip_locations[i])
            elif i < num_cities + num_development:
                self.surface.blit(INDICATOR_DEVELOPMENT_IMG, pip_locations[i])
            else:
                self.surface.blit(INDICATOR_HABITAT_IMG, pip_locations[i])


class EcologySnapshot(snapshot.Snapshot):
    def __init__(self, game, planet):
        self.planet = planet
        self.ecology = planet.ecology
        super().__init__(game, (max(5 * ECOLOGY_SPECIES_WIDTH, ECOLOGY_BIOMASS_WIDTH
                                    + ECOLOGY_BIOMASS_HALO_WIDTH * 2), ECOLOGY_SPECIES_HEIGHT
                                + 2 * ECOLOGY_BIOMASS_SPACING * 2 + ECOLOGY_BIOMASS_HEIGHT
                                + ECOLOGY_BIOMASS_HALO_WIDTH * 2), system_display.COLOR_BACKGROUND)

    def update(self):
        super().update()
        self.ecology = self.planet.ecology
        if self.ecology.habitability == 0:
            return
        if self.ecology.biomass_level == 1:
            pygame.draw.rect(self.surface, COLOR_BIOMASS_HALO,
                             pygame.Rect((self.dimensions[0] - ECOLOGY_BIOMASS_WIDTH - ECOLOGY_BIOMASS_HALO_WIDTH)
                                         // 2, ECOLOGY_SPECIES_HEIGHT + ECOLOGY_BIOMASS_SPACING
                                         - ECOLOGY_BIOMASS_HALO_WIDTH,
                                         ECOLOGY_BIOMASS_WIDTH + ECOLOGY_BIOMASS_HALO_WIDTH * 2,
                                         ECOLOGY_BIOMASS_HEIGHT + ECOLOGY_BIOMASS_HALO_WIDTH * 2))
        else:
            pygame.draw.rect(self.surface, COLOR_BIOMASS_EMPTY,
                             pygame.Rect((self.dimensions[0] - ECOLOGY_BIOMASS_WIDTH) // 2, ECOLOGY_SPECIES_HEIGHT
                                         + ECOLOGY_BIOMASS_SPACING, ECOLOGY_BIOMASS_WIDTH, ECOLOGY_BIOMASS_HEIGHT))
        pygame.draw.rect(self.surface, COLOR_BIOMASS_FULL,
                         pygame.Rect((self.dimensions[0] - ECOLOGY_BIOMASS_WIDTH) // 2, ECOLOGY_SPECIES_HEIGHT
                                     + ECOLOGY_BIOMASS_SPACING,
                                     int(self.ecology.biomass_level * ECOLOGY_BIOMASS_WIDTH),
                                     ECOLOGY_BIOMASS_HEIGHT))
        # Species Icons
        species = []
        for j in range(len(self.ecology.species)):
            if self.ecology.species[j]:
                species.append(j)
        stack_coordinates = get_linear_stack_positions(0, self.dimensions[0] - ECOLOGY_SPECIES_WIDTH,
                                                       len(species))
        for s in range(len(species)):
            self.surface.blit(ECOLOGY_SPECIES_IMAGES[species[s]], (stack_coordinates[s], 0))


class ColonySnapshot(snapshot.Snapshot):
    def __init__(self, game, planet):
        self.planet = planet
        self.colony = planet.colony
        super().__init__(game, (COLONY_MARGIN + max(MINERAL_WIDTH + 6 * TEXT_WIDTH
                                                    + COLONY_DEMAND_PROGRESS_WIDTH, 2 * COLONY_ICON_WIDTH
                                                    + COLONY_SUMMARY_SPACING + TEXT_WIDTH),
                                COLONY_ICON_HEIGHT + TEXT_HEIGHT + COLONY_VERTICAL_SPACING
                                + max(MINERAL_HEIGHT, TEXT_HEIGHT)),
                         system_display.COLOR_BACKGROUND)

    def update(self):
        super().update()
        self.colony = self.planet.colony
        # Summary
        if self.colony is None:
            return
        self.surface.blit(COLONY_CITY_ICON_IMG, (COLONY_MARGIN, 0))
        self.surface.blit(COLONY_DEVELOPMENT_ICON_IMG, (COLONY_MARGIN + COLONY_ICON_WIDTH + COLONY_SUMMARY_SPACING, 0))
        city_img = font.get_text_surface(str(int(self.colony.cities)))
        self.surface.blit(city_img, (COLONY_MARGIN + (COLONY_ICON_WIDTH - TEXT_WIDTH) // 2, COLONY_ICON_HEIGHT))
        development_img = font.get_text_surface(str(int(self.colony.development)) + "/"
                                                + str(int(self.colony.get_maximum_development())))
        self.surface.blit(development_img, (COLONY_MARGIN + COLONY_ICON_WIDTH + COLONY_SUMMARY_SPACING
                                            + (COLONY_ICON_WIDTH - 3 * TEXT_WIDTH) // 2, COLONY_ICON_HEIGHT))
        # Demand
        self.surface.blit(MINERAL_IMAGES[self.colony.demand.mineral_demanded],
                          (COLONY_MARGIN, COLONY_ICON_HEIGHT + TEXT_HEIGHT + COLONY_VERTICAL_SPACING))
        demand_str = " : " + str(max(self.colony.demand.demand_quantity * trade.TRADE_PRICE_PER_DEMAND,
                                     trade.TRADE_PRICE_NON_DEMAND))
        demand_img = font.get_text_surface(demand_str)
        self.surface.blit(demand_img, (COLONY_MARGIN + MINERAL_WIDTH,
                                       COLONY_ICON_HEIGHT + TEXT_HEIGHT + COLONY_VERTICAL_SPACING))
        progress_height = int(self.colony.demand.change_progress * COLONY_DEMAND_PROGRESS_HEIGHT)
        pygame.draw.rect(self.surface, COLOR_DEMAND_PROGRESS,
                         pygame.Rect(COLONY_MARGIN + MINERAL_WIDTH + len(demand_str) * TEXT_WIDTH,
                                     COLONY_ICON_HEIGHT + 2 * TEXT_HEIGHT + COLONY_VERTICAL_SPACING - progress_height,
                                     COLONY_DEMAND_PROGRESS_WIDTH, progress_height))


class ProductionSnapshot(snapshot.Snapshot):

    def __init__(self, game, planet):
        self.planet = planet
        self.colony = planet.colony
        super().__init__(game, (TEXT_WIDTH * 7 + MINERAL_WIDTH, MINERAL_HEIGHT + TEXT_HEIGHT
                                + PRODUCTION_SPACING), system_display.COLOR_BACKGROUND)

    def update(self):
        super().update()
        self.colony = self.planet.colony
        if self.colony is None:
            return
        # Production
        production_str = "+" + str(int(self.colony.get_production(1)))
        production_img = font.get_text_surface(production_str)
        self.surface.blit(production_img, (0, (MINERAL_HEIGHT - TEXT_HEIGHT) // 2))
        self.surface.blit(MINERAL_IMAGES[self.colony.planet.mineral], (TEXT_HEIGHT * len(production_str), 0))
        self.surface.blit(PRODUCTION_TIME_IMG, (TEXT_HEIGHT * len(production_str) + MINERAL_WIDTH,
                                                (MINERAL_HEIGHT - TEXT_HEIGHT) // 2))
        # Storage
        storage_str = str(int(self.colony.minerals)) + "/" + str(int(self.colony.get_mineral_capacity()))
        storage_img = font.get_text_surface(storage_str)
        self.surface.blit(storage_img, ((self.dimensions[0] - len(storage_str) * TEXT_WIDTH) // 2,
                                        MINERAL_HEIGHT + PRODUCTION_SPACING))


class DefenseSnapshot(snapshot.Snapshot):

    def __init__(self, game, planet):
        self.planet = planet
        self.colony = planet.colony
        super().__init__(game, (DEFENSE_STACK_WIDTH * (DEFENSE_ICON_WIDTH - 1),
                                DEFENSE_STACK_HEIGHT * DEFENSE_ICON_HEIGHT), system_display.COLOR_BACKGROUND)

    def update(self):
        super().update()
        self.colony = self.planet.colony
        if self.colony is None:
            return
        defense = self.colony.get_defense()
        for i in range(defense // DEFENSE_STACK_WIDTH + 1):
            locations = get_linear_stack_positions(-DEFENSE_ICON_WIDTH, self.dimensions[0],
                                                   min(DEFENSE_STACK_WIDTH, defense - i * DEFENSE_STACK_WIDTH))
            for location in locations:
                pygame.draw.rect(self.surface, self.colony.ruler.color,
                                 pygame.Rect(location, i * (DEFENSE_ICON_HEIGHT - 1),
                                             DEFENSE_ICON_WIDTH, DEFENSE_ICON_HEIGHT))
                self.surface.blit(DEFENSE_ICON_IMG, (location, i * (DEFENSE_ICON_HEIGHT - 1)))


class PlanetDisplay(drawable.Drawable):

    def __init__(self, game, player, planet):
        super().__init__(game, planet)
        self.game = game
        self.player = player
        self.planet = planet
        self.center_surface = PlanetSnapshot(game, planet)
        self.above_surface = EcologySnapshot(game, planet)
        self.right_surface = ColonySnapshot(game, planet)
        self.below_surface = DefenseSnapshot(game, planet)
        self.left_surface = ProductionSnapshot(game, planet)
        self.update()

    def update_center(self):
        self.center_surface.update()

    def update_above(self):
        self.above_surface.update()

    def update_right(self):
        self.right_surface.update()

    def update_below(self):
        self.below_surface.update()

    def update_left(self):
        self.left_surface.update()

    def draw(self, dest_surface, position):
        drawable.draw_centered(dest_surface, self.center_surface, position)
        self.above_surface.draw(dest_surface, (position[0] - self.above_surface.dimensions[0] // 2,
                                               position[1] - self.center_surface.dimensions[1] // 2
                                               - self.above_surface.dimensions[1]))
        self.right_surface.draw(dest_surface, (position[0] + self.center_surface.dimensions[0] // 2,
                                               position[1] - self.right_surface.dimensions[1] // 2))
        self.below_surface.draw(dest_surface, (position[0] - self.below_surface.dimensions[0] // 2,
                                               position[1] + self.center_surface.dimensions[1] // 2))
        self.left_surface.draw(dest_surface, (position[0] - self.left_surface.dimensions[0]
                                              - self.center_surface.dimensions[0] // 2,
                                              position[1] - self.left_surface.dimensions[1] // 2))

    def update(self):
        self.update_center()
        self.update_above()
        self.update_right()
        self.update_below()
        self.update_left()
