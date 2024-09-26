import pygame
import sys

import colony
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
        new_display = galaxy_display.GalaxyDisplay(game, p, GALAXY_PANE_DIMENSIONS, GALAXY_PANE_DIMENSIONS,
                                                            GALAXY_PANE_POSITION)
        new_display.set_scale(3.0, p.homeworld.star.location)
        galaxy_displays.append(new_display)
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

    g = galaxy.Galaxy()
    game = player.Game(5, g)
    galaxy.generate_galaxy_boxes(g, GALAXY_WIDTH, GALAXY_HEIGHT, GALAXY_ZONE_RADIUS)
    galaxy.populate_homeworlds(g, game)
    galaxy.populate_artifacts(g)

    active_player = game.players[0]
    ship_selection = active_player.ships[0]
    active_player.selected_ship = ship_selection

    pygame.init()

    display = pygame.display.set_mode(DISPLAY_DIMENSIONS)

    system_displays = generate_system_displays(game, active_player)
    galaxy_displays = generate_galaxy_displays(game)

    active_display = galaxy_displays[active_player.id]
    active_display.refresh_all_layers()

    text_explore = font.get_text_surface("explore")
    text_colonise = font.get_text_surface("colonise")

    panel_small = uiframe.get_panel_surface(20, 20)
    panel_large = uiframe.get_panel_surface(DISPLAY_DIMENSIONS[0] - 6, 52)
    panel_wide = uiframe.get_panel_surface(156, 26)
    panel_money = uiframe.get_panel_surface(108, 16)

    icon_mineral_r = uiframe.create_button("assets/minerals-red.png")
    icon_mineral_g = uiframe.create_button("assets/minerals-green.png")
    icon_mineral_b = uiframe.create_button("assets/minerals-blue.png")
    icon_mineral_c = uiframe.create_button("assets/minerals-cyan.png")
    icon_mineral_m = uiframe.create_button("assets/minerals-magenta.png")
    icon_mineral_y = uiframe.create_button("assets/minerals-yellow.png")

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
            active_display.handle_event(event, pygame.mouse.get_pos())
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            # Handle ship selection events
            # TODO: include in ship-specific event handling
            elif event.type == pygame.KEYDOWN:
                # TEMP: conquer active ship's star
                if event.key == pygame.K_c:
                    if active_player.selected_ship.planet is not None:
                        new_colony = colony.Colony(active_player, active_player.selected_ship.planet)
                        active_player.selected_ship.planet.colony = new_colony
                        active_player.colonies.append(new_colony)
                        active_player.add_ruled_star(active_player.selected_ship.star)
                        galaxy_displays[active_player.id].refresh_layer(0)
                        system_displays[active_player.selected_ship.planet.star.id].refresh_layer(1)
                        system_displays[active_player.selected_ship.planet.star.id].refresh_layer(2)
                # TEMP: auto explore
                elif event.key == pygame.K_e:
                    active_player.selected_ship.task = 1
                # TEMP: collect biomass
                elif event.key == pygame.K_b:
                    if active_player.selected_ship.planet is not None:
                        active_player.selected_ship.collect_biomass(active_player.selected_ship.planet.ecology)

        if active_display.next_pane_id != -1:
            next_id = active_display.next_pane_id
            active_display.next_pane_id = -1
            if next_id == 0:
                active_display = galaxy_displays[active_player.id]
            else:
                active_display = system_displays[next_id - 1]

        # Game Mechanics
        # Player loop
        for p in game.players:
            for s in p.ships:
                s.do_task()
                s.move(elapsed_time)
                if p == active_player:
                    galaxy_displays[active_player.id].refresh_layer(0)
                    galaxy_displays[active_player.id].refresh_layer(1)
        # Galaxy loop
        for s in g.stars:
            for p in s.planets:
                p.ecology.regenerate_biomass(elapsed_time)
                if p.colony is not None:
                    p.colony.demand.progress_demand(elapsed_time)
                    p.colony.produce(elapsed_time)

        # Display

        display.fill(COLOR_BACKGROUND)
        active_display.refresh_layer(len(active_display.layers) - 1)  # refresh top layer every tick
        if isinstance(active_display, system_display.SystemDisplay):
            active_display.refresh_layer(3)  # refresh ecology layer every tick, because it has moving bars
        active_display.draw(display)

        # TEMP: manually drawing all UI elements

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

        display.blit(button_explore, (175, DISPLAY_DIMENSIONS[1] - 52))
        amt_artifact = font.get_text_surface(str(active_player.selected_ship.cargo.artifacts))
        display.blit(amt_artifact, (182, DISPLAY_DIMENSIONS[1] - 22))

        display.blit(panel_wide, (226, DISPLAY_DIMENSIONS[1] - 55))
        display.blit(icon_mineral_r, (229, DISPLAY_DIMENSIONS[1] - 52))
        amt_r = font.get_text_surface(str(active_player.selected_ship.cargo.minerals[0]))
        display.blit(amt_r, (236, DISPLAY_DIMENSIONS[1] - 22))
        display.blit(icon_mineral_g, (255, DISPLAY_DIMENSIONS[1] - 52))
        amt_g = font.get_text_surface(str(active_player.selected_ship.cargo.minerals[1]))
        display.blit(amt_g, (262, DISPLAY_DIMENSIONS[1] - 22))
        display.blit(icon_mineral_b, (281, DISPLAY_DIMENSIONS[1] - 52))
        amt_b = font.get_text_surface(str(active_player.selected_ship.cargo.minerals[2]))
        display.blit(amt_b, (288, DISPLAY_DIMENSIONS[1] - 22))
        display.blit(icon_mineral_c, (307, DISPLAY_DIMENSIONS[1] - 52))
        amt_c = font.get_text_surface(str(active_player.selected_ship.cargo.minerals[3]))
        display.blit(amt_c, (314, DISPLAY_DIMENSIONS[1] - 22))
        display.blit(icon_mineral_m, (333, DISPLAY_DIMENSIONS[1] - 52))
        amt_m = font.get_text_surface(str(active_player.selected_ship.cargo.minerals[4]))
        display.blit(amt_m, (340, DISPLAY_DIMENSIONS[1] - 22))
        display.blit(icon_mineral_y, (359, DISPLAY_DIMENSIONS[1] - 52))
        amt_y = font.get_text_surface(str(active_player.selected_ship.cargo.minerals[5]))
        display.blit(amt_y, (366, DISPLAY_DIMENSIONS[1] - 22))

        display.blit(button_colonial, (425, DISPLAY_DIMENSIONS[1] - 52))
        amt_building = font.get_text_surface(str(active_player.selected_ship.cargo.buildings))
        display.blit(amt_building, (432, DISPLAY_DIMENSIONS[1] - 22))

        display.blit(button_ecology, (475, DISPLAY_DIMENSIONS[1] - 52))
        biomasses = 0
        for i in range(len(active_player.selected_ship.cargo.biomass.quantities)):
            if active_player.selected_ship.cargo.biomass.quantities[i] > 0:
                pygame.draw.rect(display, (50, 15, 15),
                                 pygame.Rect(504 + biomasses * 14, DISPLAY_DIMENSIONS[1] - 49, 16, 18))
                display.blit(system_display.ECOLOGY_SPECIES_IMAGES[i],
                             (506 + biomasses * 14, DISPLAY_DIMENSIONS[1] - 48))
                biomass_amount = font.get_text_surface(str(active_player.selected_ship.cargo.biomass.quantities[i]))
                display.blit(biomass_amount,(506 + biomasses * 14, DISPLAY_DIMENSIONS[1] - 22))
                biomasses += 1

        # Update; end tick
        pygame.display.update()


if __name__ == "__main__":
    main()
