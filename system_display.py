import pygame
import math

import ecology
import galaxy

import pane
import ship_display

SYSTEM_STAR_RADIUS = 60
SYSTEM_PLANET_RADIUS = 20
SYSTEM_HORIZONTAL_AXIS = 300
SYSTEM_VERTICAL_AXIS = 150
SYSTEM_ARTIFACT_RING_WIDTH = 2

SYSTEM_SURFACE_WIDTH = 2 * SYSTEM_HORIZONTAL_AXIS + 4 * SYSTEM_PLANET_RADIUS + 2
SYSTEM_SURFACE_HEIGHT = 2 * SYSTEM_VERTICAL_AXIS + 4 * SYSTEM_PLANET_RADIUS + 2

SYSTEM_SHIP_RADIUS = 10

ECOLOGY_SPECIES_ALTITUDE = SYSTEM_PLANET_RADIUS * 3
ECOLOGY_SPECIES_WIDTH = 12
ECOLOGY_SPECIES_HEIGHT = 16
ECOLOGY_SPECIES_SPACING = 6

ECOLOGY_BIOMASS_ALTITUDE = SYSTEM_PLANET_RADIUS * 2
ECOLOGY_BIOMASS_HEIGHT = 10
ECOLOGY_BIOMASS_WIDTH = 30
ECOLOGY_BIOMASS_HALO_WIDTH = 2

ECOLOGY_SPECIES_FILENAMES = ["assets/typeface/eco-serif/" + letter + ".png" for letter in ecology.BIOMASS_TYPES]

INDICATOR_HABITAT_IMG = pygame.image.load("assets/indicator-habitat-new.png")
INDICATOR_CITY_IMG = pygame.image.load("assets/indicator-city-new.png")
INDICATOR_DEVELOPMENT_IMG = pygame.image.load("assets/indicator-development-new.png")

COLOR_BACKGROUND = (10, 10, 10)
COLOR_STAR = (200, 130, 25)
COLOR_ARTIFACT_RING = (150, 125, 35)
COLOR_SHIP_SELECTION = (225, 225, 225)
COLOR_BIOMASS_EMPTY = (95, 35, 15)
COLOR_BIOMASS_FULL = (25, 110, 15)
COLOR_BIOMASS_HALO = (110, 220, 110)

def get_ring_distribution_coordinates(center, radius, num_items):
    coordinates = [[0, 0] for _ in range(num_items)]
    num_rings = int(math.sqrt(num_items) + 1)
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

def get_pane_id(star_id):
    return star_id + 1

