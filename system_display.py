import pygame
import math

import galaxy
import ship_tasks

import pane
import planet_display
import ship_display

SYSTEM_STAR_RADIUS = 60
SYSTEM_PLANET_RADIUS = 20
SYSTEM_HORIZONTAL_AXIS = 300
SYSTEM_VERTICAL_AXIS = 150
SYSTEM_ARTIFACT_RING_WIDTH = 2
SYSTEM_COLONY_RADIUS = 30

SYSTEM_SURFACE_WIDTH = 2 * SYSTEM_HORIZONTAL_AXIS + 4 * SYSTEM_PLANET_RADIUS + 2
SYSTEM_SURFACE_HEIGHT = 2 * SYSTEM_VERTICAL_AXIS + 4 * SYSTEM_PLANET_RADIUS + 2

SYSTEM_SHIP_RADIUS = 10

ACCESS_PANE_HEIGHT = 46
ACCESS_PANE_WIDTH = 96
ACCESS_ELEMENT_POSITIONS = [(0, 0), (24, 0), (48, 0), (72, 13), (48, 26), (24, 26), (0, 26)]

ACCESS_IMAGE_FILENAMES = ["assets/icon-ecology.png", "assets/icon-diplomacy.png", "assets/icon-trade.png",
                          "assets/icon-access-passage.png", "assets/icon-access-piracy.png", "assets/icon-battle.png",
                          "assets/icon-access-siege.png"]

ACCESS_IMAGES = [pygame.image.load(fn) for fn in ACCESS_IMAGE_FILENAMES]
ACCESS_NONE_IMG = pygame.image.load("assets/no-access.png")

COLOR_BACKGROUND = (10, 10, 10)
COLOR_STAR = (200, 130, 25)
COLOR_ARTIFACT_RING = (150, 125, 35)
COLOR_SHIP_SELECTION = (225, 225, 225)
COLOR_BIOMASS_EMPTY = (95, 35, 15)
COLOR_BIOMASS_FULL = (25, 110, 15)
COLOR_BIOMASS_HALO = (110, 220, 110)
COLOR_DEMAND_PROGRESS = (180, 180, 180)
COLOR_ACCESS_PANE = (120, 80, 120)

def get_pane_id(star_id):
    return star_id + 1

