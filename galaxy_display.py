import pygame
import math

import galaxy
import ship_display

GALAXY_STAR_RADIUS = 12
GALAXY_PLANET_RADIUS = 3

COLOR_BACKGROUND = (20, 20, 20)
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

def project_to_pane(location, view_corner, view_scale):
    return (int(view_scale * (location[0] - view_corner[0])), int(view_scale * (location[1] - view_corner[1])))

class GalaxyDisplay():

    def __init__(self, game, player, galaxy_dimensions, pane_dimensions):
        self.game = game
        self.player = player
        self.galaxy_dimensions = galaxy_dimensions
        self.pane_dimensions = pane_dimensions
        self.view_corner = (0, 0)
        self.view_scale = 1.0
        self.player_surface = pygame.Surface(pane_dimensions)
        self.refresh_player_surface()
        self.primary_surface = create_blank_surface(pane_dimensions)
        self.refresh_primary_surface()
        self.ship_surface = create_blank_surface(pane_dimensions)
        self.refresh_ship_surface()

    def set_scale(self, new_scale, center):
        scale_change_coefficient = 1 / self.view_scale - 1 / new_scale
        self.view_corner = (self.view_corner[0] + center[0] * scale_change_coefficient, self.view_corner[1] + center[1] * scale_change_coefficient)
        self.view_scale = new_scale
        self.refresh_player_surface()
        self.refresh_primary_surface()
        self.refresh_ship_surface()

    def refresh_primary_surface(self):
        self.primary_surface.fill(COLOR_BACKGROUND)
        for i in range(len(self.game.galaxy.stars)):
            s = self.game.galaxy.stars[i]
            star_color = COLOR_UNEXPLORED_STAR
            if self.player.explored_stars[i]:
                if s.ruler != None:
                    pygame.draw.circle(self.primary_surface, s.ruler.color, project_to_pane(s.location, self.view_corner, self.view_scale), int(1.5 * self.view_scale * GALAXY_STAR_RADIUS))
                star_color = COLOR_STAR
            pygame.draw.circle(self.primary_surface, star_color, project_to_pane(s.location, self.view_corner, self.view_scale), int(self.view_scale * GALAXY_STAR_RADIUS))
            # pygame.draw.circle(surface, (255, 255, 255), s.location, radii, 1)
            numPlanets = len(s.planets)
            for p in range(numPlanets):
                angle = p * 2 * math.pi / numPlanets
                planetCenter = (int(s.location[0] + GALAXY_STAR_RADIUS * math.cos(angle)), int(s.location[1] + GALAXY_STAR_RADIUS * math.sin(angle)))
                pygame.draw.circle(self.primary_surface, galaxy.MINERAL_COLORS[s.planets[p].mineral], project_to_pane(planetCenter, self.view_corner, self.view_scale), int(self.view_scale * GALAXY_PLANET_RADIUS))

    def refresh_player_surface(self):
        # TODO: Add connectivity lines between players' colonies
        self.player_surface.fill(COLOR_BACKGROUND)
        for i in range(len(self.game.galaxy.stars)):
            s = self.game.galaxy.stars[i]
            if self.player.explored_stars[i]:
                if s.ruler != None:
                    pygame.draw.circle(self.player_surface, s.ruler.color, project_to_pane(s.location, self.view_corner, self.view_scale), int(1.5 * self.view_scale * GALAXY_STAR_RADIUS))

    def refresh_ship_surface(self):
        self.ship_surface.fill(COLOR_BACKGROUND)
        for p in self.game.players:
            for s in p.ships:
                if s.star == None:
                    ship_display.draw_ship(self.ship_surface, s, project_to_pane(s.location, self.view_corner, self.view_scale))

    def draw(self, display, pane_location):
        display.blit(self.player_surface, pane_location)
        display.blit(self.primary_surface, pane_location)
        display.blit(self.ship_surface, pane_location)
