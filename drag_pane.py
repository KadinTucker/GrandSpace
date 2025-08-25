import pygame

import pane

ZOOM_MAX = 2.0
ZOOM_MIN = 0.5
ZOOM_RATE = 0.1

class DragPane(pane.Pane):

    def __init__(self, game, player, pane_dimensions, pane_position, num_layers, background_color):
        super().__init__(game, player, pane_dimensions, pane_position, num_layers, background_color)
        self.held_at = self.view_corner
        self.is_held = False

    def handle_event(self, event, mouse_pos):
        super().handle_event(event, mouse_pos)
        mouse_pos = self.get_relative_pane_pos(mouse_pos)
        if not pygame.mouse.get_pressed()[0]:
            self.is_held = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == pygame.BUTTON_LEFT:
                self.is_held = True
                self.held_at = (self.view_corner[0] - mouse_pos[0], self.view_corner[1] - mouse_pos[1])
                self.update()
            elif event.button == pygame.BUTTON_WHEELUP:
                self.set_scale(min(ZOOM_MAX, self.view_scale + ZOOM_RATE), mouse_pos)
            elif event.button == pygame.BUTTON_WHEELDOWN:
                self.set_scale(max(ZOOM_MIN, self.view_scale - ZOOM_RATE), mouse_pos)
        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == pygame.BUTTON_LEFT:
                self.is_held = False
        elif event.type == pygame.MOUSEMOTION:
            if self.is_held:
                self.view_corner = (self.held_at[0] + mouse_pos[0], self.held_at[1] + mouse_pos[1])
                self.update()

