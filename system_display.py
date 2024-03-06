import pygame
import sys
import math

import galaxy
import player

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

class SystemDisplay():

    def __init__(self, star):
        self.star = star
        self.planet_locations = []
        self.set_planet_locations()
        self.primary_surface = pygame.Surface((SYSTEM_SURFACE_WIDTH, SYSTEM_SURFACE_HEIGHT))
        self.refresh_primary_surface()
        self.player_surface = create_blank_surface((SYSTEM_SURFACE_WIDTH, SYSTEM_SURFACE_HEIGHT))
        self.refresh_player_surface()
        self.ship_surface = create_blank_surface((SYSTEM_SURFACE_WIDTH, SYSTEM_SURFACE_HEIGHT))
        self.refresh_ship_surface()

    def set_planet_locations(self):
        # Relative to the system pane's pasted location
        self.planet_locations = []
        num_planets = len(self.star.planets)
        for p in range(num_planets):
            angle = p * 2 * math.pi / num_planets - math.pi / 2
            self.planet_locations.append((int(SYSTEM_SURFACE_WIDTH / 2 + SYSTEM_HORIZONTAL_AXIS * math.cos(angle)), int(SYSTEM_SURFACE_HEIGHT / 2 + SYSTEM_VERTICAL_AXIS * math.sin(angle))))
        
    def refresh_primary_surface(self):
        self.primary_surface.fill(COLOR_BACKGROUND)
        pygame.draw.circle(self.primary_surface, COLOR_STAR, (SYSTEM_SURFACE_WIDTH // 2, SYSTEM_SURFACE_HEIGHT // 2), SYSTEM_STAR_RADIUS)
        for p in range(len(self.star.planets)):
            pygame.draw.circle(self.primary_surface, galaxy.MINERAL_COLORS[self.star.planets[p].mineral], self.planet_locations[p], SYSTEM_PLANET_RADIUS)
            
    def refresh_player_surface(self):
        self.player_surface.fill(COLOR_BACKGROUND)
        for p in range(len(self.star.planets)):
            if self.star.planets[p].colony != None:
                pygame.draw.circle(self.player_surface, self.star.planets[p].colony.ruler.color, self.planet_locations[p], int(1.5 * SYSTEM_PLANET_RADIUS), SYSTEM_PLANET_RADIUS // 2)
            if self.star.planets[p].artifacts > 0:
                pygame.draw.circle(self.player_surface, COLOR_ARTIFACT_RING, self.planet_locations[p], SYSTEM_PLANET_RADIUS + SYSTEM_ARTIFACT_RING_WIDTH * 2, SYSTEM_ARTIFACT_RING_WIDTH)
                pygame.draw.circle(self.player_surface, COLOR_ARTIFACT_RING, self.planet_locations[p], SYSTEM_PLANET_RADIUS + SYSTEM_ARTIFACT_RING_WIDTH * 4, SYSTEM_ARTIFACT_RING_WIDTH)

    def refresh_ship_surface(self, player=None):
        self.ship_surface.fill(COLOR_BACKGROUND)
        star_ships = []
        for s in self.star.ships:
            if s.planet == None:
                star_ships.append(s)
        ship_display.draw_overlapping_ships(self.ship_surface, star_ships, (SYSTEM_SURFACE_WIDTH // 2, SYSTEM_SURFACE_HEIGHT // 2), player)
        for p in range(len(self.star.planets)):
            ship_display.draw_overlapping_ships(self.ship_surface, self.star.planets[p].ships, self.planet_locations[p], player)

    def draw(self, display, pane_location):
        display.blit(self.primary_surface, pane_location)
        display.blit(self.player_surface, pane_location)
        display.blit(self.ship_surface, pane_location)

    def find_planet(self, position):
        """
        Position relative to pane
        """
        for p in range(len(self.planet_locations)):
            if math.hypot(self.planet_locations[p][0] - position[0], self.planet_locations[p][1] - position[1]) <= SYSTEM_PLANET_RADIUS:
                return self.star.planets[p]
        return None
    
    def is_star_clicked(self, position):
        return math.hypot(SYSTEM_SURFACE_WIDTH / 2 - position[0], SYSTEM_SURFACE_HEIGHT / 2 - position[1]) <= SYSTEM_STAR_RADIUS
    
    def find_ship(self, position):
        # First, star ships:
        star_ships = []
        for s in self.star.ships:
            if s.planet == None:
                star_ships.append(s)
        star_ship = ship_display.find_overlapped_ship((SYSTEM_SURFACE_WIDTH // 2, SYSTEM_SURFACE_HEIGHT // 2), star_ships, position, SYSTEM_SHIP_RADIUS)
        if star_ship != None:
            return star_ship
        # Next, planet ships:
        for p in range(len(self.star.planets)):
            planet_ship = ship_display.find_overlapped_ship(self.planet_locations[p], self.star.planets[p].ships, position, SYSTEM_SHIP_RADIUS)
            if planet_ship != None:
                return planet_ship
        return None