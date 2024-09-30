import pygame
import math

IMG_SHIP = pygame.image.load("assets/ufo.png")
SHIP_WIDTH = IMG_SHIP.get_width()
SHIP_HEIGHT = IMG_SHIP.get_height()

SHIP_COLOR_RADIUS = 8
SHIP_SELECTION_RADIUS = 12
SHIP_RANGE_WIDTH = 1

SHIP_STACK_RADIUS = 10

SHIP_PROJECTILE_FRAMES = 45
SHIP_PROJECTILE_LENGTH = 5
SHIP_PROJECTILE_WIDTH = 2

COLOR_SHIP_SELECTION = (225, 225, 225)
COLOR_SHIP_PROJECTILE = (200, 50, 50)
COLOR_SHIP_HEALTH = (10, 220, 10)
COLOR_SHIP_DAMAGE = (180, 10, 10)

def draw_ship_selection(surface, position):
    pygame.draw.circle(surface, COLOR_SHIP_SELECTION, position, SHIP_SELECTION_RADIUS)

def draw_ship_galaxy_range(surface, position, radius, scale):
    pygame.draw.circle(surface, COLOR_SHIP_SELECTION, position, int(radius * scale),
                       math.ceil(SHIP_RANGE_WIDTH * scale))

def draw_ship(surface, ship_obj, position, player=None):
    if player is not None and ship_obj == player.selected_ship:
        draw_ship_selection(surface, position)
    pygame.draw.circle(surface, ship_obj.ruler.color, position, SHIP_COLOR_RADIUS)
    surface.blit(IMG_SHIP, (position[0] - SHIP_WIDTH // 2, position[1] - SHIP_HEIGHT // 2))
    draw_ship_health(surface, ship_obj, position)
    draw_ship_action_progress(surface, ship_obj, position)

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
    angle = 2 * math.pi / len(ships)
    return [(int(center[0] + radius * math.cos(i * angle)),
             int(center[1] + radius * math.sin(i * angle))) for i in range(len(ships))]

def draw_overlapping_ships(surface, ships, center, player=None):
    positions = get_overlapped_ship_positions(center, ships)
    for i in range(len(positions)):
        draw_ship(surface, ships[i], positions[i], player)
    return positions

def find_overlapped_ship_position(ship, overlapped_ships, position):
    ship_positions = get_overlapped_ship_positions(position, overlapped_ships)
    for i in range(len(ship_positions)):
        if overlapped_ships[i] is ship:
            return ship_positions[i]
    return None

def draw_ship_projectile(surface, origin_pos, destination_pos, progress):
    diffx = destination_pos[0] - origin_pos[0]
    diffy = destination_pos[1] - origin_pos[1]
    dist = math.hypot(diffx, diffy)
    pygame.draw.line(surface, COLOR_SHIP_PROJECTILE,
                     (origin_pos[0] + progress * diffx, origin_pos[1] + progress * diffy),
                     (origin_pos[0] + (progress + SHIP_PROJECTILE_LENGTH / dist) * diffx,
                      origin_pos[1] + (progress + SHIP_PROJECTILE_LENGTH / dist) * diffy), SHIP_PROJECTILE_WIDTH)

def draw_ship_health(surface, ship, position):
    if ship.health < ship.ruler.technology.get_ship_max_health():
        pygame.draw.rect(surface, (0, 0, 0),
                         pygame.Rect(position[0] - SHIP_WIDTH // 2 - 1, position[1] + SHIP_HEIGHT // 2 - 1,
                                     SHIP_WIDTH + 2, SHIP_HEIGHT // 4 + 2), 1)
        pygame.draw.rect(surface, COLOR_SHIP_DAMAGE, pygame.Rect(position[0] - SHIP_WIDTH // 2, position[1]
                                                                 + SHIP_HEIGHT // 2, SHIP_WIDTH, SHIP_HEIGHT // 4))
        pygame.draw.rect(surface, COLOR_SHIP_HEALTH,
                         pygame.Rect(position[0] - SHIP_WIDTH // 2, position[1] + SHIP_HEIGHT // 2,
                                     int(SHIP_WIDTH * ship.health / ship.ruler.technology.get_ship_max_health()),
                                     SHIP_HEIGHT // 4))

def draw_ship_action_progress(surface, ship, position):
    if ship.action_progress > 0.0:
        pygame.draw.rect(surface, (150, 150, 150),
                         pygame.Rect(position[0] + SHIP_WIDTH // 2, position[1] - SHIP_HEIGHT // 2, 5,
                                     int(ship.action_progress * SHIP_HEIGHT) + 2), 1)
        pygame.draw.rect(surface, (200, 200, 200),
                         pygame.Rect(position[0] + SHIP_WIDTH // 2 + 1, position[1] - SHIP_HEIGHT // 2 + 1, 3,
                                     int(ship.action_progress * SHIP_HEIGHT)))

class ProjectileAnim:

    def __init__(self, ship_origin, ship_target):
        self.ship_origin = ship_origin
        self.ship_target = ship_target
        self.last_position = None
        self.progress = 0

    def get_progress_fraction(self):
        return self.progress / SHIP_PROJECTILE_FRAMES
