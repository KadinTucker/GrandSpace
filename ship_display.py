import pygame
import sys
import math

import galaxy
import player
import ship

IMG_SHIP = pygame.image.load("assets/ufo.png")
SHIP_WIDTH = IMG_SHIP.get_width()
SHIP_HEIGHT = IMG_SHIP.get_height()

SHIP_COLOR_RADIUS = 8
SHIP_SELECTION_RADIUS = 12

SHIP_STACK_RADIUS = 10

COLOR_SHIP_SELECTION = (225, 225, 225)

def draw_ship_selection(surface, position):
    pygame.draw.circle(surface, COLOR_SHIP_SELECTION, position, SHIP_SELECTION_RADIUS)

def draw_ship(surface, ship_obj, position, player=None):
    if player != None and ship_obj == player.selected_ship:
        draw_ship_selection(surface, position)
    pygame.draw.circle(surface, ship_obj.ruler.color, position, SHIP_COLOR_RADIUS)
    surface.blit(IMG_SHIP, (position[0] - SHIP_WIDTH // 2, position[1] - SHIP_HEIGHT // 2))

def find_overlapped_ship(center, ships, position, radius):
    star_ship_positions = get_overlapped_ship_positions(center, ships)
    for i in range(len(star_ship_positions)):
        if math.hypot(star_ship_positions[i][0] - position[0], star_ship_positions[i][1] - position[1]) <= radius:
            return ships[i]
    return None

def get_overlapped_ship_positions(center, ships):
    if len(ships) == 0:
        return []
    radius = SHIP_STACK_RADIUS * (len(ships) - 1)
    angle =  2 * math.pi / len(ships)
    return [(int(center[0] + radius * math.cos(i * angle)), int(center[1] + radius * math.sin(i * angle))) for i in range(len(ships))]

# def draw_overlapping_ships(surface, ships, position, player=None):
#     if len(ships) == 0:
#         return
#     radius = SHIP_STACK_RADIUS * (len(ships) - 1)
#     angle_mult = 2 * math.pi / len(ships)
#     for s in range(len(ships)):
#         angle = s * angle_mult - math.pi / 2
#         draw_ship(surface, ships[s], (int(position[0] + radius * math.cos(angle)), int(position[1] + radius * math.sin(angle))), player)

def draw_overlapping_ships(surface, ships, center, player=None):
    positions = get_overlapped_ship_positions(center, ships)
    for i in range(len(positions)):
        draw_ship(surface, ships[i], positions[i], player)