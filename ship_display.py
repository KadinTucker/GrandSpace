import pygame
import sys
import math

import galaxy
import player
import ship

IMG_SHIP = pygame.image.load("assets/ufo.png")
SHIP_WIDTH = IMG_SHIP.get_width()
SHIP_HEIGHT = IMG_SHIP.get_height()

COLOR_SHIP_SELECTION = (225, 225, 225)

def draw_ship(surface, ship_obj, position):
    if ship_obj.selected:
        pygame.draw.circle(surface, COLOR_SHIP_SELECTION, position, 12)
    pygame.draw.circle(surface, ship_obj.ruler.color, position, 8)
    surface.blit(IMG_SHIP, (position[0] - SHIP_WIDTH / 2, position[1] - SHIP_HEIGHT / 2))

def draw_overlapping_ships(surface, ships, position):
    if len(ships) == 0:
        return
    radius = 15 * (len(ships) - 1)
    angle_mult = 2 * math.pi / len(ships)
    for s in range(len(ships)):
        angle = s * angle_mult - math.pi / 2
        draw_ship(surface, ships[s], (int(position[0] + radius * math.cos(angle)), int(position[1] + radius * math.sin(angle))))
