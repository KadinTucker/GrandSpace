import pygame
import math

import galaxy
import pane
import ship_display
import system_display

GALAXY_STAR_RADIUS = 12
GALAXY_PLANET_RADIUS = 3
GALAXY_SHIP_RADIUS = 10  # At view scale 1.0

EMPIRE_CONTROL_LINE_WIDTH = 5

COLOR_BACKGROUND = (20, 20, 20)
COLOR_UNEXPLORED_STAR = (135, 135, 135)
COLOR_STAR = (200, 170, 25)

COLONY_HALO_MODIFIER = 1.3
CAPITAL_STAR_MINOR_MODIFIER = 1.0
CAPITAL_STAR_MAJOR_MODIFIER = 1.0
CAPITAL_STAR_ANGLES = [(i + 0.5) * math.pi / 5 for i in range(10)]

MINERAL_COLORS = [(200, 20, 20), (20, 200, 20), (20, 20, 200), (200, 200, 20), (200, 20, 200), (20, 200, 200)]

def draw_five_point_star(surface, color, center, minor_radius, major_radius):
    pygame.draw.polygon(surface, color, [(int(center[0] + (minor_radius + major_radius * (a % 2))
                                              * math.cos(CAPITAL_STAR_ANGLES[a])),
                                          int(center[1] + (minor_radius + major_radius * (a % 2))
                                              * math.sin(CAPITAL_STAR_ANGLES[a]))) for a in range(10)])

class GalaxyDisplay(pane.Pane):

    def __init__(self, game, player, galaxy_dimensions, pane_dimensions, pane_position):
        super().__init__(game, player, pane_dimensions, pane_position, 3, COLOR_BACKGROUND)
        self.galaxy_dimensions = galaxy_dimensions
        self.refresh_all_layers()

    def find_star(self, click_location):
        location = self.deproject_coordinate(click_location)
        for s in self.game.galaxy.stars:
            if math.hypot(s.location[0] - location[0], s.location[1] - location[1]) <= GALAXY_STAR_RADIUS:
                return s
        return None
    
    def find_player_ship(self, click_location):
        location = self.deproject_coordinate(click_location)
        for s in self.player.ships:
            if math.hypot(s.location[0] - location[0],
                          s.location[1] - location[1]) <= GALAXY_SHIP_RADIUS / self.view_scale:
                return s

    def sketch_primary_surface(self):
        for i in range(len(self.game.galaxy.stars)):
            s = self.game.galaxy.stars[i]
            star_color = COLOR_UNEXPLORED_STAR
            if self.player.explored_stars[i]:
                star_color = COLOR_STAR
            pygame.draw.circle(self.layers[1], star_color, self.project_coordinate(s.location),
                               int(self.view_scale * GALAXY_STAR_RADIUS))
            num_planets = len(s.planets)
            for p in range(num_planets):
                angle = p * 2 * math.pi / num_planets
                planet_center = (int(s.location[0] + GALAXY_STAR_RADIUS * math.cos(angle)),
                                 int(s.location[1] + GALAXY_STAR_RADIUS * math.sin(angle)))
                pygame.draw.circle(self.layers[1], galaxy.MINERAL_COLORS[s.planets[p].mineral],
                                   self.project_coordinate(planet_center), int(self.view_scale * GALAXY_PLANET_RADIUS))

    def sketch_player_surface(self):
        for i in range(len(self.game.galaxy.stars)):
            s = self.game.galaxy.stars[i]
            if self.player.explored_stars[i]:
                if s.ruler is not None:
                    pygame.draw.circle(self.layers[0], s.ruler.color, self.project_coordinate(s.location),
                                       int(COLONY_HALO_MODIFIER * self.view_scale * GALAXY_STAR_RADIUS))
                    if s == s.ruler.homeworld.star:
                        draw_five_point_star(self.layers[0], s.ruler.color, self.project_coordinate(s.location),
                                             int(CAPITAL_STAR_MINOR_MODIFIER * self.view_scale * GALAXY_STAR_RADIUS),
                                             int(CAPITAL_STAR_MAJOR_MODIFIER * self.view_scale * GALAXY_STAR_RADIUS))
        for p in self.game.players:
            for s in p.ruled_stars:
                if self.player.explored_stars[s.id] and s.connected_star is not None:
                    pygame.draw.line(self.layers[0], p.color, self.project_coordinate(s.location),
                                     self.project_coordinate(s.connected_star.location),
                                     int(self.view_scale * EMPIRE_CONTROL_LINE_WIDTH))

    def sketch_ship_surface(self):
        for p in self.game.players:
            for s in p.ships:
                if s.star is None:
                    ship_display.draw_ship(self.layers[2], s, self.project_coordinate(s.location), self.player)

    def refresh_layer(self, index):
        super().refresh_layer(index)
        if index == 0:
            self.sketch_player_surface()
        elif index == 1:
            self.sketch_primary_surface()
        elif index == 2:
            self.sketch_ship_surface()

    def handle_event(self, event, mouse_pos, active_player):
        super().handle_event(event, mouse_pos, active_player)
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == pygame.BUTTON_RIGHT:
                active_player.selected_ship.set_destination_star(self.find_star(self.get_relative_pane_pos(mouse_pos)))
            elif event.button == pygame.BUTTON_LEFT:
                new_ship = self.find_player_ship(self.get_relative_pane_pos(mouse_pos))
                if new_ship is not None:
                    active_player.selected_ship = new_ship
                if self.num_clicks >= 2:
                    star = self.find_star(self.get_relative_pane_pos(mouse_pos))
                    if star is not None and active_player.explored_stars[star.id]:
                        self.next_pane_id = system_display.get_pane_id(star.id)
                    self.num_clicks = 0
