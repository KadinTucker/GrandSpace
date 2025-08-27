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
ACCESS_FRAME_SPACING = 125

ACCESS_ACTIVE_IMAGE_FILENAMES = ["assets/icon-ecology.png", "assets/icon-diplomacy.png", "assets/icon-trade.png",
                                 "assets/icon-access-passage.png"]
ACCESS_PASSIVE_IMAGE_FILENAMES = ["assets/icon-access-trespass.png", "assets/icon-access-piracy.png",
                                  "assets/icon-battle.png", "assets/icon-access-siege.png"]

ACCESS_ACTIVE_IMAGES = [pygame.image.load(fn) for fn in ACCESS_ACTIVE_IMAGE_FILENAMES]
ACCESS_PASSIVE_IMAGES = [pygame.image.load(fn) for fn in ACCESS_PASSIVE_IMAGE_FILENAMES]
ACCESS_BLOCKED_IMG = pygame.image.load("assets/no-access.png")
ACCESS_MISSING_IMG = pygame.image.load("assets/no-access-diplo.png")

ACCESS_FRAME_WIDTH = ACCESS_ICON_OFFSET * len(ACCESS_ACTIVE_IMAGES)
ACCESS_FRAME_HEIGHT = 2 * ACCESS_ICON_OFFSET + 2 * font.LETTER_HEIGHT

PLAYER_FRAME_IMG = pygame.image.load("assets/player-diplo-frame.png")

REVOKE_IMG = pygame.image.load("assets/icon-revoke.png")
FAVOUR_IMG = pygame.image.load("assets/icon-favour.png")

def get_revoke_action(access_id):
    def revoke_access(diplomacy_obj, origin_id, dest_id):
        diplomacy_obj.revoke_access(origin_id, dest_id)
    return revoke_access

def get_offer_action(access_id):
    def offer_access(diplomacy_obj, origin_id, dest_id):
        diplomacy_obj.offer_access(origin_id, dest_id)
    return offer_access

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

def draw_player_frame(surface, color, x, y):
    pygame.draw.rect(surface, color, pygame.Rect(x, y, PLAYER_FRAME_IMG.get_width(), PLAYER_FRAME_IMG.get_height()))
    surface.blit(PLAYER_FRAME_IMG, (x, y))

class DiploActionButton(uiframe.UIElement):

    def __init__(self, container, diplomacy_obj, origin_id, dest_id, icon, action, x, y):
        surface = pygame.Surface((icon.get_width(), icon.get_height()))
        surface.set_colorkey((0, 0, 0))
        super().__init__(container, surface, x, y, icon.get_width(), icon.get_height())
        self.diplomacy = diplomacy_obj
        self.origin_id = origin_id
        self.dest_id = dest_id
        self.icon = icon
        self.action = action
        self.update()

    def update(self):
        self.surface.fill((0, 0, 0))
        self.surface.blit(self.icon, (0, 0))

    def handle_event(self, event, mouse_pos):
        if self.is_point_in(mouse_pos):
            self.action(self.diplomacy, self.origin_id, self.dest_id)

