import pygame
import sys

import ecology
import galaxy
import macros
import player

import font
import ship_tasks
import ui_diplomacy
import ui_main
import uiframe
import ui_technology

import galaxy_display
import planet_display
import system_display
import drag_pane

MAX_FPS = 90

DISPLAY_DIMENSIONS = (1300, 700)

GALAXY_WIDTH = 14
GALAXY_HEIGHT = 10
GALAXY_ZONE_RADIUS = 40
GALAXY_STAR_RADIUS = 12
GALAXY_PLANET_RADIUS = 3
GALAXY_MARGIN = 20

GALAXY_SPACE_WIDTH = GALAXY_ZONE_RADIUS * GALAXY_WIDTH + GALAXY_MARGIN
GALAXY_SPACE_HEIGHT = int(GALAXY_ZONE_RADIUS * GALAXY_HEIGHT * 0.86 + GALAXY_MARGIN)

GALAXY_PANE_MARGIN = 177
SYSTEM_PANE_MARGIN = 177

SYSTEM_PANE_DIMENSIONS = (DISPLAY_DIMENSIONS[0] - SYSTEM_PANE_MARGIN * 2, DISPLAY_DIMENSIONS[1] - 58)
SYSTEM_PANE_POSITION = ((DISPLAY_DIMENSIONS[0] - SYSTEM_PANE_DIMENSIONS[0]) // 2,
                        (DISPLAY_DIMENSIONS[1] - SYSTEM_PANE_DIMENSIONS[1] - 58) // 2)
GALAXY_PANE_DIMENSIONS = (DISPLAY_DIMENSIONS[0] - GALAXY_PANE_MARGIN * 2, DISPLAY_DIMENSIONS[1] - 58)
GALAXY_PANE_POSITION = ((DISPLAY_DIMENSIONS[0] - GALAXY_PANE_DIMENSIONS[0]) // 2,
                        (DISPLAY_DIMENSIONS[1] - GALAXY_PANE_DIMENSIONS[1] - 58) // 2)

TOP_BAR_HEIGHT = 44
MAIN_PANE_HEIGHT = 60

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
        new_display.set_scale(drag_pane.ZOOM_MAX, p.homeworld.star.location)
        galaxy_displays.append(new_display)
    return galaxy_displays
            
def generate_player_system_displays(game, player_obj):
    return [system_display.SystemDisplay(game, player_obj, SYSTEM_PANE_DIMENSIONS,
                                         SYSTEM_PANE_POSITION, s) for s in game.galaxy.stars]

def generate_all_system_displays(game):
    return [generate_player_system_displays(game, p) for p in game.players]

def get_pane_mouse_pos(pane_location):
    mouse = pygame.mouse.get_pos()
    return mouse[0] - pane_location[0], mouse[1] - pane_location[1]

def generate_ui_elements(player_obj):
    window_container = uiframe.UIContainer(None, 177, TOP_BAR_HEIGHT, DISPLAY_DIMENSIONS[0] - 177,
                                           DISPLAY_DIMENSIONS[1] - TOP_BAR_HEIGHT - MAIN_PANE_HEIGHT)
    window_container.elements.append(ui_technology.TechPane(window_container, 0, 2 * uiframe.FRAME_WIDTH))
    window_container.elements.append(ui_diplomacy.DiplomacyPane(window_container, player_obj,
                                                                0, 2 * uiframe.FRAME_WIDTH))

    for element in window_container.elements:
        element.visible = False

    main_ui = ui_main.get_main_ui_container(player_obj, 0, DISPLAY_DIMENSIONS[1] - MAIN_PANE_HEIGHT,
                                            DISPLAY_DIMENSIONS[0], MAIN_PANE_HEIGHT)

    top_bar = ui_main.get_top_bar_container(window_container, player_obj, 0, 0,
                                            DISPLAY_DIMENSIONS[0], TOP_BAR_HEIGHT)
    milestones = ui_main.MilestoneFrame(player_obj, None, 0, TOP_BAR_HEIGHT)
    diplomacy_pane = ui_main.DiplomacyFrame(player_obj, None, 0, TOP_BAR_HEIGHT + milestones.height,
                                            window_container.elements[1])
    return [main_ui, top_bar, milestones, diplomacy_pane, window_container]

def main():

    galaxy_obj = galaxy.Galaxy(galaxy.generate_galaxy_boxes(GALAXY_WIDTH, GALAXY_HEIGHT, GALAXY_ZONE_RADIUS))
    game = player.Game(5, galaxy_obj)
    galaxy_obj.generate_star_distance_matrix()
    galaxy_obj.generate_star_distance_hierarchy()
    galaxy_obj.populate_homeworlds(game)
    galaxy_obj.populate_life(game)
    galaxy_obj.populate_artifacts()

    # artifact_spawner = galaxy.ArtifactSpawner(galaxy_obj)

    active_player = game.players[0]
    active_player.selected_ship = active_player.ships[0]

    timescale = 1.5

    if len(sys.argv) > 1 and sys.argv[1] == 'cheat':
        print("*** CHEAT MODE ACTIVATED ***")
        for p in game.players:
            for t in range(len(p.technology.tech_level)):
                p.technology.tech_level[t] = [5, 5, 2]
        ecology.BIOMASS_REGENERATION_PER_MINUTE = 15.0
        for i in range(1, len(game.players)):
            import random
            game.diplomacy.lose_leverage(0, i, random.randint(0, 100))
            game.diplomacy.gain_leverage(0, i, random.randint(0, 100))
            game.diplomacy.lose_leverage(i, 0, random.randint(0, 100))
            game.diplomacy.gain_leverage(i, 0, random.randint(0, 100))
        #   game.diplomacy.gain_leverage(0, i, 100)

    pygame.init()

    display = pygame.display.set_mode(DISPLAY_DIMENSIONS)
    pygame.display.set_icon(pygame.image.load("assets/app.png"))
    pygame.display.set_caption("Grand Space")

    clock = pygame.time.Clock()

    system_displays = generate_all_system_displays(game)
    galaxy_displays = generate_galaxy_displays(game)
    player_uis = [generate_ui_elements(p) for p in game.players]

    active_display = system_displays[active_player.id][active_player.homeworld.star.id]
    active_display.update()

    timestamp = pygame.time.get_ticks()

    while True:

        # Calculate Tick Time
        elapsed_time = float(pygame.time.get_ticks() - timestamp) * timescale / 60000
        timestamp = pygame.time.get_ticks()

        # Events
        for event in pygame.event.get():
            active_display.handle_event(event, pygame.mouse.get_pos())
            for uie in player_uis[active_player.id]:
                uie.handle_event(event, pygame.mouse.get_pos())
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            # Handle ship selection events
            # TODO: include in ship-specific event handling
            elif event.type == pygame.KEYDOWN:
                # TEMP: change active player
                if event.key == pygame.K_TAB:
                    active_player = game.players[(active_player.id + 1) % len(game.players)]
                    active_display = galaxy_displays[active_player.id]
                # TEMP: spawn ship
                elif event.key == pygame.K_s:
                    active_player.add_ship(active_player.homeworld)
                if event.key in macros.ACTION_KEYCONTROL_DICT.keys():
                    active_player.selected_ship.set_action(macros.ACTION_KEYCONTROL_DICT[event.key])

        if active_display.next_pane_id != -1:
            next_id = active_display.next_pane_id
            active_display.next_pane_id = -1
            if next_id == 0:
                active_display = galaxy_displays[active_player.id]
            else:
                active_display = system_displays[active_player.id][next_id - 1]

        # Game Mechanics
        # Player loop
        for p in game.players:
            for s in p.ships:
                s.act(elapsed_time)
                if p == active_player:
                    galaxy_displays[active_player.id].refresh_layer(0)
                    galaxy_displays[active_player.id].refresh_layer(1)
            p.milestone_progress[3] = game.diplomacy.get_milestone_state(p.id)
        # Galaxy loop
        # artifact_spawner.try_place_artifact(elapsed_time)
        for s in galaxy_obj.stars:
            for p in s.planets:
                p.ecology.regenerate_biomass(elapsed_time)
                if p.colony is not None:
                    p.colony.demand.progress_demand(elapsed_time)
                    p.colony.do_tick(elapsed_time)

        # Display

        display.fill(active_player.color)
        active_display.refresh_layer(len(active_display.layers) - 1)  # refresh top layer every tick
        if isinstance(active_display, system_display.SystemDisplay):
            active_display.refresh_layer(1)
            active_display.refresh_layer(2)
        active_display.draw(display)
        if elapsed_time > 0:
            display.blit(font.get_text_surface(str(int(1 / (elapsed_time / timescale * 60)))), (0, 0))

        for uie in player_uis[active_player.id]:
            uie.draw(display)

        # Update; end tick
        pygame.display.update()
        clock.tick(MAX_FPS)


if __name__ == "__main__":
    main()
