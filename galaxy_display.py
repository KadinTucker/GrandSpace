import pygame
import math

import galaxy
import pane
import drag_pane
import ship_display
import ship_tasks
import system_display

GALAXY_STAR_RADIUS = 8
GALAXY_PLANET_RADIUS = 2
GALAXY_SHIP_RADIUS = 10  # At view scale 1.0

GALAXY_RING_WIDTH = 1

SCROLL_SPEED = 0.125  # As a fraction of pane size

EMPIRE_CONTROL_LINE_WIDTH = 5

COLOR_BACKGROUND = (20, 20, 20)
COLOR_UNEXPLORED_STAR = (50, 50, 50)
COLOR_UNSEEN_STAR = (175, 165, 135)
COLOR_STAR = (200, 170, 25)
COLOR_STAR_IN_RANGE = (230, 190, 50)
COLOR_ARTIFACT_RING = (150, 125, 35)
COLOR_CIVILIZATION_RING = (35, 125, 150)
COLOR_FOG = (165, 165, 165)
IN_RANGE_INDICATOR_RADIUS = 8
IN_RANGE_INDICATOR_WIDTH = 2

COLONY_HALO_MODIFIER = 1.3
CAPITAL_STAR_MINOR_MODIFIER = 1.0
CAPITAL_STAR_MAJOR_MODIFIER = 1.0
CAPITAL_STAR_ANGLES = [(i + 0.5) * math.pi / 5 for i in range(10)]

MINERAL_COLORS = [(200, 20, 20), (20, 200, 20), (20, 20, 200), (200, 200, 20), (200, 20, 200), (20, 200, 200)]

def get_color_blend(color1, color2, color1_share):
    return (int(color1[0] * color1_share + color2[0] * (1 - color1_share)),
            int(color1[1] * color1_share + color2[1] * (1 - color1_share)),
            int(color1[2] * color1_share + color2[2] * (1 - color1_share)))

def draw_five_point_star(surface, color, center, minor_radius, major_radius):
    pygame.draw.polygon(surface, color, [(int(center[0] + (minor_radius + major_radius * (a % 2))
                                              * math.cos(CAPITAL_STAR_ANGLES[a])),
                                          int(center[1] + (minor_radius + major_radius * (a % 2))
                                              * math.sin(CAPITAL_STAR_ANGLES[a]))) for a in range(10)])

