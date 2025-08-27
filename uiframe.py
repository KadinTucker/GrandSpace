import pygame

import uiframe

COLOR_BOTTOM = (48, 48, 48)
COLOR_MIDDLE = (94, 94, 94)
COLOR_TOP = (145, 145, 145)
COLOR_FILL = (198, 198, 198)

PATH = "assets/uiframe/"

FRAME_WIDTH = 3

CORNERS = [pygame.image.load(PATH + "highleft.png"), pygame.image.load(PATH + "highright.png"),
           pygame.image.load(PATH + "lowleft.png"), pygame.image.load(PATH + "lowright.png")]
ICON_CLOSE = pygame.image.load(PATH + "close.png")

def get_blank_panel_surface(width, height):
    surface = pygame.Surface((2 * FRAME_WIDTH + width, 2 * FRAME_WIDTH + height))
    surface.fill(COLOR_FILL)
    # Top Left
    surface.blit(CORNERS[0], (0, 0))
    pygame.draw.rect(surface, COLOR_TOP, pygame.Rect(FRAME_WIDTH, 0, width, FRAME_WIDTH))
    # Top Right
    surface.blit(CORNERS[1], (FRAME_WIDTH + width, 0))
    pygame.draw.rect(surface, COLOR_MIDDLE, pygame.Rect(0, FRAME_WIDTH, FRAME_WIDTH, height))
    # Bottom Left
    surface.blit(CORNERS[2], (0, FRAME_WIDTH + height))
    pygame.draw.rect(surface, COLOR_BOTTOM, pygame.Rect(FRAME_WIDTH, FRAME_WIDTH + height, width, FRAME_WIDTH))
    # Bottom Right
    surface.blit(CORNERS[3], (FRAME_WIDTH + width, FRAME_WIDTH + height))
    pygame.draw.rect(surface, COLOR_MIDDLE, pygame.Rect(FRAME_WIDTH + width, FRAME_WIDTH, FRAME_WIDTH, height))
    return surface

def get_panel_from_image(surface, depth=1):
    for _ in range(depth):
        base_surface = get_blank_panel_surface(surface.get_width(), surface.get_height())
        base_surface.blit(surface, (FRAME_WIDTH, FRAME_WIDTH))
        surface = base_surface
    return surface

class UIElement:

    def __init__(self, container, surface, x, y, width, height):
        self.container = container
        self.surface = surface
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.visible = True

    def is_point_in(self, point):
        if self.container is None:
            return 0 <= point[0] - self.x <= self.width and 0 <= point[1] - self.y <= self.height
        return (0 <= point[0] - self.x - self.container.x <= self.width
                and 0 <= point[1] - self.y - self.container.y <= self.height)

    def handle_event(self, event, mouse_pos):
        pass

    def draw(self, dest_surface):
        if self.visible:
            if self.container is None:
                dest_surface.blit(self.surface, (self.x, self.y))
            else:
                dest_surface.blit(self.surface, (self.container.x + self.x, self.container.y + self.y))

    def update(self):
        pass

    def destroy(self):
        self.container.elements.remove(self)

def get_background_pane(container, x, y, width, height):
    panel_large = get_blank_panel_surface(width - 2 * FRAME_WIDTH,
                                                  height - 2 * FRAME_WIDTH)
    return UIElement(container, panel_large, x, y, width, height)


class Draggable(UIElement):

    def __init__(self, container, surface, x, y, width, height):
        super().__init__(container, surface, x, y, width, height)
        bar_surface = pygame.Surface((width, 2 * FRAME_WIDTH))
        bar_surface.blit(get_blank_panel_surface(width - 2 * FRAME_WIDTH, 0), (0, 0))
        bar_surface.blit(ICON_CLOSE, (width - 2 * FRAME_WIDTH, 0))
        self.drag_bar = UIElement(container, bar_surface, x, y - 2 * FRAME_WIDTH, width, 2 * FRAME_WIDTH)
        self.is_held = False
        self.held_at = (0, 0)

    def handle_event(self, event, mouse_pos):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == pygame.BUTTON_LEFT:
                if self.drag_bar.is_point_in(mouse_pos):
                    if mouse_pos[0] - self.x % self.container.width - self.width + 2 * FRAME_WIDTH > 0:
                        self.visible = False
                    else:
                        self.is_held = True
                        self.held_at = (self.x - mouse_pos[0], self.y - mouse_pos[1])
        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == pygame.BUTTON_LEFT:
                self.is_held = False
        elif event.type == pygame.MOUSEMOTION:
            if self.is_held:
                self.move_to(max(min(mouse_pos[0] + self.held_at[0], self.container.width - self.width), 0),
                             max(min(mouse_pos[1] + self.held_at[1],
                                     self.container.height - self.height), 2 * uiframe.FRAME_WIDTH))

    def draw(self, dest_surface):
        super().draw(dest_surface)
        if self.visible:
            self.drag_bar.draw(dest_surface)

    def move_to(self, x, y):
        self.x = x
        self.y = y
        self.drag_bar.x = x
        self.drag_bar.y = y - 2 * FRAME_WIDTH

class UIContainer(UIElement):

    def __init__(self, container, x, y, width, height):
        self.elements = []
        surface = pygame.Surface((width, height))
        surface.set_colorkey((0, 0, 0))
        surface.fill((0, 0, 0))
        super().__init__(container, surface, x, y, width, height)
        self.stagger_left = 0
        self.stagger_right = 0

    def handle_event(self, event, mouse_pos):
        for elt in self.elements:
            elt.handle_event(event, mouse_pos)

    def draw(self, dest_surface):
        if self.visible:
            dest_surface.blit(self.surface, (self.x, self.y))
            for elt in self.elements:
                elt.draw(dest_surface)

    def add_element_left(self, element):
        self.elements.append(element)
        element.x = self.stagger_left
        self.stagger_left += element.width

    def add_element_right(self, element):
        self.elements.append(element)
        element.x = self.width - self.stagger_right - element.width
        self.stagger_right += element.width


