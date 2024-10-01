import pygame

import technology

import uiframe
import font

DOMAIN_COLORS = [(140, 100, 100), (100, 100, 140), (100, 140, 100)]

MAIN_TREE_COLORS = [
    ((100, 20, 150), (150, 20, 100)),
    ((150, 20, 75), (150, 75, 20)),
    ((150, 100, 20), (100, 150, 20)),
    ((75, 20, 150), (20, 75, 150)),
    ((20, 150, 100), (20, 100, 150)),
    ((75, 150, 20), (20, 150, 75))
]

WILDCARD_COLORS = [
    (150, 20, 150),
    (150, 20, 20),
    (150, 150, 20),
    (20, 20, 150),
    (20, 150, 150),
    (20, 150, 20),
]

ROMAN_NUMERALS = "i ii iii iv v".split()

PANE_WIDTH = 800
PANE_HEIGHT = 300

TECH_MARGIN = 15
TECH_WIDTH = 228 + 6
TECH_HEIGHT = 30 + 6
WILDCARD_HEIGHT = 60

COLOR_BACKGROUND = (100, 100, 100)

def get_tech_label(category, branch, level):
    base_surface = pygame.Surface((TECH_WIDTH - 6, TECH_HEIGHT - 6))
    base_surface.fill(MAIN_TREE_COLORS[category][branch])
    text_img = font.get_text_surface(technology.MAIN_TREE_NAMES[category][branch].lower()
                                     + " " + ROMAN_NUMERALS[level], MAIN_TREE_COLORS[category][branch])
    base_surface.blit(text_img, ((base_surface.get_width() - text_img.get_width()) // 2,
                                 (base_surface.get_height() - text_img.get_height()) // 2))
    return uiframe.create_button_surface(base_surface)

def get_wildcard_label(category, level):
    base_surface = pygame.Surface((TECH_WIDTH - 6, WILDCARD_HEIGHT - 6))
    base_surface.fill(WILDCARD_COLORS[category])
    lines = technology.WILDCARD_NAMES[category][level].split(" ")
    for l in range(len(lines)):
        text_img = font.get_text_surface(lines[l].lower(), WILDCARD_COLORS[category])
        base_surface.blit(text_img, ((base_surface.get_width() - text_img.get_width()) // 2,
                                     (base_surface.get_height()) * (l + 1) // (len(lines) + 1) - 8))
    return uiframe.create_button_surface(base_surface)

MAIN_TREE_IMGS = [
    [[get_tech_label(i, j, k) for k in range(5)] for j in range(2)] for i in range(6)
]

WILDCARD_IMGS = [
    [get_wildcard_label(i, j) for j in range(2)] for i in range(6)
]

class TechPane(uiframe.Draggable):

    def __init__(self, container, x, y):
        surface = pygame.Surface((PANE_WIDTH, PANE_HEIGHT))
        super().__init__(container, surface, x, y, PANE_WIDTH, PANE_HEIGHT)
        self.category = 0
        self.update()

    def update(self):
        self.surface.fill(DOMAIN_COLORS[technology.DOMAINS[self.category]])
        for j in range(5):
            self.surface.blit(MAIN_TREE_IMGS[self.category][0][j],
                              (TECH_MARGIN, TECH_MARGIN * (j + 1) + TECH_HEIGHT * j))
        for j in range(5):
            self.surface.blit(MAIN_TREE_IMGS[self.category][1][j],
                              (PANE_WIDTH - TECH_MARGIN - TECH_WIDTH, TECH_MARGIN * (j + 1) + TECH_HEIGHT * j))
        for j in range(2):
            self.surface.blit(WILDCARD_IMGS[self.category][j], ((PANE_WIDTH - TECH_WIDTH) // 2,
                                                                (TECH_HEIGHT + TECH_MARGIN) * (2 * j + 2)))

    def handle_event(self, event, mouse_pos):
        super().handle_event(event, mouse_pos)
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_q:
                self.category = (self.category + 1) % 6
                self.update()
            elif event.key == pygame.K_e:
                self.category = (self.category + 1) % 6
                self.update()
