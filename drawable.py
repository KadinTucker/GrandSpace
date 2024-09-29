import pygame

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

    def __init__(self, game, position, dimensions):
        self.game = game
        self.position = position
        self.dimensions = dimensions

    def draw(self, dest_surface):
        pass

    def update(self):
        pass