class SystemDisplay(pane.Pane):

    def __init__(self, game, player, pane_dimensions, pane_position, star):
        super().__init__(game, player, pane_dimensions, pane_position, 4, COLOR_BACKGROUND)
        self.star = star
        self.planet_locations = []
        self.set_planet_locations()
        self.projectile_anim_progress = 0  # TEMP
        self.planet_displays = [planet_display.PlanetDisplay(game, player, p) for p in self.star.planets]
        self.update()

    def set_planet_locations(self):
        # Relative to the system pane's pasted location
        self.planet_locations = []
        num_planets = len(self.star.planets)
        for p in range(num_planets):
            angle = p * 2 * math.pi / num_planets - math.pi / 2
            self.planet_locations.append((int(self.dimensions[0] / 2 + SYSTEM_HORIZONTAL_AXIS * math.cos(angle)),
                                          int(self.dimensions[1] / 2 + SYSTEM_VERTICAL_AXIS * math.sin(angle))))

    def sketch_primary_surface(self):
        self.layers[0].fill(COLOR_BACKGROUND)
        pygame.draw.circle(self.layers[0], COLOR_STAR,
                           (self.dimensions[0] // 2, self.dimensions[1] // 2), SYSTEM_STAR_RADIUS)
        for p in range(len(self.star.planets)):
            pygame.draw.circle(self.layers[0], galaxy.MINERAL_COLORS[self.star.planets[p].mineral],
                               self.planet_locations[p], SYSTEM_PLANET_RADIUS)

    def sketch_player_surface(self):
        self.layers[1].fill(COLOR_BACKGROUND)
        for p in range(len(self.star.planets)):
            if self.star.planets[p].colony is not None:
                pygame.draw.circle(self.layers[1], self.star.planets[p].colony.ruler.color, self.planet_locations[p],
                                   SYSTEM_COLONY_RADIUS, SYSTEM_COLONY_RADIUS - SYSTEM_PLANET_RADIUS + 1)
        # Access
        if self.star.ruler is not None:
            pane_left = (self.dimensions[0] - ACCESS_PANE_WIDTH) // 2
            pane_up = (self.dimensions[1] - ACCESS_PANE_HEIGHT) // 2
            pygame.draw.rect(self.layers[1], self.star.ruler.color,
                             pygame.Rect(pane_left, pane_up, ACCESS_PANE_WIDTH, ACCESS_PANE_HEIGHT))
            for i in range(len(ACCESS_ELEMENT_POSITIONS)):
                self.layers[1].blit(ACCESS_IMAGES[i], (pane_left + ACCESS_ELEMENT_POSITIONS[i][0],
                                                       pane_up + ACCESS_ELEMENT_POSITIONS[i][1]))
                if not self.game.diplomacy.access_matrix[self.star.ruler.id][self.player.id][i]:
                    self.layers[1].blit(ACCESS_NONE_IMG, (pane_left + ACCESS_ELEMENT_POSITIONS[i][0],
                                                          pane_up + ACCESS_ELEMENT_POSITIONS[i][1]))

    def sketch_ship_surface(self):
        self.layers[3].fill(COLOR_BACKGROUND)
        all_ships = []
        all_ship_positions = []
        star_ships = []
        for s in self.star.ships:
            if s.planet is None:
                star_ships.append(s)
        all_ships += star_ships
        all_ship_positions += ship_display.draw_overlapping_ships(self.layers[3], star_ships,
                                            (self.dimensions[0] // 2, self.dimensions[1] // 2),
                                            self.player)
        for p in range(len(self.star.planets)):
            all_ships += self.star.planets[p].ships
            all_ship_positions += ship_display.draw_overlapping_ships(self.layers[3], self.star.planets[p].ships,
                                                                      self.planet_locations[p], self.player)
        for i in range(len(all_ships)):
            for j in range(len(all_ships)):
                if ship_tasks.is_enemy_ship(all_ships[i], all_ships[j]):
                    ship_display.draw_ship_projectile(self.layers[3], all_ship_positions[i], all_ship_positions[j],
                                                      self.projectile_anim_progress
                                                      / ship_display.SHIP_PROJECTILE_FRAMES)
                    break
        self.projectile_anim_progress += 1
        self.projectile_anim_progress %= ship_display.SHIP_PROJECTILE_FRAMES

    def sketch_planet_detail_surface(self):
        self.layers[2].fill(COLOR_BACKGROUND)
        for p in range(len(self.star.planets)):
            # TODO: Only make planet display update when it is visible to the player,
            #   with both in-game meaning of having a ship/colony there, and if the layer is drawn
            self.planet_displays[p].update()
            self.planet_displays[p].draw(self.layers[2], self.planet_locations[p])

    def refresh_layer(self, index):
        super().refresh_layer(index)
        if index == 0:
            self.sketch_primary_surface()
        elif index == 1:
            self.sketch_player_surface()
        elif index == 2:
            self.sketch_planet_detail_surface()
        elif index == 3:
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
        return math.hypot(self.dimensions[0] / 2 - position[0],
                          self.dimensions[1] / 2 - position[1]) <= SYSTEM_STAR_RADIUS

    def handle_event(self, event, mouse_pos):
        super().handle_event(event, mouse_pos)
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == pygame.BUTTON_RIGHT:
                self.player.selected_ship.reset_task()
                if (self.player.selected_ship.get_distance_to(self.star.location)
                        < self.player.technology.get_ship_range()):
                    if self.is_star_clicked(self.get_relative_pane_pos(mouse_pos)):
                        if self.player.selected_ship.star is not self.star:
                            self.player.selected_ship.set_destination_star(self.star)
                        elif self.player.selected_ship.planet is None:
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
        star_ship = ship_display.find_overlapped_ship((self.dimensions[0] // 2,
                                                       self.dimensions[1] // 2), all_star_ships,
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