class GalaxyDisplay(drag_pane.DragPane):

    def __init__(self, game, player, galaxy_dimensions, pane_dimensions, pane_position):
        super().__init__(game, player, pane_dimensions, pane_position, 3, COLOR_BACKGROUND)
        self.galaxy_dimensions = galaxy_dimensions
        self.update()

    def find_star(self, click_location):
        location = self.deproject_coordinate(click_location)
        for s in self.game.galaxy.stars:
            if math.hypot(s.location[0] - location[0], s.location[1] - location[1]) <= GALAXY_STAR_RADIUS:
                return s
        return None

    def draw_vision(self, dest_surface):
        for s in self.player.ruled_stars + self.player.ships:
            pygame.draw.circle(dest_surface, get_color_blend(self.player.color, COLOR_BACKGROUND, 0.1),
                               self.project_coordinate(s.location),
                               self.view_scale * self.player.technology.get_visibility_range())

    def set_view_center(self, obj_center):
        self.view_corner = (self.dimensions[0] / 2 - self.view_scale * obj_center[0],
                            self.dimensions[1] / 2 - self.view_scale * obj_center[1])
        self.update()
    
    def find_player_ship(self, click_location):
        location = self.deproject_coordinate(click_location)
        for s in self.player.ships:
            if s.star is None:
                if math.hypot(s.location[0] - location[0],
                              s.location[1] - location[1]) <= GALAXY_SHIP_RADIUS / self.view_scale:
                    return s

    def draw_rings(self, dest_surface, color, star):
        pygame.draw.circle(dest_surface, color, self.project_coordinate(star.location),
                           int(self.view_scale * (GALAXY_STAR_RADIUS + GALAXY_RING_WIDTH * 2)),
                           int(self.view_scale * GALAXY_RING_WIDTH))
        pygame.draw.circle(dest_surface, color, self.project_coordinate(star.location),
                           int(self.view_scale * (GALAXY_STAR_RADIUS + GALAXY_RING_WIDTH * 4)),
                           int(self.view_scale * GALAXY_RING_WIDTH))

    def sketch_primary_surface(self):
        for i in range(len(self.game.galaxy.stars)):
            s = self.game.galaxy.stars[i]
            star_color = COLOR_STAR
            explored = self.player.explored_stars[i]
            visible = self.player.visibility.get_visible(s)
            if visible:
                if s.has_artifact():
                    self.draw_rings(self.layers[1], COLOR_ARTIFACT_RING, s)
            else:
                star_color = COLOR_UNSEEN_STAR
            if not explored:
                star_color = COLOR_UNEXPLORED_STAR
                if visible and s.ruler is not None:
                    self.draw_rings(self.layers[1], COLOR_CIVILIZATION_RING, s)

            pygame.draw.circle(self.layers[1], star_color, self.project_coordinate(s.location),
                               int(self.view_scale * GALAXY_STAR_RADIUS))
            if self.player.explored_stars[i]:
                num_planets = len(s.planets)
                for p in range(num_planets):
                    angle = p * 2 * math.pi / num_planets
                    planet_center = (int(s.location[0] + GALAXY_STAR_RADIUS * math.cos(angle)),
                                     int(s.location[1] + GALAXY_STAR_RADIUS * math.sin(angle)))
                    pygame.draw.circle(self.layers[1], galaxy.MINERAL_COLORS[s.planets[p].mineral],
                                       self.project_coordinate(planet_center),
                                       int(self.view_scale * GALAXY_PLANET_RADIUS))

    def sketch_player_surface(self):
        # Draw empire connection lines
        # TODO: make it a "snapshot", so changes in empire lines are not recorded
        self.draw_vision(self.layers[0])
        for p in self.game.players:
            for s in p.ruled_stars:
                if self.player.explored_stars[s.id] and s.connected_star is not None:
                    pygame.draw.line(self.layers[0], p.color, self.project_coordinate(s.location),
                                     self.project_coordinate(s.connected_star.location),
                                     int(self.view_scale * EMPIRE_CONTROL_LINE_WIDTH))
        # Draw player control markers
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

    def sketch_ship_surface(self):
        ship_display.draw_ship_selection(self.layers[2], self.project_coordinate(self.player.selected_ship.location))
        ship_display.draw_ship_galaxy_range(self.layers[2], self.project_coordinate(self.player.selected_ship.location),
                                            self.player.technology.get_ship_range(), self.view_scale)
        for p in self.game.players:
            for s in p.ships:
                if s.star is None and self.player.is_ship_visible(s):
                    # TODO: make ships only drawn if they are "visible" to the active player
                    # TODO: make ship pathing and movement affected by range
                    # TODO: make ships drawn overlapped, but as "ghosts", if in a star system,
                    #  from the galaxy perspective
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

    def draw(self, dest_surface, position=None):
        super().draw(dest_surface, position)
        #self.draw_fog(dest_surface, self.position)

    def handle_event(self, event, mouse_pos):
        super().handle_event(event, mouse_pos)
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == pygame.BUTTON_RIGHT:
                self.player.selected_ship.reset_task()
                if self.player.selected_ship.star is not None:
                    self.player.selected_ship.set_destination_star(None)
                clicked_star = self.find_star(self.get_relative_pane_pos(mouse_pos))
                if clicked_star is not None:
                    if clicked_star is self.player.selected_ship.star:
                        self.player.selected_ship.set_destination_star(None)
                    elif (self.player.selected_ship.get_distance_to(clicked_star.location)
                            < self.player.technology.get_ship_range()):
                        self.player.selected_ship.set_destination_star(clicked_star)
            elif event.button == pygame.BUTTON_LEFT:
                new_ship = self.find_player_ship(self.get_relative_pane_pos(mouse_pos))
                if new_ship is not None:
                    self.player.selected_ship = new_ship
                if self.num_clicks >= 2:
                    star = self.find_star(self.get_relative_pane_pos(mouse_pos))
                    if star is not None and self.player.explored_stars[star.id]:
                        self.next_pane_id = system_display.get_pane_id(star.id)
                    self.num_clicks = 0
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_PLUS:
                self.set_scale(min(drag_pane.ZOOM_MAX, self.view_scale + drag_pane.ZOOM_RATE), mouse_pos)
            elif event.key == pygame.K_MINUS:
                self.set_scale(max(drag_pane.ZOOM_MIN, self.view_scale - drag_pane.ZOOM_RATE), mouse_pos)
            # if event.key == pygame.K_LEFT:
            #     self.view_corner = (self.view_corner[0] + SCROLL_SPEED * self.dimensions[0] / self.view_scale,
            #                         self.view_corner[1])
            # elif event.key == pygame.K_RIGHT:
            #     self.view_corner = (self.view_corner[0] - SCROLL_SPEED * self.dimensions[0] / self.view_scale,
            #                         self.view_corner[1])
            # elif event.key == pygame.K_UP:
            #     self.view_corner = (self.view_corner[0],
            #                         self.view_corner[1] + SCROLL_SPEED * self.dimensions[1] / self.view_scale)
            # elif event.key == pygame.K_DOWN:
            #     self.view_corner = (self.view_corner[0],
            #                         self.view_corner[1] - SCROLL_SPEED * self.dimensions[1] / self.view_scale)

