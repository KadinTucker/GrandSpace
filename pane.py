import pygame

import drawable

class Pane(drawable.Drawable):

    def __init__(self, game, player, pane_dimensions, pane_position, num_layers, background_color):
        """
        A layered panel, with multiple cached layers
        The first layer, at index 0, is the background layer
        Subsequent layers lie on top
        Can also (optionally) zoom and handle events
        """
        super().__init__(game, pane_dimensions)
        self.player = player
        self.position = pane_position
        self.background_color = background_color
        self.next_pane_id = -1
        self.view_corner = (0, 0)
        self.view_scale = 1.0
        self.num_clicks = 0
        self.layers = []
        self.init_layers(num_layers)

    def get_relative_pane_pos(self, position):
        return position[0] - self.position[0], position[1] - self.position[1]

    def init_layers(self, num_layers):
        self.layers.append(pygame.Surface(self.dimensions))
        self.layers[0].fill(self.background_color)
        for _ in range(num_layers - 1):
            self.layers.append(drawable.create_blank_surface(self.dimensions, self.background_color))

    def refresh_layer(self, index):
        if index == 0:
            self.layers[index] = pygame.Surface(self.dimensions)
        else:
            self.layers[index] = drawable.create_blank_surface(self.dimensions, self.background_color)

    def update(self):
        for i in range(len(self.layers)):
            self.refresh_layer(i)

    def draw(self, dest_surface, position=None):
        for layer in self.layers:
            dest_surface.blit(layer, self.position)

    def set_scale(self, new_scale, center):
        scale_change_coefficient = 1 / self.view_scale - 1 / new_scale
        self.view_corner = (self.view_corner[0] + center[0] * scale_change_coefficient,
                            self.view_corner[1] + center[1] * scale_change_coefficient)
        self.view_scale = new_scale
        self.update()

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

    def handle_event(self, event, mouse_pos):
        """
        Takes a pygame Event object as input, the mouse position, and the active player
        Modifies data internal to the object
        """
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == pygame.BUTTON_LEFT:
                self.num_clicks += 1
        elif event.type == pygame.MOUSEMOTION:
            self.num_clicks = 0
