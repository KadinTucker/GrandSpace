import pygame
from pygame.locals import *
import sys
import math

import galaxy
import player
import ship

import font
import uiframe

import system_display

GALAXY_WIDTH = 14
GALAXY_HEIGHT = 10
GALAXY_ZONE_RADIUS = 40
GALAXY_STAR_RADIUS = 12
GALAXY_PLANET_RADIUS = 3
GALAXY_MARGIN = 50

GALAXY_SPACE_WIDTH = GALAXY_ZONE_RADIUS * GALAXY_WIDTH + GALAXY_MARGIN
GALAXY_SPACE_HEIGHT = int(GALAXY_ZONE_RADIUS * GALAXY_HEIGHT * 0.86 + GALAXY_MARGIN)

SYSTEM_PANE_POSITION = ((2 * GALAXY_SPACE_WIDTH - system_display.SYSTEM_SURFACE_WIDTH) // 2, (2 * GALAXY_SPACE_HEIGHT - system_display.SYSTEM_SURFACE_HEIGHT) // 2)
print(SYSTEM_PANE_POSITION)

COLOR_BACKGROUND = (10, 10, 10)
COLOR_UNEXPLORED_STAR = (135, 135, 135)
COLOR_STAR = (200, 170, 25)
COLOR_ARTIFACT_RING = (150, 125, 35)
COLOR_SHIP_SELECTION = (225, 225, 225)

img_ufo = pygame.image.load("ufo.png")

def draw_galaxy(surface, g, player):
    for i in range(len(g.stars)):
        s = g.stars[i]
        star_color = COLOR_UNEXPLORED_STAR
        if player.explored_stars[i]:
            if s.ruler != None:
                pygame.draw.circle(surface, s.ruler.color, s.location, int(1.5 * GALAXY_STAR_RADIUS))
            star_color = COLOR_STAR
        pygame.draw.circle(surface, star_color, s.location, GALAXY_STAR_RADIUS)
        # pygame.draw.circle(surface, (255, 255, 255), s.location, radii, 1)
        numPlanets = len(s.planets)
        for p in range(numPlanets):
            angle = p * 2 * math.pi / numPlanets
            planetCenter = (int(s.location[0] + GALAXY_STAR_RADIUS * math.cos(angle)), int(s.location[1] + GALAXY_STAR_RADIUS * math.sin(angle)))
            pygame.draw.circle(surface, galaxy.MINERAL_COLORS[s.planets[p].mineral], planetCenter, GALAXY_PLANET_RADIUS)

# def draw_system(surface, star):
#     #ship_at = ship_selection.star == star
#     surface.fill(COLOR_BACKGROUND)
#     pygame.draw.circle(surface, COLOR_STAR, (GALAXY_SPACE_WIDTH, GALAXY_SPACE_HEIGHT), SYSTEM_STAR_RADIUS)
#     num_planets = len(star.planets)
#     for p in range(num_planets):
#         angle = p * 2 * math.pi / num_planets - math.pi / 2
#         planet_center = (int(GALAXY_SPACE_WIDTH + SYSTEM_HORIZONTAL_AXIS * math.cos(angle)), int(GALAXY_SPACE_HEIGHT + SYSTEM_VERTICAL_AXIS * math.sin(angle)))
#         draw_planet(surface, star.planets[p], planet_center)
#         # if ship_at and ship_selection.planet == star.planets[p]:
#         #     draw_ship(surface, ship_selection, planetCenter, True)
#         #     ship_at = False
#     # if ship_at:
#     #     draw_ship(surface, ship_selection, (GALAXY_SPACE_WIDTH, GALAXY_SPACE_HEIGHT), True)
#     #     ship_at = False
#     for s in range(len(star.ships)):
#         if star.ships[s].planet == None:
#             angle = s * 2 * math.pi / len(star.ships) - math.pi / 2
#             radius = 15 * (len(star.ships) - 1)
#             draw_ship(surface, star.ships[s], (int(GALAXY_SPACE_WIDTH + radius * math.cos(angle)), int(GALAXY_SPACE_HEIGHT + radius * math.sin(angle))))
            
# def draw_planet(surface, planet, position):
#     if planet.colony != None:
#         pygame.draw.circle(surface, planet.colony.ruler.color, position, int(1.5 * SYSTEM_PLANET_RADIUS))
#     pygame.draw.circle(surface, galaxy.MINERAL_COLORS[planet.mineral], position, SYSTEM_PLANET_RADIUS)
#     if planet.artifacts > 0:
#         #pygame.draw.circle(surface, (150, 125, 35), planetCenter, 17, 3)
#         pygame.draw.circle(surface, COLOR_ARTIFACT_RING, position, SYSTEM_PLANET_RADIUS + SYSTEM_ARTIFACT_RING_WIDTH * 2, SYSTEM_ARTIFACT_RING_WIDTH)
#         pygame.draw.circle(surface, COLOR_ARTIFACT_RING, position, SYSTEM_PLANET_RADIUS + SYSTEM_ARTIFACT_RING_WIDTH * 4, SYSTEM_ARTIFACT_RING_WIDTH)
#     for s in range(len(planet.ships)):
#         angle = s * 2 * math.pi / len(planet.ships) - math.pi / 2
#         radius = 10 * (len(planet.ships) - 1)
#         draw_ship(surface, planet.ships[s], (int(position[0] + radius * math.cos(angle)), int(position[1] + radius * math.sin(angle))))
            
def generate_system_displays(galaxy):
    system_displays = []
    for s in galaxy.stars:
        system_displays.append(system_display.SystemDisplay(s))
    return system_displays

# def get_system_planet_location(planet_id, num_planets):
#     angle = planet_id * 2 * math.pi / num_planets - math.pi / 2
#     return (int(GALAXY_SPACE_WIDTH + SYSTEM_HORIZONTAL_AXIS * math.cos(angle)), int(GALAXY_SPACE_HEIGHT + SYSTEM_VERTICAL_AXIS * math.sin(angle)))

def draw_location_ships(surface, position, ship_list):
    for s in range(len(ship_list)):
        angle = s * 2 * math.pi / len(ship_list) - math.pi / 2
        radius = 10 * (len(ship_list) - 1)
        draw_ship(surface, ship_list[s], (int(position[0] + radius * math.cos(angle)), int(position[1] + radius * math.sin(angle))))

def draw_ship(display, ship_obj, position):
    if ship_obj.selected:
        pygame.draw.circle(display, COLOR_SHIP_SELECTION, position, 12)
    pygame.draw.circle(display, ship_obj.ruler.color, position, 8)
    display.blit(img_ufo, (position[0] - 10, position[1] - 10))

def find_star(position, galaxy):
    for s in galaxy.stars:
        if math.hypot(s.location[0] - position[0], s.location[1] - position[1]) <= GALAXY_STAR_RADIUS:
            return s
    return None

# def find_planet(position, star):
#     for p in range(len(star.planets)):
#         angle = p * 2 * math.pi / len(star.planets) - math.pi / 2
#         planetCenter = (int(GALAXY_SPACE_WIDTH + SYSTEM_HORIZONTAL_AXIS * math.cos(angle)), int(GALAXY_SPACE_HEIGHT + SYSTEM_VERTICAL_AXIS * math.sin(angle)))
#         if math.hypot(planetCenter[0] - position[0], planetCenter[1] - position[1]) <= SYSTEM_PLANET_RADIUS:
#             return star.planets[p]
#     return None

def find_ship_galaxy(position, game):
    for p in game.players:
        for s in p.ships:
            if math.hypot(s.location[0] - position[0], s.location[1] - position[1]) <= 10:
                return s
    return None

def find_ship_system(position, star):
    pass #TODO

"""
Display Modes:
0 - null
1 - Galaxy
2 - System
3 - Planet(?)
"""
"""
Queries:
0 - null
1 - Destination Star
2 - Destination Planet
"""



def main():

    display_mode = 1
    active_query = 0

    g = galaxy.Galaxy()
    game = player.Game(5, g)
    galaxy.generateGalaxyBoxes(g, GALAXY_WIDTH, GALAXY_HEIGHT, GALAXY_ZONE_RADIUS)
    galaxy.populate_homeworlds(g, game)
    galaxy.populate_artifacts(g)

    active_player = game.players[0]
    #ship_selection = ship.Ship((200, 100), active_player)
    ship_selection = active_player.ships[0]
    ship_selection.selected = True

    star = None

    doubleclick = 0

    pygame.init()

    display = pygame.display.set_mode((GALAXY_SPACE_WIDTH * 2, GALAXY_SPACE_HEIGHT * 2))

    system_displays = generate_system_displays(g)

    text_explore = font.get_text_surface("explore")
    text_colonise = font.get_text_surface("colonise")

    panel_small = uiframe.get_panel_surface(20, 20)
    panel_large = uiframe.get_panel_surface(GALAXY_SPACE_WIDTH * 2 - 6, 52)
    panel_money = uiframe.get_panel_surface(108, 16)

    button_diplomacy = uiframe.create_button("icon-diplomacy.png")
    button_colonial = uiframe.create_button("icon-colonial.png")
    button_research = uiframe.create_button("icon-research.png")
    button_explore = uiframe.create_button("icon-explore.png")
    button_battle = uiframe.create_button("icon-battle.png")
    button_ecology = uiframe.create_button("icon-ecology.png")

    timestamp = pygame.time.get_ticks()

    while True:

        # Calculate Tick Time
        elapsed_time = float(pygame.time.get_ticks() - timestamp) / 60000
        timestamp = pygame.time.get_ticks()

        # Events
        for event in pygame.event.get():
            if event.type == pygame.QUIT: #QUIT
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN: #MOUSEBUTTONDOWN

                if event.button == pygame.BUTTON_RIGHT: # RIGHT MOUSE BUTTON
                    if display_mode == 1:
                        ship_selection.exit_star()
                        ship_selection.destination_star = find_star(pygame.mouse.get_pos(), g)
                        if ship_selection.destination_star != None:
                            ship_selection.destination = ship_selection.destination_star.location
                    elif display_mode == 2 and ship_selection.star == star:
                        mouse_pos = pygame.mouse.get_pos()
                        relative_mouse_pos = (mouse_pos[0] - SYSTEM_PANE_POSITION[0], mouse_pos[1] - SYSTEM_PANE_POSITION[1])
                        ship_selection.destination_planet = system_displays[star.id].find_planet(relative_mouse_pos)
                        if system_displays[star.id].is_star_clicked(relative_mouse_pos):
                            if ship_selection.planet == None:
                                ship_selection.exit_star()
                            ship_selection.exit_planet()

                elif event.button == pygame.BUTTON_LEFT: # LEFT MOUSE BUTTON
                    if active_query == 0:
                        doubleclick += 1
                        new_ship = find_ship_galaxy(pygame.mouse.get_pos(), game)
                        if new_ship != None:
                            ship_selection.selected = False
                            new_ship.selected = True
                            ship_selection = new_ship
                            active_player = ship_selection.ruler
                    # elif active_query == 1:
                    #     star = find_star(pygame.mouse.get_pos(), g)
                    #     if star != None and active_player.explored_stars[star.id]:
                    #         active_query = 2
                    #         display_mode = 2
                    # elif active_query == 2:
                    #     planet = find_planet(pygame.mouse.get_pos(), star)
                    #     if planet != None:
                    #         ship_selection.destination_planet = planet
                    #         ship_selection.destination_star = star
                    #         ship_selection.destination = star.location
                    #         active_query = 0
                    #         display_mode = 1

            elif event.type == pygame.MOUSEMOTION: #MOUSEMOTION
                doubleclick = 0
            elif event.type == pygame.KEYDOWN: #KEYDOWN
                #print(event.key)
                if event.key == pygame.K_ESCAPE: #ESC 
                    active_query = 0 
                    display_mode = 1
                # elif event.key == 101: #E
                #     active_query = 1
                #     display_mode = 1

        if doubleclick >= 2:
            star = find_star(pygame.mouse.get_pos(), g)
            if star != None and active_player.explored_stars[star.id]:
                display_mode = 2
            doubleclick = 0

        # Game Mechanics
        for p in game.players:
            for s in p.ships:
                s.move(elapsed_time)

        # Display

        display.fill(COLOR_BACKGROUND)

        # GALAXY DISPLAY
        if display_mode == 1:
            
            display.fill(COLOR_BACKGROUND)
            draw_galaxy(display, g, active_player)
            for p in game.players:
                for s in p.ships:
                    if s.star == None:
                        draw_ship(display, s, (int(s.location[0]), int(s.location[1])))
                    elif s.selected:
                        pygame.draw.circle(display, COLOR_SHIP_SELECTION, s.star.location, GALAXY_STAR_RADIUS + 2, 2)

        # SYSTEM DISPLAY
        elif display_mode == 2:
            if star != None:
                system_displays[star.id].refresh_ship_surface()
                system_displays[star.id].draw(display, SYSTEM_PANE_POSITION)
            else:
                display_mode = 1

        if active_query == 1 or active_query == 2:
            display.blit(text_colonise, (GALAXY_SPACE_WIDTH * 2 - GALAXY_MARGIN - 150, GALAXY_SPACE_HEIGHT * 1.72 - GALAXY_MARGIN - 20))
            #display.blit(text_colonise, (0, 0))

        # display.blit(panel_large, (0, GALAXY_SPACE_HEIGHT * 2 - 58))
        # display.blit(button_diplomacy, (GALAXY_SPACE_WIDTH * 2 - 29, GALAXY_SPACE_HEIGHT * 2 - 55))
        # display.blit(button_ecology, (GALAXY_SPACE_WIDTH * 2 - 29, GALAXY_SPACE_HEIGHT * 2 - 29))
        # display.blit(button_explore, (GALAXY_SPACE_WIDTH * 2 - 55, GALAXY_SPACE_HEIGHT * 2 - 55))
        # display.blit(button_research, (GALAXY_SPACE_WIDTH * 2 - 55, GALAXY_SPACE_HEIGHT * 2 - 29))
        # display.blit(button_battle, (GALAXY_SPACE_WIDTH * 2 - 81, GALAXY_SPACE_HEIGHT * 2 - 55))
        # display.blit(button_colonial, (GALAXY_SPACE_WIDTH * 2 - 81, GALAXY_SPACE_HEIGHT * 2 - 29))
        # money = font.get_text_surface("$" + str(active_player.money))
        # display.blit(panel_money, (3, GALAXY_SPACE_HEIGHT * 2 - 40))
        # display.blit(money, (6, GALAXY_SPACE_HEIGHT * 2 - 37))
        # Update; end tick
        pygame.display.update()

if __name__ == "__main__":
    main()