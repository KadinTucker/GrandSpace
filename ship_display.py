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

SHIP_STACK_RADIUS = 15

COLOR_SHIP_SELECTION = (225, 225, 225)

def draw_ship_selection(surface, position):
    pygame.draw.circle(surface, COLOR_SHIP_SELECTION, position, SHIP_SELECTION_RADIUS)

def draw_ship(surface, ship_obj, position):
    pygame.draw.circle(surface, ship_obj.ruler.color, position, SHIP_COLOR_RADIUS)
    surface.blit(IMG_SHIP, (position[0] - SHIP_WIDTH // 2, position[1] - SHIP_HEIGHT // 2))

def draw_overlapping_ships(surface, ships, position):
    if len(ships) == 0:
        return
    radius = SHIP_STACK_RADIUS * (len(ships) - 1)
    angle_mult = 2 * math.pi / len(ships)
    for s in range(len(ships)):
        angle = s * angle_mult - math.pi / 2
        draw_ship(surface, ships[s], (int(position[0] + radius * math.cos(angle)), int(position[1] + radius * math.sin(angle))))
