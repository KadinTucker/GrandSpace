import math

import pygame
from matplotlib.backend_bases import MouseButton

import planet_display
import player as ply
import technology

import uiframe
import font
import macros

COLOR_MILESTONES = [(200, 50, 50), (150, 150, 0), (50, 200, 50), (0, 150, 150), (50, 50, 200), (150, 0, 150)]

MILESTONE_OFFSET = 29
MILESTONE_MAX = 121 / 5
MILESTONE_TOP = 156
MILESTONE_WIDTH = 20

DIPLOMACY_TEXT_OFFSET = 34

ACTION_ICONS = [
    (macros.ACTION_BUILD_CITY, uiframe.get_panel_from_image(macros.ICONS["build_city"])),
    (macros.ACTION_DEVELOP, uiframe.get_panel_from_image(macros.ICONS["develop"])),
    (macros.ACTION_COLONISE, uiframe.get_panel_from_image(macros.ICONS["colonise"])),
    (macros.ACTION_COLLECT_BIOMASS, uiframe.get_panel_from_image(macros.ICONS["collect_biomass"])),
    (macros.ACTION_TERRAFORM, uiframe.get_panel_from_image(macros.ICONS["terraform"])),
    (macros.ACTION_COLLECT, uiframe.get_panel_from_image(macros.ICONS["collect_minerals"])),
    (macros.ACTION_RESEARCH, uiframe.get_panel_from_image(macros.ICONS["science"])),
    (macros.ACTION_BIOLOGY, uiframe.get_panel_from_image(macros.ICONS["biology"])),
    (macros.ACTION_FUND_SCIENCE, uiframe.get_panel_from_image(macros.ICONS["fund_science"])),
    (macros.ACTION_SCHMOOZE, uiframe.get_panel_from_image(macros.ICONS["schmooze"])),
    (macros.ACTION_RAID_MINERALS, uiframe.get_panel_from_image(macros.ICONS["raid_minerals"])),
    (macros.ACTION_RAID_BIOMASS, uiframe.get_panel_from_image(macros.ICONS["raid_biomass"])),
    (macros.ACTION_BESIEGE, uiframe.get_panel_from_image(macros.ICONS["besiege"])),
]

def get_main_ui_container(player_obj, x, y, width, height):
    main_container = uiframe.UIContainer(None, x, y, width, height)
    background = uiframe.get_background_pane(main_container, 0, 0, width, height)
    main_container.elements.append(background)
    # main_container.add_element_left(MoneyPane(main_container, 0, 0, 8, player))
    main_container.add_element_left(CargoPane(main_container, 0, 0, player_obj))
    main_container.add_element_left(BiomassPane(main_container, 0, 0, player_obj))
    for action in ACTION_ICONS:
        main_container.add_element_left(ActionButton(main_container, action[1], 0, 0, player_obj, action[0]))
    return main_container

