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


class Pane(object):

    def __init__(self, game, player, pane_dimensions, pane_position, num_layers, background_color):
        """
        A layered panel, with multiple cached layers
        The first layer, at index 0, is the background layer
        Subsequent layers lie on top
        Can also (optionally) zoom and handle events
        """
        self.game = game
        self.player = player
        self.pane_dimensions = pane_dimensions
        self.pane_position = pane_position
        self.next_pane_id = -1
        self.view_corner = (0, 0)
        self.view_scale = 1.0
        self.num_clicks = 0
        self.layers = []
        self.background_color = background_color
        self.init_layers(num_layers)

    def get_relative_pane_pos(self, position):
        return position[0] - self.pane_position[0], position[1] - self.pane_position[1]

    def init_layers(self, num_layers):
        self.layers.append(pygame.Surface(self.pane_dimensions))
        self.layers[0].fill(self.background_color)
        for _ in range(num_layers - 1):
            self.layers.append(create_blank_surface(self.pane_dimensions, self.background_color))

    def refresh_layer(self, index):
        if index == 0:
            self.layers[index] = pygame.Surface(self.pane_dimensions)
        else:
            self.layers[index] = create_blank_surface(self.pane_dimensions, self.background_color)

    def refresh_all_layers(self):
        for i in range(len(self.layers)):
            self.refresh_layer(i)

    def draw(self, display):
        for layer in self.layers:
            display.blit(layer, self.pane_position)

    def set_scale(self, new_scale, center):
        scale_change_coefficient = 1 / self.view_scale - 1 / new_scale
        self.view_corner = (self.view_corner[0] + center[0] * scale_change_coefficient,
                            self.view_corner[1] + center[1] * scale_change_coefficient)
        self.view_scale = new_scale
        self.refresh_all_layers()

    def project_coordinate(self, coordinate):
        """
        Turns a zoomed coordinate into a pane display coordinate
        """
        return (self.view_scale * (coordinate[0] - self.view_corner[0]),
                self.view_scale * (coordinate[1] - self.view_corner[1]))

    def deproject_coordinate(self, coordinate):
        """
        Turns a pane display coordinate into a zoomed coordinate
        """
        return (int(coordinate[0] / self.view_scale + self.view_corner[0]),
                int(coordinate[1] / self.view_scale + self.view_corner[1]))

    def handle_event(self, event, mouse_pos, active_player):
        """
        Takes a pygame Event object as input, the mouse position, and the active player
        Modifies data internal to the object
        """
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == pygame.BUTTON_LEFT:
                self.num_clicks += 1
        elif event.type == pygame.MOUSEMOTION:
            self.num_clicks = 0
