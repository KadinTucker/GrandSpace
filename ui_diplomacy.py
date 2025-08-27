import pygame

import diplomacy
import font
import uiframe
import system_display as sd

PANE_WIDTH = 250
PANE_HEIGHT = 400

COLOR_FILL = (115, 145, 145)
COLOR_TEXT_BG = (55, 115, 115)
ACCESS_ICON_OFFSET = 24

ACCESS_ACTIVE_IMAGE_FILENAMES = ["assets/icon-ecology.png", "assets/icon-diplomacy.png", "assets/icon-trade.png",
                                 "assets/icon-access-passage.png"]
ACCESS_PASSIVE_IMAGE_FILENAMES = ["assets/icon-access-trespass.png", "assets/icon-access-piracy.png",
                                  "assets/icon-battle.png", "assets/icon-access-siege.png"]

ACCESS_ACTIVE_IMAGES = [pygame.image.load(fn) for fn in ACCESS_ACTIVE_IMAGE_FILENAMES]
ACCESS_PASSIVE_IMAGES = [pygame.image.load(fn) for fn in ACCESS_PASSIVE_IMAGE_FILENAMES]
ACCESS_BLOCKED_IMG = pygame.image.load("assets/no-access.png")
ACCESS_MISSING_IMG = pygame.image.load("assets/no-access-diplo.png")

PLAYER_FRAME_IMG = pygame.image.load("assets/player-diplo-frame.png")

def get_diplomatic_state(diplomacy_obj, origin_id, dest_id):
    # If the target has offended the origin
    if diplomacy_obj.leverage_matrix[dest_id][origin_id] < 0:
        return "hostile"
    else:
        # if only the origin has offended the target:
        if diplomacy_obj.leverage_matrix[origin_id][dest_id] < 0:
            return "blocked"
    # Otherwise, friends
    return "friendly"

def draw_access(surface, diplomacy_obj, origin_id, dest_id, x, y):
    text = font.get_text_surface(get_diplomatic_state(diplomacy_obj, origin_id, dest_id), COLOR_FILL)
    # If "at war", only show hostile accesses
    if diplomacy_obj.leverage_matrix[dest_id][origin_id] < 0:
        surface.blit(text, (x, y))
        for i in range(len(ACCESS_PASSIVE_IMAGES)):
            surface.blit(ACCESS_PASSIVE_IMAGES[i], (x + i * ACCESS_ICON_OFFSET, y + text.get_height()))
            if not diplomacy_obj.get_hostile_access(dest_id, origin_id, i):

                surface.blit(ACCESS_BLOCKED_IMG, (x + i * ACCESS_ICON_OFFSET, y + text.get_height()))
    else:
        for i in range(len(ACCESS_ACTIVE_IMAGES)):
            surface.blit(text, (x, y))
            surface.blit(ACCESS_ACTIVE_IMAGES[i], (x + i * ACCESS_ICON_OFFSET, y + text.get_height()))
            if not diplomacy_obj.get_active_access(dest_id, origin_id, i):
                # If access is blocked due to hostility, draw this with red
                if diplomacy_obj.leverage_matrix[origin_id][dest_id] < 0:
                    surface.blit(ACCESS_BLOCKED_IMG, (x + i * ACCESS_ICON_OFFSET, y + text.get_height()))
                else:
                    surface.blit(ACCESS_MISSING_IMG, (x + i * ACCESS_ICON_OFFSET, y + text.get_height()))

def draw_player_frame(surface, color, x, y):
    pygame.draw.rect(surface, color, pygame.Rect(x, y, PLAYER_FRAME_IMG.get_width(), PLAYER_FRAME_IMG.get_height()))
    surface.blit(PLAYER_FRAME_IMG, (x, y))

class DiplomacyPane(uiframe.Draggable):

    def __init__(self, container, player, x, y):
        surface = pygame.Surface((PANE_WIDTH, PANE_HEIGHT))
        super().__init__(container, surface, x, y, PANE_WIDTH, PANE_HEIGHT)
        self.player = player
        self.dest_player = None
        self.player_button_pos = [(p, 0, 0) for p in self.player.game.players]
        self.update()

    def update_player_select_positions(self, left, top):
        self.player_button_pos = [(None, 0, 0) for _ in range(len(self.player.game.players) - 1)]
        index = 0
        for p in self.player.game.players:
            if p is not self.player:
                self.player_button_pos[index] = (p, left + index * PLAYER_FRAME_IMG.get_width(), top)
                index += 1

    def update(self):
        self.surface.fill(COLOR_FILL)
        if self.dest_player is None:
            select_surface = font.get_text_surface("select a player")
            self.surface.blit(select_surface, ((self.width - select_surface.get_width()) / 2, 0))
            left = (self.width - (len(self.player.game.players) - 1) * PLAYER_FRAME_IMG.get_width()) / 2
            top = select_surface.get_height()
            self.update_player_select_positions(left, top)
            for i in range(len(self.player_button_pos)):
                draw_player_frame(self.surface, self.player_button_pos[i][0].color,
                                  self.player_button_pos[i][1], self.player_button_pos[i][2])
        else:
            draw_player_frame(self.surface, self.dest_player.color, self.width - PLAYER_FRAME_IMG.get_width(), 0)
            header = font.get_text_surface("your access:", COLOR_TEXT_BG)
            self.surface.blit(header, (0, 0))
            draw_access(self.surface, self.player.game.diplomacy, self.player.id, self.dest_player.id, 0,
                        header.get_height())
            header = font.get_text_surface("their access:", COLOR_TEXT_BG)
            self.surface.blit(header, (0, 75))
            draw_access(self.surface, self.player.game.diplomacy, self.dest_player.id, self.player.id, 0,
                        75 + header.get_height())

    def handle_event(self, event, mouse_pos):
        if self.dest_player is None:
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == pygame.BUTTON_LEFT:
                    rel_mouse = (mouse_pos[0] - self.x - self.container.x, mouse_pos[1] - self.y - self.container.y)
                    for i in range(len(self.player_button_pos)):
                        if (0 <= rel_mouse[0] - self.player_button_pos[i][1] <= PLAYER_FRAME_IMG.get_width()
                                and 0 <= rel_mouse[1] - self.player_button_pos[i][2] <= PLAYER_FRAME_IMG.get_height()):
                            self.dest_player = self.player_button_pos[i][0]
        else:
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == pygame.BUTTON_LEFT:
                    rel_mouse = (mouse_pos[0] - self.x - self.container.x, mouse_pos[1] - self.y - self.container.y)
                    if (0 <= rel_mouse[0] - (self.width - PLAYER_FRAME_IMG.get_width()) <= PLAYER_FRAME_IMG.get_width()
                            and 0 <= rel_mouse[1] <= PLAYER_FRAME_IMG.get_height()):
                        self.dest_player = None
        super().handle_event(event, mouse_pos)

    def draw(self, dest_surface):
        self.update()
        super().draw(dest_surface)
