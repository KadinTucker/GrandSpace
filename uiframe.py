import pygame

COLOR_BOTTOM = (48, 48, 48)
COLOR_MIDDLE = (94, 94, 94)
COLOR_TOP = (145, 145, 145)
COLOR_FILL = (198, 198, 198)

PATH = "assets/uiframe/"

corners = [pygame.image.load(PATH + "highleft.png"), pygame.image.load(PATH + "highright.png"),
           pygame.image.load(PATH + "lowleft.png"), pygame.image.load(PATH + "lowright.png")]
close = pygame.image.load(PATH + "close.png")

def get_panel_surface(width, height):
    surface = pygame.Surface((6 + width, 6 + height))
    surface.fill(COLOR_FILL)
    # Top Left
    surface.blit(corners[0], (0, 0))
    pygame.draw.rect(surface, COLOR_TOP, pygame.Rect(3, 0, width, 3))
    # Top Right
    surface.blit(corners[1], (3 + width, 0))
    pygame.draw.rect(surface, COLOR_MIDDLE, pygame.Rect(0, 3, 3, height))
    # Bottom Left
    surface.blit(corners[2], (0, 3 + height))
    pygame.draw.rect(surface, COLOR_BOTTOM, pygame.Rect(3, 3 + height, width, 3))
    # Bottom Right
    surface.blit(corners[3], (3 + width, 3 + height))
    pygame.draw.rect(surface, COLOR_MIDDLE, pygame.Rect(3 + width, 3, 3, height))
    return surface

def create_button_surface(button_surface):
    base_surface = get_panel_surface(button_surface.get_width(), button_surface.get_height())
    base_surface.blit(button_surface, (3, 3))
    return base_surface

class UIElement:

    def __init__(self, container, surface, x, y, width, height):
        self.container = container
        self.surface = surface
        self.x = x  # negative values mean position from the right
        self.y = y  # negative values mean position from the bottom
        self.width = width
        self.height = height

    def is_point_in(self, point):
        return (0 <= point[0] - self.x % self.container.dimensions[0] <= self.width
                and 0 <= point[1] - self.y % self.container.dimensions[1] <= self.height)

    def handle_event(self, event, mouse_pos):
        pass

    def draw(self, dest_surface):
        dest_surface.blit(self.surface, (self.x % self.container.dimensions[0], self.y % self.container.dimensions[1]))

    def destroy(self):
        self.container.elements.remove(self)

class Draggable(UIElement):

    def __init__(self, container, surface, x, y, width, height):
        super().__init__(container, surface, x, y, width, height)
        bar_surface = pygame.Surface((width, 6))
        bar_surface.blit(get_panel_surface(width - 6, 0), (0, 0))
        bar_surface.blit(close, (width - 6, 0))
        self.drag_bar = UIElement(container, bar_surface, x, y - 6, width, 6)
        self.is_held = False
        self.held_at = (0, 0)

    def handle_event(self, event, mouse_pos):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == pygame.BUTTON_LEFT:
                if self.drag_bar.is_point_in(mouse_pos):
                    if mouse_pos[0] - self.x % self.container.dimensions[0] - self.width + 6 > 0:
                        self.destroy()
                    else:
                        self.is_held = True
                        self.held_at = (self.x - mouse_pos[0], self.y - mouse_pos[1])
        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == pygame.BUTTON_LEFT:
                self.is_held = False
        elif event.type == pygame.MOUSEMOTION:
            if self.is_held:
                self.move_to(mouse_pos[0] + self.held_at[0], mouse_pos[1] + self.held_at[1])

    def draw(self, dest_surface):
        super().draw(dest_surface)
        self.drag_bar.draw(dest_surface)

    def move_to(self, x, y):
        self.x = x
        self.y = y
        self.drag_bar.x = x
        self.drag_bar.y = y - 6

class UIContainer:

    def __init__(self, dimensions):
        self.dimensions = dimensions
        self.elements = []

    def handle_event(self, event, mouse_pos):
        pass
