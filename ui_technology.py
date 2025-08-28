import pygame

import technology

import uiframe
import font

# Order: empire, warfare, discovery, ecology, diplomacy, commerce
DOMAIN_COLORS = [(140, 100, 100), (100, 100, 140), (100, 140, 100)]

MAIN_TREE_COLORS = [
    ((100, 20, 150), (150, 20, 100)),
    ((150, 20, 75), (150, 75, 20)),
    ((150, 100, 20), (100, 150, 20)),
    ((75, 150, 20), (20, 150, 75)),
    ((20, 150, 100), (20, 100, 150)),
    ((75, 20, 150), (20, 75, 150)),
]

WILDCARD_COLORS = [
    (150, 20, 150),
    (150, 20, 20),
    (150, 150, 20),
    (20, 150, 20),
    (20, 150, 150),
    (20, 20, 150),
]

DOMAINS = [
    0, 0, 1, 2, 2, 1
]

ROMAN_NUMERALS = "i ii iii iv v".split()

PANE_WIDTH = 800
PANE_HEIGHT = 300

TECH_MARGIN = 15
TECH_WIDTH = 228 + 6
TECH_HEIGHT = 30 + 6
WILDCARD_HEIGHT = 60

COLOR_BACKGROUND = (100, 100, 100)

def shade_color(color):
    return color[0] // 2, color[1] // 2, color[2] // 2

def get_tech_label(category, branch, level, unlocked):
    base_surface = pygame.Surface((TECH_WIDTH - 6, TECH_HEIGHT - 6))
    color = MAIN_TREE_COLORS[category][branch]
    if not unlocked:
        color = shade_color(color)
    base_surface.fill(color)
    text_img = font.get_text_surface(technology.MAIN_TREE_NAMES[category][branch].lower()
                                     + " " + ROMAN_NUMERALS[level], color)
    base_surface.blit(text_img, ((base_surface.get_width() - text_img.get_width()) // 2,
                                 (base_surface.get_height() - text_img.get_height()) // 2))
    return uiframe.get_panel_from_image(base_surface)

def get_wildcard_label(category, level, unlocked):
    base_surface = pygame.Surface((TECH_WIDTH - 6, WILDCARD_HEIGHT - 6))
    color = WILDCARD_COLORS[category]
    if not unlocked:
        color = shade_color(color)
    base_surface.fill(color)
    lines = technology.WILDCARD_NAMES[category][level].split(" ")
    for l in range(len(lines)):
        text_img = font.get_text_surface(lines[l].lower(), color)
        base_surface.blit(text_img, ((base_surface.get_width() - text_img.get_width()) // 2,
                                     (base_surface.get_height()) * (l + 1) // (len(lines) + 1) - 8))
    return uiframe.get_panel_from_image(base_surface)


MAIN_TREE_IMGS = [
    [[[get_tech_label(i, j, k, unlocked) for k in range(5)] for j in range(2)] for i in range(6)]
     for unlocked in [False, True]
]

WILDCARD_IMGS = [
    [[get_wildcard_label(i, j, unlocked) for j in range(2)] for i in range(6)]
     for unlocked in [False, True]
]

class TechPane(uiframe.Draggable):

    def __init__(self, container, x, y, tech_obj):
        surface = pygame.Surface((PANE_WIDTH, PANE_HEIGHT))
        super().__init__(container, surface, x, y, PANE_WIDTH, PANE_HEIGHT)
        self.category = 0
        self.technology = tech_obj
        self.update()

    def update(self):
        self.surface.fill(DOMAIN_COLORS[technology.DOMAINS[self.category]])
        for j in range(5):
            unlocked = int(self.technology.tech_level[self.category][0] > j)
            print(len(MAIN_TREE_IMGS))
            self.surface.blit(MAIN_TREE_IMGS[unlocked][self.category][0][j],
                              (TECH_MARGIN, TECH_MARGIN * (j + 1) + TECH_HEIGHT * j))
        for j in range(5):
            unlocked = int(self.technology.tech_level[self.category][1] > j)
            self.surface.blit(MAIN_TREE_IMGS[unlocked][self.category][1][j],
                              (PANE_WIDTH - TECH_MARGIN - TECH_WIDTH, TECH_MARGIN * (j + 1) + TECH_HEIGHT * j))
        for j in range(2):
            unlocked = int(self.technology.tech_level[self.category][2] > j)
            self.surface.blit(WILDCARD_IMGS[unlocked][self.category][j], ((PANE_WIDTH - TECH_WIDTH) // 2,
                                                                (TECH_HEIGHT + TECH_MARGIN) * (2 * j + 2)))

    def handle_event(self, event, mouse_pos):
        super().handle_event(event, mouse_pos)
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_q:
                self.category = (self.category - 1) % 6
                self.update()
            elif event.key == pygame.K_e:
                self.category = (self.category + 1) % 6
                self.update()
            print(self.category)
