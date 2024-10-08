import pygame
import sys

import ecology
import galaxy
import macros
import player

import font
import ship_tasks
import uiframe
import ui_technology

import galaxy_display
import planet_display
import system_display

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

GALAXY_PANE_MARGIN = 75
SYSTEM_PANE_MARGIN = 75

SYSTEM_PANE_DIMENSIONS = (DISPLAY_DIMENSIONS[0] - SYSTEM_PANE_MARGIN * 2, DISPLAY_DIMENSIONS[1] - 58)
SYSTEM_PANE_POSITION = ((DISPLAY_DIMENSIONS[0] - SYSTEM_PANE_DIMENSIONS[0]) // 2,
                        (DISPLAY_DIMENSIONS[1] - SYSTEM_PANE_DIMENSIONS[1] - 58) // 2)
GALAXY_PANE_DIMENSIONS = (DISPLAY_DIMENSIONS[0] - GALAXY_PANE_MARGIN * 2, DISPLAY_DIMENSIONS[1] - 58)
GALAXY_PANE_POSITION = ((DISPLAY_DIMENSIONS[0] - GALAXY_PANE_DIMENSIONS[0]) // 2,
                        (DISPLAY_DIMENSIONS[1] - GALAXY_PANE_DIMENSIONS[1] - 58) // 2)

COLOR_BACKGROUND = (50, 50, 50)
COLOR_UNEXPLORED_STAR = (135, 135, 135)
COLOR_STAR = (200, 170, 25)
COLOR_ARTIFACT_RING = (150, 125, 35)
COLOR_SHIP_SELECTION = (225, 225, 225)
COLOR_MILESTONES = [(200, 50, 50), (150, 150, 0), (50, 200, 50), (0, 150, 150), (50, 50, 200), (150, 0, 150)]

def generate_galaxy_displays(game):
    galaxy_displays = []
    for p in game.players:
        new_display = galaxy_display.GalaxyDisplay(game, p, GALAXY_PANE_DIMENSIONS, GALAXY_PANE_DIMENSIONS,
                                                   GALAXY_PANE_POSITION)
        new_display.set_scale(3.0, p.homeworld.star.location)
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

def main():

    galaxy_obj = galaxy.Galaxy(galaxy.generate_galaxy_boxes(GALAXY_WIDTH, GALAXY_HEIGHT, GALAXY_ZONE_RADIUS))
    game = player.Game(5, galaxy_obj)
    galaxy_obj.generate_star_distance_matrix()
    galaxy_obj.generate_star_distance_hierarchy()
    galaxy_obj.populate_homeworlds(game)
    galaxy_obj.populate_life(game)

    artifact_spawner = galaxy.ArtifactSpawner(galaxy_obj)

    active_player = game.players[0]
    active_player.selected_ship = active_player.ships[0]

    timescale = 1.5

    if len(sys.argv) > 1 and sys.argv[1] == 'cheat':
        print("*** CHEAT MODE ACTIVATED ***")
        for p in game.players:
            for t in range(len(p.technology.tech_level)):
                p.technology.tech_level[t] = [5, 5, 2]
        ecology.BIOMASS_REGENERATION_PER_MINUTE = 15.0

    pygame.init()

    display = pygame.display.set_mode(DISPLAY_DIMENSIONS)
    pygame.display.set_icon(pygame.image.load("assets/app.png"))
    pygame.display.set_caption("Grand Space")

    clock = pygame.time.Clock()

    system_displays = generate_all_system_displays(game)
    galaxy_displays = generate_galaxy_displays(game)

    active_display = galaxy_displays[active_player.id]
    active_display.update()

    milestone_frame = pygame.image.load("assets/milestone-frame.png")

    panel_large = uiframe.get_panel_surface(DISPLAY_DIMENSIONS[0] - 6, 52)
    panel_wide = uiframe.get_panel_surface(156, 26)
    panel_money = uiframe.get_panel_surface(108, 16)

    icon_mineral_r = uiframe.create_button_surface(pygame.image.load("assets/minerals-red.png"))
    icon_mineral_g = uiframe.create_button_surface(pygame.image.load("assets/minerals-green.png"))
    icon_mineral_b = uiframe.create_button_surface(pygame.image.load("assets/minerals-blue.png"))
    icon_mineral_c = uiframe.create_button_surface(pygame.image.load("assets/minerals-cyan.png"))
    icon_mineral_m = uiframe.create_button_surface(pygame.image.load("assets/minerals-magenta.png"))
    icon_mineral_y = uiframe.create_button_surface(pygame.image.load("assets/minerals-yellow.png"))

    icon_diplomacy = pygame.image.load("assets/icon-diplomacy.png")
    icon_empire = pygame.image.load("assets/icon-colonial.png")
    icon_discovery = pygame.image.load("assets/icon-explore.png")
    icon_trade = pygame.image.load("assets/icon-trade.png")
    icon_battle = pygame.image.load("assets/icon-battle.png")
    icon_ecology = pygame.image.load("assets/icon-ecology.png")

    button_diplomacy = uiframe.create_button_surface(pygame.image.load("assets/icon-diplomacy.png"))
    button_colonial = uiframe.create_button_surface(pygame.image.load("assets/icon-colonial.png"))
    button_research = uiframe.create_button_surface(pygame.image.load("assets/icon-research.png"))
    button_explore = uiframe.create_button_surface(pygame.image.load("assets/icon-explore.png"))
    button_battle = uiframe.create_button_surface(pygame.image.load("assets/icon-battle.png"))
    button_ecology = uiframe.create_button_surface(pygame.image.load("assets/icon-ecology.png"))

    ui_container = uiframe.UIContainer(DISPLAY_DIMENSIONS)
    #ui_container.elements.append(uiframe.Draggable(ui_container, milestone_frame, 500, 500, 177, 165))
    ui_container.elements.append(ui_technology.TechPane(ui_container, 300, 300))

    timestamp = pygame.time.get_ticks()

    while True:

        # Calculate Tick Time
        elapsed_time = float(pygame.time.get_ticks() - timestamp) * timescale / 60000
        timestamp = pygame.time.get_ticks()

        # Events
        for event in pygame.event.get():
            active_display.handle_event(event, pygame.mouse.get_pos())
            for element in ui_container.elements:
                element.handle_event(event, pygame.mouse.get_pos())
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

            elif event.type == pygame.MOUSEBUTTONDOWN:
                # TODO: Include in modular uiframe input handler
                if event.button == pygame.BUTTON_LEFT:
                    mouse_pos = pygame.mouse.get_pos()
                    if DISPLAY_DIMENSIONS[1] - 49 < mouse_pos[1] < DISPLAY_DIMENSIONS[1] - 31:
                        biomass_index = (mouse_pos[0] - 504) // 14 + 1
                        if 0 <= biomass_index < 26:
                            biomasses = 0
                            for i in range(len(active_player.selected_ship.cargo.biomass.quantities)):
                                if active_player.selected_ship.cargo.biomass.quantities[i] > 0:
                                    biomasses += 1
                                    if biomasses == biomass_index:
                                        if i == active_player.selected_ship.cargo.biomass.selected:
                                            active_player.selected_ship.cargo.biomass.select(-1)
                                        else:
                                            active_player.selected_ship.cargo.biomass.select(i)
                                        break
                    if DISPLAY_DIMENSIONS[1] - 52 < mouse_pos[1] < DISPLAY_DIMENSIONS[1] - 26:
                        if 175 < mouse_pos[0] < 201:
                            active_player.selected_ship.set_action(14)
                        elif 229 < mouse_pos[0] < 386:
                            if ship_tasks.is_at_colony(active_player.selected_ship):
                                mineral_num = (mouse_pos[0] - 229) // 26
                                assert 0 <= mineral_num < 6
                                active_player.selected_ship.set_action(8 + mineral_num)
                        elif 425 < mouse_pos[0] < 451:
                            active_player.selected_ship.set_action(15)

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
        artifact_spawner.try_place_artifact(elapsed_time)
        for s in galaxy_obj.stars:
            for p in s.planets:
                p.ecology.regenerate_biomass(elapsed_time)
                if p.colony is not None:
                    p.colony.demand.progress_demand(elapsed_time)
                    p.colony.produce(elapsed_time)

        # Display

        display.fill(active_player.color)
        active_display.refresh_layer(len(active_display.layers) - 1)  # refresh top layer every tick
        if isinstance(active_display, system_display.SystemDisplay):
            active_display.refresh_layer(1)
            active_display.refresh_layer(2)
        active_display.draw(display)
        if elapsed_time > 0:
            display.blit(font.get_text_surface(str(int(1 / (elapsed_time / timescale * 60)))), (0, 0))

        # TEMP: manually drawing all UI elements

        for element in ui_container.elements:
            element.draw(display)

        for i in range(len(active_player.milestone_progress)):
            height = int(121 * player.get_milestone_from_progress(active_player.milestone_progress[i]) / 5)
            pygame.draw.rect(display, COLOR_MILESTONES[i],
                             pygame.Rect(GALAXY_PANE_POSITION[0] + 6 + 29 * i, 156 - height, 20, height))

        display.blit(milestone_frame, (GALAXY_PANE_POSITION[0], 0))

        display.blit(icon_battle, (GALAXY_PANE_POSITION[0] + 6, 6))
        display.blit(icon_discovery, (GALAXY_PANE_POSITION[0] + 35, 6))
        display.blit(icon_ecology, (GALAXY_PANE_POSITION[0] + 64, 6))
        display.blit(icon_diplomacy, (GALAXY_PANE_POSITION[0] + 93, 6))
        display.blit(icon_trade, (GALAXY_PANE_POSITION[0] + 122, 6))
        display.blit(icon_empire, (GALAXY_PANE_POSITION[0] + 151, 6))

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
        value_biomass = font.get_text_surface(str(active_player.selected_ship.cargo.biomass.value))
        display.blit(value_biomass, (476, DISPLAY_DIMENSIONS[1] - 26))
        biomasses = 0
        for i in range(len(active_player.selected_ship.cargo.biomass.quantities)):
            if active_player.selected_ship.cargo.biomass.quantities[i] > 0:
                biomass_amount = font.get_text_surface(str(active_player.selected_ship.cargo.biomass.quantities[i]))
                display.blit(biomass_amount, (506 + biomasses * 14, DISPLAY_DIMENSIONS[1] - 22))
                if active_player.selected_ship.cargo.biomass.selected == i:
                    pygame.draw.rect(display, (160, 200, 120),
                                     pygame.Rect(504 + biomasses * 14 - 2, DISPLAY_DIMENSIONS[1] - 49 - 2, 20, 22))
                    pygame.draw.rect(display, (30, 10, 10),
                                     pygame.Rect(504 + biomasses * 14 - 2, DISPLAY_DIMENSIONS[1] - 49 - 2, 20, 22), 2)
                    pygame.draw.rect(display, (200, 10, 10),
                                     pygame.Rect(506 + biomasses * 14, DISPLAY_DIMENSIONS[1] - 22, 12, 16), 2)
                else:
                    pygame.draw.rect(display, (50, 15, 15),
                                     pygame.Rect(504 + biomasses * 14, DISPLAY_DIMENSIONS[1] - 49, 16, 18))
                display.blit(planet_display.ECOLOGY_SPECIES_IMAGES[i],
                             (506 + biomasses * 14, DISPLAY_DIMENSIONS[1] - 48))
                biomasses += 1

        # Update; end tick
        pygame.display.update()
        clock.tick(MAX_FPS)


if __name__ == "__main__":
    main()
