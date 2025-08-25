import pygame

import planet_display
import technology

import uiframe
import font
import macros

def get_background_pane(container, x, y, width, height):
    panel_large = uiframe.get_blank_panel_surface(width - 2 * uiframe.FRAME_WIDTH,
                                                  height - 2 * uiframe.FRAME_WIDTH)
    return uiframe.UIElement(container, panel_large, x, y, width, height)

def get_main_ui_container(player, x, y, width, height):
    main_container = uiframe.UIContainer((width, height))
    background = get_background_pane(main_container, x, y, width, height)
    stagger = 0
    money_pane = MoneyPane(main_container, x + uiframe.FRAME_WIDTH + stagger,
                           y + uiframe.FRAME_WIDTH, 8, player)
    stagger += money_pane.width
    cargo_pane = CargoPane(main_container, x + uiframe.FRAME_WIDTH + stagger,
                           y + uiframe.FRAME_WIDTH, player)
    stagger += cargo_pane.width
    biomass_pane = BiomassPane(main_container, x + uiframe.FRAME_WIDTH + stagger,
                               y + uiframe.FRAME_WIDTH, player)
    stagger += biomass_pane.width
    main_container.elements = [background, money_pane, cargo_pane, biomass_pane]
    return main_container

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
        width = 4 * uiframe.FRAME_WIDTH + macros.ICONS["ecology"].get_width() + 5 + 26 * (font.LETTER_WIDTH + 2)
        height = 4 * uiframe.FRAME_WIDTH + macros.ICONS["ecology"].get_height() + font.LETTER_HEIGHT
        super().__init__(container, None, x, y, width, height)
        self.player = player
        self.ecology_icon = uiframe.get_panel_from_image(macros.ICONS["ecology"])
        self.update()

    def get_biomass_letter_x(self, offset):
        return 2 * uiframe.FRAME_WIDTH + self.ecology_icon.get_width() + offset * (font.LETTER_WIDTH + 2)

    def draw(self, dest_surface):
        self.update()
        super().draw(dest_surface)

    def update(self):
        self.surface = uiframe.get_blank_panel_surface(self.width - 2 * uiframe.FRAME_WIDTH,
                                                       self.height - 2 * uiframe.FRAME_WIDTH)
        value_biomass = font.get_text_surface(str(self.player.selected_ship.cargo.biomass.value))
        self.surface.blit(self.ecology_icon, (uiframe.FRAME_WIDTH, uiframe.FRAME_WIDTH))
        self.surface.blit(value_biomass,
                          (uiframe.FRAME_WIDTH + (self.ecology_icon.get_width() - value_biomass.get_width()) / 2,
                           uiframe.FRAME_WIDTH + self.ecology_icon.get_height()))
        biomasses = 0
        for i in range(len(self.player.selected_ship.cargo.biomass.quantities)):
            if self.player.selected_ship.cargo.biomass.quantities[i] > 0:
                biomass_amount = font.get_text_surface(str(self.player.selected_ship.cargo.biomass.quantities[i]))
                self.surface.blit(biomass_amount, (self.get_biomass_letter_x(biomasses),
                                                   uiframe.FRAME_WIDTH + self.ecology_icon.get_height()))
                if self.player.selected_ship.cargo.biomass.selected == i:
                    pygame.draw.rect(self.surface, (160, 200, 120),
                                     pygame.Rect(self.get_biomass_letter_x(biomasses) - 2, uiframe.FRAME_WIDTH,
                                                 font.LETTER_WIDTH + 2 * 2, font.LETTER_HEIGHT + 2 * 2))
                    pygame.draw.rect(self.surface, (30, 10, 10),
                                     pygame.Rect(self.get_biomass_letter_x(biomasses) - 2, uiframe.FRAME_WIDTH,
                                                 font.LETTER_WIDTH + 2 * 4, font.LETTER_HEIGHT + 2 * 4), 2)
                    pygame.draw.rect(self.surface, (200, 10, 10),
                                     pygame.Rect(self.get_biomass_letter_x(biomasses),
                                                 uiframe.FRAME_WIDTH + self.ecology_icon.get_height(),
                                                 font.LETTER_WIDTH, font.LETTER_HEIGHT), 1)
                else:
                    pygame.draw.rect(self.surface, (50, 15, 15),
                                     pygame.Rect(self.get_biomass_letter_x(biomasses) - 2, uiframe.FRAME_WIDTH,
                                                 font.LETTER_WIDTH + 2 * 2, font.LETTER_HEIGHT + 2 * 2))
                self.surface.blit(planet_display.ECOLOGY_SPECIES_IMAGES[i],
                                  (self.get_biomass_letter_x(biomasses), uiframe.FRAME_WIDTH + 2))
                biomasses += 1

class CargoPane(uiframe.UIElement):

    def __init__(self, container, x, y, player):
        width = (2 * uiframe.FRAME_WIDTH + 1.5 * (2 * uiframe.FRAME_WIDTH + macros.ICONS["discovery"].get_width())
                 + 1.5 * (2 * uiframe.FRAME_WIDTH + macros.ICONS["empire"].get_width())
                 + 6 * (2 * uiframe.FRAME_WIDTH + macros.ICONS["mineral_r"].get_width()))
        height = 4 * uiframe.FRAME_WIDTH + macros.ICONS["discovery"].get_height() + font.LETTER_HEIGHT
        super().__init__(container, None, x, y, width, height)
        self.player = player
        self.artifact_icon = uiframe.get_panel_from_image(macros.ICONS["discovery"])
        self.building_icon = uiframe.get_panel_from_image(macros.ICONS["empire"])
        self.mineral_icons = [uiframe.get_panel_from_image(macros.ICONS["mineral_" + x]) for x in "rgbcmy"]
        self.update()

    def draw_amount_with_icon(self, icon, amount, x):
        self.surface.blit(icon, (uiframe.FRAME_WIDTH + x, uiframe.FRAME_WIDTH))
        amount_surface = font.get_text_surface(str(amount))
        self.surface.blit(amount_surface, (uiframe.FRAME_WIDTH + x + (icon.get_width() - amount_surface.get_width()) / 2,
                                           uiframe.FRAME_WIDTH + icon.get_height()))

    def update(self):
        self.surface = uiframe.get_blank_panel_surface(self.width - 2 * uiframe.FRAME_WIDTH,
                                                       self.height - 2 * uiframe.FRAME_WIDTH)
        stagger = 0
        self.draw_amount_with_icon(self.artifact_icon, self.player.selected_ship.cargo.artifacts, stagger)
        stagger += self.artifact_icon.get_width() * 1.5
        self.draw_amount_with_icon(self.building_icon, self.player.selected_ship.cargo.buildings, stagger)
        stagger += self.artifact_icon.get_width() * 1.5
        for i in range(6):
            self.draw_amount_with_icon(self.mineral_icons[i], self.player.selected_ship.cargo.minerals[i], stagger)
            stagger += self.mineral_icons[i].get_width()

    def draw(self, dest_surface):
        self.update()
        super().draw(dest_surface)

