import pygame
import math

import galaxy
import ship_display

GALAXY_STAR_RADIUS = 12
GALAXY_PLANET_RADIUS = 3

COLOR_BACKGROUND = (10, 10, 10)
COLOR_UNEXPLORED_STAR = (135, 135, 135)
COLOR_STAR = (200, 170, 25)

MINERAL_COLORS = [(200, 20, 20), (20, 200, 20), (20, 20, 200), (200, 200, 20), (200, 20, 200), (20, 200, 200)]

def create_blank_surface(dimensions):
    """
    Creates a new surface that sets the background color as transparent 
    Meaning that filling in the surface with the background color will fill with transparency
    """
    surface = pygame.Surface(dimensions)
    surface.set_colorkey(COLOR_BACKGROUND)
    surface.fill(COLOR_BACKGROUND)
    return surface

def scale_location(location, scale_factor):
    return (int(location[0] * scale_factor), int(location[1] * scale_factor))

class GalaxyDisplay():

    def __init__(self, game, player, dimensions):
        self.game = game
        self.player = player
        self.scale_factor = 1.0
        self.pan = [0, 0]
        self.display_dimensions = dimensions
        self.player_surface = pygame.Surface(dimensions)
        self.refresh_player_surface()
        self.primary_surface = create_blank_surface(dimensions)
        self.refresh_primary_surface()
        self.ship_surface = create_blank_surface(dimensions)
        self.refresh_ship_surface()

    def set_scale_factor(self, new_scale_factor, center):
        self.pan = [self.pan[0] + (self.scale_factor - new_scale_factor) * (center[0] / self.scale_factor - self.pan[0]), 
                    self.pan[1] + (self.scale_factor - new_scale_factor) * (center[1] / self.scale_factor - self.pan[1])]
        self.scale_factor = new_scale_factor

    def refresh_primary_surface(self):
        self.primary_surface.fill(COLOR_BACKGROUND)
        for i in range(len(self.game.galaxy.stars)):
            s = self.game.galaxy.stars[i]
            star_color = COLOR_UNEXPLORED_STAR
            if self.player.explored_stars[i]:
                if s.ruler != None:
                    pygame.draw.circle(self.primary_surface, s.ruler.color, scale_location(s.location, self.scale_factor), int(1.5 * self.scale_factor * GALAXY_STAR_RADIUS))
                star_color = COLOR_STAR
            pygame.draw.circle(self.primary_surface, star_color, scale_location(s.location, self.scale_factor), int(self.scale_factor * GALAXY_STAR_RADIUS))
            # pygame.draw.circle(surface, (255, 255, 255), s.location, radii, 1)
            numPlanets = len(s.planets)
            for p in range(numPlanets):
                angle = p * 2 * math.pi / numPlanets
                planetCenter = (int(s.location[0] + GALAXY_STAR_RADIUS * math.cos(angle)), int(s.location[1] + GALAXY_STAR_RADIUS * math.sin(angle)))
                pygame.draw.circle(self.primary_surface, galaxy.MINERAL_COLORS[s.planets[p].mineral], scale_location(planetCenter, self.scale_factor), int(self.scale_factor * GALAXY_PLANET_RADIUS))

    def refresh_player_surface(self):
        # TODO: Add connectivity lines between players' colonies
        self.player_surface.fill(COLOR_BACKGROUND)
        for i in range(len(self.game.galaxy.stars)):
            s = self.game.galaxy.stars[i]
            if self.player.explored_stars[i]:
                if s.ruler != None:
                    pygame.draw.circle(self.player_surface, s.ruler.color, scale_location(s.location, self.scale_factor), int(1.5 * self.scale_factor * GALAXY_STAR_RADIUS))

    def refresh_ship_surface(self):
        self.ship_surface.fill(COLOR_BACKGROUND)
        for p in self.game.players:
            for s in p.ships:
                if s.star == None:
                    ship_display.draw_ship(self.ship_surface, s, scale_location(s.location, self.scale_factor))

    def draw(self, display, pane_location):
        display.blit(self.player_surface, pane_location)
        display.blit(self.primary_surface, pane_location)
        display.blit(self.ship_surface, pane_location)