def make_top_bar_button(icon, ratio):
    surface = uiframe.get_blank_panel_surface(icon.get_width() * ratio, icon.get_height())
    surface.blit(icon, ((surface.get_width() - icon.get_width()) // 2, (surface.get_height() - icon.get_height()) // 2))
    return surface

def get_top_bar_container(window_container, player, x, y, width, height):
    top_bar_container = uiframe.UIContainer(None, x, y, width, height)
    top_bar_container.stagger_left = uiframe.FRAME_WIDTH
    background = uiframe.get_background_pane(top_bar_container, 0, 0, width, height)
    top_bar_container.elements.append(background)
    top_bar_container.add_element_left(MoneyPane(top_bar_container, 0, uiframe.FRAME_WIDTH, 8, player))
    # tech_surface = make_top_bar_button(macros.ICONS["science"], 4)
    # tech_button = MenuOpener(top_bar_container, tech_surface, 0, uiframe.FRAME_WIDTH, tech_surface.get_width(),
    #                          tech_surface.get_height(), window_container.elements[0])
    # top_bar_container.add_element_left(tech_button)
    science_indicator = ScienceIndicator(player, top_bar_container, 0, 0, window_container.elements[0])
    top_bar_container.add_element_left(science_indicator)
    return top_bar_container

class MilestoneFrame(uiframe.UIElement):

    def __init__(self, player, container, x, y):
        self.frame = pygame.image.load("assets/milestone-frame.png")
        self.frame.blit(macros.ICONS["battle"], (2 * uiframe.FRAME_WIDTH, 2 * uiframe.FRAME_WIDTH))
        self.frame.blit(macros.ICONS["discovery"], (2 * uiframe.FRAME_WIDTH + MILESTONE_OFFSET,
                                                    2 * uiframe.FRAME_WIDTH))
        self.frame.blit(macros.ICONS["ecology"], (2 * uiframe.FRAME_WIDTH + 2 * MILESTONE_OFFSET,
                                                  2 * uiframe.FRAME_WIDTH))
        self.frame.blit(macros.ICONS["diplomacy"], (2 * uiframe.FRAME_WIDTH + 3 * MILESTONE_OFFSET,
                                                    2 * uiframe.FRAME_WIDTH))
        self.frame.blit(macros.ICONS["trade"], (2 * uiframe.FRAME_WIDTH + 4 * MILESTONE_OFFSET,
                                                2 * uiframe.FRAME_WIDTH))
        self.frame.blit(macros.ICONS["empire"], (2 * uiframe.FRAME_WIDTH + 5 * MILESTONE_OFFSET,
                                                 2 * uiframe.FRAME_WIDTH))
        self.player = player
        super().__init__(container, None, x, y, self.frame.get_width(), self.frame.get_height())
        self.update()

    def update(self):
        self.surface = pygame.Surface((self.width, self.height))
        for i in range(6):
            milestone_height = int(MILESTONE_MAX
                                   * ply.get_milestone_from_progress(self.player.milestone_progress[i]))
            pygame.draw.rect(self.surface, COLOR_MILESTONES[i],
                             pygame.Rect(2 * uiframe.FRAME_WIDTH + MILESTONE_OFFSET * i,
                                         MILESTONE_TOP - milestone_height, MILESTONE_WIDTH, milestone_height))
        self.surface.blit(self.frame, (0, 0))

    def draw(self, dest_surface):
        self.update()
        super().draw(dest_surface)

class MenuOpener(uiframe.UIElement):

    def __init__(self, container, surface, x, y, width, height, menu_element):
        super().__init__(container, surface, x, y, width, height)
        self.menu_element = menu_element

    def handle_event(self, event, mouse_pos):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == pygame.BUTTON_LEFT:
                if self.is_point_in(mouse_pos):
                    self.menu_element.visible = not self.menu_element.visible

class DiplomacyFrame(MenuOpener):

    def __init__(self, player, container, x, y, menu_element):
        self.frame = pygame.image.load("assets/leverage-frame.png")
        self.player = player
        width = self.frame.get_width()
        height = self.frame.get_height() * (len(player.game.players) - 1)
        surface = pygame.Surface((width, height))
        surface.set_colorkey((0, 0, 0))
        super().__init__(container, surface, x, y, width, height, menu_element)
        self.update()

    def update(self):
        self.surface.fill((1, 1, 1))
        index = 0
        for p in self.player.game.players:
            if p is not self.player:
                y_value = self.frame.get_height() * index
                pygame.draw.rect(self.surface, self.player.color,
                                 pygame.Rect(0, y_value, self.frame.get_height(), self.frame.get_height()))
                pygame.draw.rect(self.surface, p.color, pygame.Rect(self.width - self.frame.get_height(), y_value,
                                                                    self.frame.get_height(), self.frame.get_height()))
                self.surface.blit(self.frame, (0, self.frame.get_height() * index))

                left_leverage = font.get_text_surface(
                    str(math.floor(self.player.game.diplomacy.leverage_matrix[self.player.id][p.id])))
                right_leverage = font.get_text_surface(
                    str(math.floor(self.player.game.diplomacy.leverage_matrix[p.id][self.player.id])))
                self.surface.blit(left_leverage, (DIPLOMACY_TEXT_OFFSET,
                                                  y_value + (self.frame.get_height() - left_leverage.get_height()) / 2))
                self.surface.blit(right_leverage, (self.width - DIPLOMACY_TEXT_OFFSET - right_leverage.get_width(),
                                                   y_value + (self.frame.get_height()
                                                              - right_leverage.get_height()) / 2))
                index += 1

    def draw(self, dest_surface):
        self.update()
        super().draw(dest_surface)

class ScienceIndicator(MenuOpener):
    def __init__(self, player, container, x, y, menu_element):
        width = 2 * uiframe.FRAME_WIDTH + 4 * 3 * font.LETTER_WIDTH
        height = container.height
        super().__init__(container, None, x, y, width, height, menu_element)
        self.player = player
        self.red_indicator = IndicatorIcon(container, macros.ICONS["science_red"], player,
                                           lambda p: int(p.technology.science[0]), uiframe.FRAME_WIDTH,
                                           uiframe.FRAME_WIDTH, 3)
        self.blue_indicator = IndicatorIcon(container, macros.ICONS["science_blue"], player,
                                            lambda p: int(p.technology.science[1]),
                                            uiframe.FRAME_WIDTH + 3 * font.LETTER_WIDTH, uiframe.FRAME_WIDTH, 3)
        self.green_indicator = IndicatorIcon(container, macros.ICONS["science_green"], player,
                                             lambda p: int(p.technology.science[2]),
                                             uiframe.FRAME_WIDTH + 6 * font.LETTER_WIDTH, uiframe.FRAME_WIDTH, 3)
        self.gold_indicator = IndicatorIcon(container, macros.ICONS["science"], player,
                                            lambda p: int(p.technology.science[3]),
                                            uiframe.FRAME_WIDTH + 9 * font.LETTER_WIDTH, uiframe.FRAME_WIDTH, 3)
        self.update()

    def update(self):
        self.surface = uiframe.get_blank_panel_surface(self.width - 2 * uiframe.FRAME_WIDTH,
                                                       self.height - 2 * uiframe.FRAME_WIDTH)
        self.red_indicator.update()
        self.blue_indicator.update()
        self.green_indicator.update()
        self.gold_indicator.update()
        self.surface.blit(self.red_indicator.surface, (self.red_indicator.x, self.red_indicator.y))
        self.surface.blit(self.blue_indicator.surface, (self.blue_indicator.x, self.blue_indicator.y))
        self.surface.blit(self.green_indicator.surface, (self.green_indicator.x, self.green_indicator.y))
        self.surface.blit(self.gold_indicator.surface, (self.gold_indicator.x, self.gold_indicator.y))

    def draw(self, dest_surface):
        self.update()
        super().draw(dest_surface)

class IndicatorIcon(uiframe.UIElement):

    def __init__(self, container, icon, player, indicator, x, y, max_text_width):
        width = max(icon.get_width(), max_text_width * font.LETTER_WIDTH)
        height = icon.get_height() + font.LETTER_HEIGHT
        surface = pygame.Surface((width, height))
        surface.set_colorkey((0, 0, 0))
        super().__init__(container, surface, x, y, width, height)
        self.icon = icon
        self.indicator = indicator
        self.player = player
        self.update()

    def update(self):
        self.surface.fill((0, 0, 0))
        self.surface.blit(self.icon, (0, 0))
        amount_surface = font.get_text_surface(str(self.indicator(self.player)))
        self.surface.blit(amount_surface, ((self.icon.get_width() - amount_surface.get_width()) / 2,
                                           self.icon.get_height()))

class ActionButton(uiframe.UIElement):

    def __init__(self, container, icon, x, y, player, action):
        super().__init__(container, icon, x, y, icon.get_width(), icon.get_height())
        self.player = player
        self.action = action

    # TODO: add a way to indicate if the ship can currently do the action or not
    def handle_event(self, event, mouse_pos):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == pygame.BUTTON_LEFT:
                if self.is_point_in(mouse_pos):
                    self.player.selected_ship.set_action(self.action)

class MoneyPane(uiframe.UIElement):

    def __init__(self, container, x, y, max_money_digits, player):
        width = (max_money_digits + 1) * font.LETTER_WIDTH + 2 * uiframe.FRAME_WIDTH
        height = font.LETTER_HEIGHT + 2 * uiframe.FRAME_WIDTH
        frame = uiframe.get_blank_panel_surface(width - 2 * uiframe.FRAME_WIDTH, height - 2 * uiframe.FRAME_WIDTH)
        super().__init__(container, frame, x, y, width, height)
        self.player = player
        self.money_surface = pygame.Surface((width - 2 * uiframe.FRAME_WIDTH, height - 2 * uiframe.FRAME_WIDTH))

    def update(self):
        self.money_surface.fill((0, 0, 0))
        money_text = font.get_text_surface("$" + str(self.player.money))
        self.money_surface.blit(money_text, (self.money_surface.get_width() - money_text.get_width(), 0))
        self.surface.blit(self.money_surface, (uiframe.FRAME_WIDTH, uiframe.FRAME_WIDTH))

    def draw(self, dest_surface):
        self.update()
        super().draw(dest_surface)

class BiomassPane(uiframe.UIElement):

    def __init__(self, container, x, y, player):
        self.value_indicator = IndicatorIcon(container, uiframe.get_panel_from_image(macros.ICONS["ecology"]),
                                             player, lambda p: p.selected_ship.cargo.biomass.value,
                                             uiframe.FRAME_WIDTH, uiframe.FRAME_WIDTH, 3)
        width = self.value_indicator.width + 5 + 26 * (font.LETTER_WIDTH + 2) + 2 * uiframe.FRAME_WIDTH
        height = self.value_indicator.height + 2 * uiframe.FRAME_WIDTH
        super().__init__(container, None, x, y, width, height)
        self.player = player
        self.update()

    def get_biomass_letter_x(self, offset):
        return self.value_indicator.width + uiframe.FRAME_WIDTH + offset * (font.LETTER_WIDTH + 2)

    def get_biomass_letter_from_x(self, x):
        return int((x - self.value_indicator.width - uiframe.FRAME_WIDTH) / (font.LETTER_WIDTH + 2))

    def draw(self, dest_surface):
        self.update()
        super().draw(dest_surface)

    def update(self):
        self.surface = uiframe.get_blank_panel_surface(self.width - 2 * uiframe.FRAME_WIDTH,
                                                       self.height - 2 * uiframe.FRAME_WIDTH)
        self.value_indicator.update()
        self.surface.blit(self.value_indicator.surface, (self.value_indicator.x, self.value_indicator.y))

        biomasses = 0
        for i in range(len(self.player.selected_ship.cargo.biomass.quantities)):
            if self.player.selected_ship.cargo.biomass.quantities[i] > 0:
                biomass_amount = font.get_text_surface(str(self.player.selected_ship.cargo.biomass.quantities[i]))
                self.surface.blit(biomass_amount, (self.get_biomass_letter_x(biomasses),
                                                   uiframe.FRAME_WIDTH + self.value_indicator.height
                                                   - font.LETTER_HEIGHT))
                if self.player.selected_ship.cargo.biomass.selected == i:
                    pygame.draw.rect(self.surface, (160, 200, 120),
                                     pygame.Rect(self.get_biomass_letter_x(biomasses) - 2, uiframe.FRAME_WIDTH,
                                                 font.LETTER_WIDTH + 2 * 2, font.LETTER_HEIGHT + 2 * 2))
                    pygame.draw.rect(self.surface, (30, 10, 10),
                                     pygame.Rect(self.get_biomass_letter_x(biomasses) - 2, uiframe.FRAME_WIDTH,
                                                 font.LETTER_WIDTH + 2 * 4, font.LETTER_HEIGHT + 2 * 4), 2)
                    pygame.draw.rect(self.surface, (200, 10, 10),
                                     pygame.Rect(self.get_biomass_letter_x(biomasses),
                                                 uiframe.FRAME_WIDTH + self.value_indicator.height
                                                 - font.LETTER_HEIGHT,
                                                 font.LETTER_WIDTH, font.LETTER_HEIGHT), 1)
                else:
                    pygame.draw.rect(self.surface, (50, 15, 15),
                                     pygame.Rect(self.get_biomass_letter_x(biomasses) - 2, uiframe.FRAME_WIDTH,
                                                 font.LETTER_WIDTH + 2 * 2, font.LETTER_HEIGHT + 2 * 2))
                self.surface.blit(planet_display.ECOLOGY_SPECIES_IMAGES[i],
                                  (self.get_biomass_letter_x(biomasses), uiframe.FRAME_WIDTH + 2))
                biomasses += 1

    def handle_event(self, event, mouse_pos):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == pygame.BUTTON_LEFT:
                letter = self.get_biomass_letter_from_x(mouse_pos[0] - self.container.x - self.x) + 1
                if 0 <= letter < 26:
                    biomasses = 0
                    for i in range(len(self.player.selected_ship.cargo.biomass.quantities)):
                        if self.player.selected_ship.cargo.biomass.quantities[i] > 0:
                            biomasses += 1
                            if biomasses == letter:
                                if i == self.player.selected_ship.cargo.biomass.selected:
                                    self.player.selected_ship.cargo.biomass.select(-1)
                                else:
                                    self.player.selected_ship.cargo.biomass.select(i)
                                self.update()
                                break

class CargoPane(uiframe.UIElement):

    def __init__(self, container, x, y, player_obj):
        width = (2 * uiframe.FRAME_WIDTH + 1.5 * (2 * uiframe.FRAME_WIDTH + macros.ICONS["discovery"].get_width())
                 + 1.5 * (2 * uiframe.FRAME_WIDTH + macros.ICONS["empire"].get_width())
                 + 6 * (2 * uiframe.FRAME_WIDTH + macros.ICONS["mineral_r"].get_width()))
        height = 4 * uiframe.FRAME_WIDTH + macros.ICONS["discovery"].get_height() + font.LETTER_HEIGHT
        super().__init__(container, None, x, y, width, height)
        self.player = player_obj
        self.artifact_icon = uiframe.get_panel_from_image(macros.ICONS["discovery"])
        self.sell_artifact_icon = uiframe.get_panel_from_image(macros.ICONS["sell_artifact"])
        self.building_icon = uiframe.get_panel_from_image(macros.ICONS["empire"])
        self.mineral_icons = [uiframe.get_panel_from_image(macros.ICONS["mineral_" + x]) for x in "rgbcmy"]
        self.sell_mineral_icons = [uiframe.get_panel_from_image(macros.ICONS["sell_mineral_" + x]) for x in "rgbcmy"]
        self.artifact_pos = 0
        self.building_pos = 0
        self.mineral_pos = [0 for _ in range(6)]
        self.update()

    def draw_amount_with_icon(self, icon, amount, x):
        self.surface.blit(icon, (uiframe.FRAME_WIDTH + x, uiframe.FRAME_WIDTH))
        amount_surface = font.get_text_surface(str(amount))
        self.surface.blit(amount_surface, (uiframe.FRAME_WIDTH + x + (icon.get_width() - amount_surface.get_width()) / 2,
                                           uiframe.FRAME_WIDTH + icon.get_height()))

    def handle_event(self, event, mouse_pos):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == pygame.BUTTON_LEFT:
                rel_mouse = (mouse_pos[0] - self.container.x - self.x, mouse_pos[1] - self.container.y - self.y)
                if 0 <= rel_mouse[1] <= self.artifact_icon.get_height():
                    if 0 <= rel_mouse[0] - self.artifact_pos <= self.artifact_icon.get_width():
                        self.player.selected_ship.set_action(macros.ACTION_SELL_ARTIFACT)
                    elif 0 <= rel_mouse[0] - self.building_pos <= self.building_icon.get_width():
                        self.player.selected_ship.set_action(macros.ACTION_BUY_BUILDING)
                    else:
                        for i in range(len(self.mineral_pos)):
                            if 0 <= rel_mouse[0] - self.mineral_pos[i] <= self.mineral_icons[i].get_width():
                                self.player.selected_ship.set_action(macros.ACTION_SELL_RED + i)
                                break

    def update(self):
        self.surface = uiframe.get_blank_panel_surface(self.width - 2 * uiframe.FRAME_WIDTH,
                                                       self.height - 2 * uiframe.FRAME_WIDTH)
        stagger = 0
        self.artifact_pos = stagger
        artifact_icon = self.artifact_icon
        if (self.player.selected_ship.cargo.artifacts > 0 and self.player.selected_ship.planet is not None
                and self.player.selected_ship.planet.colony is not None
                and self.player.selected_ship.planet.colony.ruler is self.player):
            artifact_icon = self.sell_artifact_icon
        self.draw_amount_with_icon(artifact_icon, self.player.selected_ship.cargo.artifacts, stagger)
        stagger += artifact_icon.get_width() * 1.5
        self.building_pos = stagger
        self.draw_amount_with_icon(self.building_icon, self.player.selected_ship.cargo.buildings, stagger)
        stagger += self.artifact_icon.get_width() * 1.5
        for i in range(6):
            self.mineral_pos[i] = stagger
            mineral_icon = self.mineral_icons[i]
            if (self.player.selected_ship.cargo.minerals[i] > 0 and self.player.selected_ship.planet is not None
                    and self.player.selected_ship.planet.colony is not None
                    and self.player.game.diplomacy.get_active_access(self.player.selected_ship.planet.star.ruler.id,
                                                                     self.player.id, 2)):
                mineral_icon = self.sell_mineral_icons[i]
            self.draw_amount_with_icon(mineral_icon, self.player.selected_ship.cargo.minerals[i], stagger)
            stagger += mineral_icon.get_width()

    def draw(self, dest_surface):
        self.update()
        super().draw(dest_surface)

