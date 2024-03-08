import pygame
import math

import galaxy
import ship_display

GALAXY_STAR_RADIUS = 12
GALAXY_PLANET_RADIUS = 3
GALAXY_SHIP_RADIUS = 10 # At view scale 1.0

EMPIRE_CONTROL_LINE_WIDTH = 5

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

    def find_star(self, click_location):
        location = self.deproject_coordinate(click_location)
        for s in self.game.galaxy.stars:
            if math.hypot(s.location[0] - location[0], s.location[1] - location[1]) <= GALAXY_STAR_RADIUS:
                return s
        return None
    
    def find_player_ship(self, click_location):
        location = self.deproject_coordinate(click_location)
        for s in self.player.ships:
            if math.hypot(s.location[0] - location[0], s.location[1] - location[1]) <= GALAXY_SHIP_RADIUS / self.view_scale:
                return s

    def project_coordinate(self, coordinate):
        """
        Turns a galaxy coordinate into a pane display coordinate
        """
        return (int(self.view_scale * (coordinate[0] - self.view_corner[0])), int(self.view_scale * (coordinate[1] - self.view_corner[1])))

    def deproject_coordinate(self, coordinate):
        """
        Turns a pane display coordinate into a galaxy coordinate
        """
        return (int(coordinate[0] / self.view_scale + self.view_corner[0]), int(coordinate[1] / self.view_scale + self.view_corner[1]))

    def refresh_primary_surface(self):
        self.primary_surface.fill(COLOR_BACKGROUND)
        for i in range(len(self.game.galaxy.stars)):
            s = self.game.galaxy.stars[i]
            star_color = COLOR_UNEXPLORED_STAR
            if self.player.explored_stars[i]:
                if s.ruler != None:
                    pygame.draw.circle(self.primary_surface, s.ruler.color, self.project_coordinate(s.location), int(1.5 * self.view_scale * GALAXY_STAR_RADIUS))
                star_color = COLOR_STAR
            pygame.draw.circle(self.primary_surface, star_color, self.project_coordinate(s.location), int(self.view_scale * GALAXY_STAR_RADIUS))
            numPlanets = len(s.planets)
            for p in range(numPlanets):
                angle = p * 2 * math.pi / numPlanets
                planetCenter = (int(s.location[0] + GALAXY_STAR_RADIUS * math.cos(angle)), int(s.location[1] + GALAXY_STAR_RADIUS * math.sin(angle)))
                pygame.draw.circle(self.primary_surface, galaxy.MINERAL_COLORS[s.planets[p].mineral], self.project_coordinate(planetCenter), int(self.view_scale * GALAXY_PLANET_RADIUS))

    def refresh_player_surface(self):
        self.player_surface.fill(COLOR_BACKGROUND)
        for i in range(len(self.game.galaxy.stars)):
            s = self.game.galaxy.stars[i]
            if self.player.explored_stars[i]:
                if s.ruler != None:
                    pygame.draw.circle(self.player_surface, s.ruler.color, self.project_coordinate(s.location), int(1.5 * self.view_scale * GALAXY_STAR_RADIUS))
        for p in self.game.players:
            for s in range(1, len(p.ruled_stars)):
                if self.player.explored_stars[p.ruled_stars[s].id]:
                    pygame.draw.line(self.player_surface, p.color, self.project_coordinate(p.ruled_stars[s].location), self.project_coordinate(p.ruled_stars[p.star_network[s]].location), EMPIRE_CONTROL_LINE_WIDTH)


    def refresh_ship_surface(self):
        self.ship_surface.fill(COLOR_BACKGROUND)
        for p in self.game.players:
            for s in p.ships:
                if s.star == None:
                    ship_display.draw_ship(self.ship_surface, s, self.project_coordinate(s.location), self.player)

    def draw(self, display, pane_location):
        display.blit(self.player_surface, pane_location)
        display.blit(self.primary_surface, pane_location)
        display.blit(self.ship_surface, pane_location)
