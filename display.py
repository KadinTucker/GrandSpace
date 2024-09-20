import pygame
import sys

import galaxy
import player

import font
import uiframe

import galaxy_display
import system_display

DISPLAY_DIMENSIONS = (1300, 600)

GALAXY_WIDTH = 14
GALAXY_HEIGHT = 10
GALAXY_ZONE_RADIUS = 40
GALAXY_STAR_RADIUS = 12
GALAXY_PLANET_RADIUS = 3
GALAXY_MARGIN = 20

GALAXY_SPACE_WIDTH = GALAXY_ZONE_RADIUS * GALAXY_WIDTH + GALAXY_MARGIN
GALAXY_SPACE_HEIGHT = int(GALAXY_ZONE_RADIUS * GALAXY_HEIGHT * 0.86 + GALAXY_MARGIN)

SYSTEM_PANE_DIMENSIONS = (2 * GALAXY_SPACE_WIDTH, 2 * GALAXY_SPACE_HEIGHT)
SYSTEM_PANE_POSITION = ((DISPLAY_DIMENSIONS[0] - SYSTEM_PANE_DIMENSIONS[0]) // 2,
                        (DISPLAY_DIMENSIONS[1] - SYSTEM_PANE_DIMENSIONS[1] - 58) // 2)
GALAXY_PANE_DIMENSIONS = (2 * GALAXY_SPACE_WIDTH, 2 * GALAXY_SPACE_HEIGHT)
GALAXY_PANE_POSITION = ((DISPLAY_DIMENSIONS[0] - GALAXY_PANE_DIMENSIONS[0]) // 2,
                        (DISPLAY_DIMENSIONS[1] - GALAXY_PANE_DIMENSIONS[1] - 58) // 2)

COLOR_BACKGROUND = (50, 50, 50)
COLOR_UNEXPLORED_STAR = (135, 135, 135)
COLOR_STAR = (200, 170, 25)
COLOR_ARTIFACT_RING = (150, 125, 35)
COLOR_SHIP_SELECTION = (225, 225, 225)

def generate_galaxy_displays(game):
    galaxy_displays = []
    for p in game.players:
        galaxy_displays.append(galaxy_display.GalaxyDisplay(game, p, GALAXY_PANE_DIMENSIONS, GALAXY_PANE_DIMENSIONS,
                                                            GALAXY_PANE_POSITION))
    return galaxy_displays
            
def generate_system_displays(game, active_player):
    system_displays = []
    for s in game.galaxy.stars:
        system_displays.append(system_display.SystemDisplay(game, active_player, SYSTEM_PANE_DIMENSIONS,
                                                            SYSTEM_PANE_POSITION, s))
    return system_displays

def get_pane_mouse_pos(pane_location):
    mouse = pygame.mouse.get_pos()
    return mouse[0] - pane_location[0], mouse[1] - pane_location[1]


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

    g = galaxy.Galaxy()
    game = player.Game(5, g)
    galaxy.generate_galaxy_boxes(g, GALAXY_WIDTH, GALAXY_HEIGHT, GALAXY_ZONE_RADIUS)
    galaxy.populate_homeworlds(g, game)
    galaxy.populate_artifacts(g)

    active_player = game.players[0]
    ship_selection = active_player.ships[0]
    active_player.selected_ship = ship_selection

    # TEMP
    for _ in range(9):
        active_player.add_ship(active_player.colonies[0].planet)

    star = None

    doubleclick = 0

    pygame.init()

    display = pygame.display.set_mode(DISPLAY_DIMENSIONS)

    system_displays = generate_system_displays(game, active_player)
    galaxy_displays = generate_galaxy_displays(game)

    active_display = galaxy_displays[active_player.id]

    text_explore = font.get_text_surface("explore")
    text_colonise = font.get_text_surface("colonise")

    panel_small = uiframe.get_panel_surface(20, 20)
    panel_large = uiframe.get_panel_surface(DISPLAY_DIMENSIONS[0] - 6, 52)
    panel_money = uiframe.get_panel_surface(108, 16)

    button_diplomacy = uiframe.create_button("assets/icon-diplomacy.png")
    button_colonial = uiframe.create_button("assets/icon-colonial.png")
    button_research = uiframe.create_button("assets/icon-research.png")
    button_explore = uiframe.create_button("assets/icon-explore.png")
    button_battle = uiframe.create_button("assets/icon-battle.png")
    button_ecology = uiframe.create_button("assets/icon-ecology.png")

    timestamp = pygame.time.get_ticks()

    while True:

        # Calculate Tick Time
        elapsed_time = float(pygame.time.get_ticks() - timestamp) / 60000
        timestamp = pygame.time.get_ticks()

        # Events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            
            active_display.handle_event(event, pygame.mouse.get_pos(), active_player)

            if event.type == pygame.MOUSEBUTTONDOWN:

                if event.button == pygame.BUTTON_RIGHT:
                    if display_mode == 2:
                        ship_selection.set_destination_planet((system_displays[star.id]
                                                              .find_planet(get_pane_mouse_pos(SYSTEM_PANE_POSITION))))
                        if system_displays[star.id].is_star_clicked(get_pane_mouse_pos(SYSTEM_PANE_POSITION)):
                            if ship_selection.planet is None:
                                ship_selection.exit_star()
                            ship_selection.exit_planet()
                        print(ship_selection.star)
                        print(ship_selection.planet)

                elif event.button == pygame.BUTTON_LEFT:
                    doubleclick += 1
                    if display_mode == 2:
                        new_ship = system_displays[star.id].find_ship(get_pane_mouse_pos(SYSTEM_PANE_POSITION))
                        if new_ship is not None:
                            ship_selection = new_ship
                            active_player = ship_selection.ruler
                            active_player.selected_ship = ship_selection
                            galaxy_displays[active_player.id].refresh_layer(1)
                            galaxy_displays[active_player.id].refresh_layer(0)

            elif event.type == pygame.MOUSEMOTION:
                doubleclick = 0

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    active_query = 0 
                    display_mode = 1
                elif event.key == pygame.K_PLUS:
                    if display_mode == 1:
                        galaxy_displays[active_player.id].set_scale(galaxy_displays[active_player.id].view_scale * 1.5,
                                                                    get_pane_mouse_pos(GALAXY_PANE_POSITION))
                elif event.key == pygame.K_MINUS:
                    if display_mode == 1:
                        galaxy_displays[active_player.id].set_scale(galaxy_displays[active_player.id].view_scale / 1.5,
                                                                    get_pane_mouse_pos(GALAXY_PANE_POSITION))
                # TEMP
                elif event.key == pygame.K_c:
                    if star is not None:
                        active_player.add_ruled_star(star)
                        galaxy_displays[active_player.id].refresh_layer(0)
                # TEMP
                elif event.key == pygame.K_e:
                    ship_selection.task = 1

        if doubleclick >= 2:
            star = galaxy_displays[active_player.id].find_star(get_pane_mouse_pos(GALAXY_PANE_POSITION))
            if star is not None and active_player.explored_stars[star.id]:
                system_displays[star.id].refresh_all_layers()
                display_mode = 2
            doubleclick = 0

        # Game Mechanics
        for p in game.players:
            for s in p.ships:
                s.do_task()
                moved, entered = s.move(elapsed_time)
                if p == active_player and entered:
                    galaxy_displays[active_player.id].refresh_layer(0)
                    galaxy_displays[active_player.id].refresh_layer(1)

        # Display

        display.fill(COLOR_BACKGROUND)

        # GALAXY DISPLAY
        if display_mode == 1:
            active_display.refresh_layer(2)
            active_display.draw(display)

        # SYSTEM DISPLAY
        elif display_mode == 2:
            if star is not None:
                system_displays[star.id].sketch_ship_surface()
                system_displays[star.id].draw(display)
            else:
                display_mode = 1

        display.blit(panel_large, (0, DISPLAY_DIMENSIONS[1] - 58))
        display.blit(button_diplomacy, (DISPLAY_DIMENSIONS[0] - 29, DISPLAY_DIMENSIONS[1] - 55))
        display.blit(button_ecology, (DISPLAY_DIMENSIONS[0] - 29, DISPLAY_DIMENSIONS[1] - 29))
        display.blit(button_explore, (DISPLAY_DIMENSIONS[0] - 55, DISPLAY_DIMENSIONS[1] - 55))
        display.blit(button_research, (DISPLAY_DIMENSIONS[0] - 55, DISPLAY_DIMENSIONS[1] - 29))
        display.blit(button_battle, (DISPLAY_DIMENSIONS[0] - 81, DISPLAY_DIMENSIONS[1] - 55))
        display.blit(button_colonial, (DISPLAY_DIMENSIONS[0] - 81, DISPLAY_DIMENSIONS[1] - 29))
        money = font.get_text_surface("$" + str(active_player.money))
        display.blit(panel_money, (3, DISPLAY_DIMENSIONS[1] - 40))
        display.blit(money, (6, DISPLAY_DIMENSIONS[1] - 37))
        # Update; end tick
        pygame.display.update()


if __name__ == "__main__":
    main()