class SystemDisplay(pane.Pane):

    def __init__(self, game, player, pane_dimensions, pane_position, star):
        super().__init__(game, player, pane_dimensions, pane_position, 5, COLOR_BACKGROUND)
        self.star = star
        self.planet_locations = []
        self.set_planet_locations()
        self.species_images = [pygame.image.load(fn) for fn in ECOLOGY_SPECIES_FILENAMES]
        self.refresh_all_layers()

    def set_planet_locations(self):
        # Relative to the system pane's pasted location
        self.planet_locations = []
        num_planets = len(self.star.planets)
        for p in range(num_planets):
            angle = p * 2 * math.pi / num_planets - math.pi / 2
            self.planet_locations.append((int(self.pane_dimensions[0] / 2 + SYSTEM_HORIZONTAL_AXIS * math.cos(angle)),
                                          int(self.pane_dimensions[1] / 2 + SYSTEM_VERTICAL_AXIS * math.sin(angle))))
        
    def sketch_primary_surface(self):
        self.layers[0].fill(COLOR_BACKGROUND)
        pygame.draw.circle(self.layers[0], COLOR_STAR,
                           (self.pane_dimensions[0] // 2, self.pane_dimensions[1] // 2), SYSTEM_STAR_RADIUS)
        for p in range(len(self.star.planets)):
            pygame.draw.circle(self.layers[0], galaxy.MINERAL_COLORS[self.star.planets[p].mineral],
                               self.planet_locations[p], SYSTEM_PLANET_RADIUS)
            
    def sketch_player_surface(self):
        self.layers[1].fill(COLOR_BACKGROUND)
        for p in range(len(self.star.planets)):
            if self.star.planets[p].colony is not None:
                pygame.draw.circle(self.layers[1], self.star.planets[p].colony.ruler.color, self.planet_locations[p],
                                   int(1.5 * SYSTEM_PLANET_RADIUS), SYSTEM_PLANET_RADIUS // 2 + 1)
            if self.star.planets[p].artifacts > 0:
                pygame.draw.circle(self.layers[1], COLOR_ARTIFACT_RING, self.planet_locations[p],
                                   SYSTEM_PLANET_RADIUS + SYSTEM_ARTIFACT_RING_WIDTH * 2, SYSTEM_ARTIFACT_RING_WIDTH)
                pygame.draw.circle(self.layers[1], COLOR_ARTIFACT_RING, self.planet_locations[p],
                                   SYSTEM_PLANET_RADIUS + SYSTEM_ARTIFACT_RING_WIDTH * 4, SYSTEM_ARTIFACT_RING_WIDTH)

    def sketch_ship_surface(self):
        self.layers[2].fill(COLOR_BACKGROUND)
        star_ships = []
        for s in self.star.ships:
            if s.planet is None:
                star_ships.append(s)
        ship_display.draw_overlapping_ships(self.layers[2], star_ships,
                                            (self.pane_dimensions[0] // 2, self.pane_dimensions[1] // 2),
                                            self.player)
        for p in range(len(self.star.planets)):
            ship_display.draw_overlapping_ships(self.layers[2], self.star.planets[p].ships,
                                                self.planet_locations[p], self.player)

    def sketch_ecology_surface(self):
        self.layers[3].fill(COLOR_BACKGROUND)
        for p in range(len(self.star.planets)):
            # Biomass Bar
            if self.star.planets[p].ecology.habitability > 0:
                if self.star.planets[p].ecology.biomass_level == 1:
                    pygame.draw.rect(self.layers[3], COLOR_BIOMASS_HALO,
                                     pygame.Rect(self.planet_locations[p][0] - ECOLOGY_BIOMASS_WIDTH // 2
                                                 - ECOLOGY_BIOMASS_HALO_WIDTH,
                                                 self.planet_locations[p][1] - ECOLOGY_BIOMASS_HEIGHT
                                                 - ECOLOGY_BIOMASS_ALTITUDE - ECOLOGY_BIOMASS_HALO_WIDTH,
                                                 ECOLOGY_BIOMASS_WIDTH + ECOLOGY_BIOMASS_HALO_WIDTH * 2,
                                                 ECOLOGY_BIOMASS_HEIGHT + ECOLOGY_BIOMASS_HALO_WIDTH * 2))
                else:
                    pygame.draw.rect(self.layers[3], COLOR_BIOMASS_EMPTY,
                                     pygame.Rect(self.planet_locations[p][0] - ECOLOGY_BIOMASS_WIDTH // 2,
                                                 self.planet_locations[p][1] - ECOLOGY_BIOMASS_HEIGHT
                                                 - ECOLOGY_BIOMASS_ALTITUDE, ECOLOGY_BIOMASS_WIDTH,
                                                 ECOLOGY_BIOMASS_HEIGHT))
                pygame.draw.rect(self.layers[3], COLOR_BIOMASS_FULL,
                                 pygame.Rect(self.planet_locations[p][0] - ECOLOGY_BIOMASS_WIDTH // 2,
                                             self.planet_locations[p][1] - ECOLOGY_BIOMASS_HEIGHT
                                             - ECOLOGY_BIOMASS_ALTITUDE,
                                             int(ECOLOGY_BIOMASS_WIDTH * self.star.planets[p].ecology.biomass_level),
                                             ECOLOGY_BIOMASS_HEIGHT))
            # Species Icons
            species = []
            for j in range(len(self.star.planets[p].ecology.species)):
                if self.star.planets[p].ecology.species[j]:
                    species.append(j)
            for s in range(len(species)):
                self.layers[3].blit(self.species_images[species[s]],
                                    (self.planet_locations[p][0] - (ECOLOGY_SPECIES_SPACING * (len(species) - 1)
                                     + ECOLOGY_SPECIES_WIDTH * len(species)) // 2
                                     + s * (ECOLOGY_SPECIES_WIDTH + ECOLOGY_SPECIES_SPACING),
                                     self.planet_locations[p][1] - ECOLOGY_SPECIES_ALTITUDE - ECOLOGY_SPECIES_HEIGHT))

    def sketch_planet_detail_surface(self):
        self.layers[4].fill(COLOR_BACKGROUND)
        for p in range(len(self.star.planets)):
            # Draw cities, development pips, then trees, in a spiral fashion
            num_cities = 0
            num_development = 0
            if self.star.planets[p].colony is not None:
                num_cities = self.star.planets[p].colony.cities
                num_development = self.star.planets[p].colony.development
            num_habit = self.star.planets[p].ecology.habitability * 3
            pip_locations = get_ring_distribution_coordinates((self.planet_locations[p][0] - 4,
                                                               self.planet_locations[p][1] - 4), SYSTEM_PLANET_RADIUS,
                                                              num_cities + num_development + num_habit)
            for i in range(len(pip_locations)):
                if i < num_cities:
                    self.layers[4].blit(INDICATOR_CITY_IMG, pip_locations[i])
                elif i < num_cities + num_development:
                    self.layers[4].blit(INDICATOR_DEVELOPMENT_IMG, pip_locations[i])
                else:
                    self.layers[4].blit(INDICATOR_HABITAT_IMG, pip_locations[i])

    def refresh_layer(self, index):
        super().refresh_layer(index)
        if index == 0:
            self.sketch_primary_surface()
        elif index == 1:
            self.sketch_player_surface()
        elif index == 2:
            self.sketch_ship_surface()
        elif index == 3:
            self.sketch_ecology_surface()
        elif index == 4:
            self.sketch_planet_detail_surface()

    def find_planet(self, position):
        """
        Position relative to pane
        """
        for p in range(len(self.planet_locations)):
            if math.hypot(self.planet_locations[p][0] - position[0],
                          self.planet_locations[p][1] - position[1]) <= SYSTEM_PLANET_RADIUS:
                return self.star.planets[p]
        return None
    
    def is_star_clicked(self, position):
        return math.hypot(self.pane_dimensions[0] / 2 - position[0],
                          self.pane_dimensions[1] / 2 - position[1]) <= SYSTEM_STAR_RADIUS

    def handle_event(self, event, mouse_pos):
        super().handle_event(event, mouse_pos)
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == pygame.BUTTON_RIGHT:
                self.player.selected_ship.reset_task()
                if self.is_star_clicked(self.get_relative_pane_pos(mouse_pos)):
                    if self.player.selected_ship.planet is None:
                        self.player.selected_ship.set_destination_star(None)
                    else:
                        self.player.selected_ship.set_destination_planet(None)
                else:
                    planet = self.find_planet(self.get_relative_pane_pos(mouse_pos))
                    if planet is not None:
                        self.player.selected_ship.set_destination_planet(planet)
            elif event.button == pygame.BUTTON_LEFT:
                new_ship = self.find_ship(self.get_relative_pane_pos(mouse_pos))
                if new_ship is not None and new_ship.ruler is self.player:
                    self.player.selected_ship = new_ship
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.next_pane_id = 0
    
    def find_ship(self, position):
        # First, star ships:
        all_star_ships = []
        for s in self.star.ships:
            if s.planet is None:
                all_star_ships.append(s)
        star_ship = ship_display.find_overlapped_ship((self.pane_dimensions[0] // 2,
                                                      self.pane_dimensions[1] // 2), all_star_ships,
                                                      position, SYSTEM_SHIP_RADIUS)
        if star_ship is not None:
            return star_ship
        # Next, planet ships:
        for p in range(len(self.star.planets)):
            planet_ship = ship_display.find_overlapped_ship(self.planet_locations[p],
                                                            self.star.planets[p].ships, position, SYSTEM_SHIP_RADIUS)
            if planet_ship is not None:
                return planet_ship
        return None
