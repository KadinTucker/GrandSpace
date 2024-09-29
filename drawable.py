import pygame

def draw_centered(dest_surface, to_draw, position):
    to_draw.draw(dest_surface, (position[0] - to_draw.dimensions[0] // 2, position[1] - to_draw.dimensions[1] // 2))

def create_blank_surface(dimensions, background_color):
    """
    Creates a new surface that sets the background color as transparent
    Meaning that filling in the surface with the background color will fill with transparency
    """
    surface = pygame.Surface(dimensions)
    surface.set_colorkey(background_color)
    surface.fill(background_color)
    return surface

class Drawable:

    def __init__(self, game, dimensions):
        self.game = game
        self.dimensions = dimensions

    def draw(self, dest_surface, position):
        pass
