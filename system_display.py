import pygame
import math

import galaxy

import pane
import ship_display

SYSTEM_STAR_RADIUS = 60
SYSTEM_PLANET_RADIUS = 15
SYSTEM_HORIZONTAL_AXIS = 300
SYSTEM_VERTICAL_AXIS = 150
SYSTEM_ARTIFACT_RING_WIDTH = 2

SYSTEM_SURFACE_WIDTH = 2 * SYSTEM_HORIZONTAL_AXIS + 4 * SYSTEM_PLANET_RADIUS + 2
SYSTEM_SURFACE_HEIGHT = 2 * SYSTEM_VERTICAL_AXIS + 4 * SYSTEM_PLANET_RADIUS + 2

SYSTEM_SHIP_RADIUS = 10

COLOR_BACKGROUND = (10, 10, 10)
COLOR_STAR = (200, 170, 25)
COLOR_ARTIFACT_RING = (150, 125, 35)
COLOR_SHIP_SELECTION = (225, 225, 225)

def create_blank_surface(dimensions):
    """
    Creates a new surface that sets the background color as transparent 
    Meaning that filling in the surface with the background color will fill with transparency
    """
    surface = pygame.Surface(dimensions)
    surface.set_colorkey(COLOR_BACKGROUND)
    surface.fill(COLOR_BACKGROUND)
    return surface

def get_pane_id(star_id):
    return star_id + 1

class SystemDisplay(pane.Pane):

    def __init__(self, game, player, pane_dimensions, pane_position, star):
        super().__init__(game, player, pane_dimensions, pane_position, 3, COLOR_BACKGROUND)
        self.star = star
        self.planet_locations = []
        self.set_planet_locations()

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
                                   int(1.5 * SYSTEM_PLANET_RADIUS), SYSTEM_PLANET_RADIUS // 2)
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

    def refresh_layer(self, index):
        super().refresh_layer(index)
        if index == 0:
            self.sketch_primary_surface()
        elif index == 1:
            self.sketch_player_surface()
        elif index == 2:
            self.sketch_ship_surface()

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