class AccessFrame(uiframe.UIElement):

    def __init__(self, container, diplomacy_obj, origin_id, dest_id, x, y):
        surface = pygame.Surface((ACCESS_FRAME_WIDTH, ACCESS_FRAME_HEIGHT))
        surface.set_colorkey((0, 0, 0))
        super().__init__(container, surface, x, y, ACCESS_FRAME_WIDTH, ACCESS_FRAME_HEIGHT)
        self.diplomacy = diplomacy_obj
        self.origin_id = origin_id
        self.dest_id = dest_id
        self.update()

    def update(self):
        self.surface.fill((0, 0, 0))
        y = 0
        text = font.get_text_surface(get_diplomatic_state(self.diplomacy, self.origin_id, self.dest_id), COLOR_FILL)
        self.surface.blit(text, (0, y))
        y += font.LETTER_HEIGHT
        for i in range(len(ACCESS_PASSIVE_IMAGES)):
            self.surface.blit(ACCESS_PASSIVE_IMAGES[i], (i * ACCESS_ICON_OFFSET, y))
            if not self.diplomacy.get_hostile_access(self.dest_id, self.origin_id, i):
                self.surface.blit(ACCESS_BLOCKED_IMG, (i * ACCESS_ICON_OFFSET, y))
        y += ACCESS_ICON_OFFSET
        for i in range(len(ACCESS_ACTIVE_IMAGES)):
            self.surface.blit(ACCESS_ACTIVE_IMAGES[i], (i * ACCESS_ICON_OFFSET, y))
            if not self.diplomacy.get_active_access(self.dest_id, self.origin_id, i):
                # If access is blocked due to hostility, draw this with red
                if self.diplomacy.leverage_matrix[self.origin_id][self.dest_id] < 0:
                    self.surface.blit(ACCESS_BLOCKED_IMG, (i * ACCESS_ICON_OFFSET, y))
                else:
                    self.surface.blit(ACCESS_MISSING_IMG, (i * ACCESS_ICON_OFFSET, y))

    def handle_event(self, event, mouse_pos):
        rel_pos = (mouse_pos[0] - self.x, mouse_pos[1] - self.y)
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == pygame.BUTTON_LEFT:
                if 0 <= rel_pos[1] - font.LETTER_HEIGHT - ACCESS_ICON_OFFSET <= ACCESS_ICON_OFFSET:
                    index = rel_pos[0] // ACCESS_ICON_OFFSET
                    if 0 <= index < len(ACCESS_ACTIVE_IMAGES):
                        # Toggle the clicked active action
                        # TODO: should only apply to the destination frame!
                        already_grants = self.diplomacy.get_active_access(self.dest_id, self.origin_id, index)
                        if already_grants:
                            # Revoke
                            self.diplomacy.revoke_access(self.dest_id, self.origin_id, index)
                        else:
                            # Offer
                            self.diplomacy.offer_access(self.dest_id, self.origin_id, index)

    def draw(self, dest_surface):
        self.update()
        # super().draw(dest_surface)
        dest_surface.blit(self.surface, (self.x, self.y))

class DiplomacyPane(uiframe.Draggable):

    def __init__(self, container, player, x, y):
        surface = pygame.Surface((PANE_WIDTH, PANE_HEIGHT))
        super().__init__(container, surface, x, y, PANE_WIDTH, PANE_HEIGHT)
        self.player = player
        self.dest_player = None
        self.player_button_pos = [(p, 0, 0) for p in self.player.game.players]
        self.own_access_frames = [AccessFrame(self, self.player.game.diplomacy, self.player.id, i, 0,
                                              font.LETTER_HEIGHT) for i in range(len(self.player.game.players))]
        self.other_access_frames = [AccessFrame(self, self.player.game.diplomacy, i, self.player.id,
                                                0, ACCESS_FRAME_SPACING + font.LETTER_HEIGHT)
                                    for i in range(len(self.player.game.players))]
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
            self.own_access_frames[self.dest_player.id].draw(self.surface)
            y = 2 * font.LETTER_HEIGHT + 2 * ACCESS_BLOCKED_IMG.get_height()
            for i in range(len(ACCESS_ACTIVE_IMAGES)):
                x = i * ACCESS_ICON_OFFSET
            header = font.get_text_surface("their access:", COLOR_TEXT_BG)
            self.surface.blit(header, (0, ACCESS_FRAME_SPACING))
            self.other_access_frames[self.dest_player.id].draw(self.surface)

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
                    self.other_access_frames[self.dest_player.id].handle_event(event, rel_mouse)
                    if (0 <= rel_mouse[0] - (self.width - PLAYER_FRAME_IMG.get_width()) <= PLAYER_FRAME_IMG.get_width()
                            and 0 <= rel_mouse[1] <= PLAYER_FRAME_IMG.get_height()):
                        self.dest_player = None
        super().handle_event(event, mouse_pos)

    def draw(self, dest_surface):
        self.update()
        super().draw(dest_surface)
