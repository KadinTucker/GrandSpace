import pygame

COLOR_BOTTOM = (48, 48, 48)
COLOR_MIDDLE = (94, 94, 94)
COLOR_TOP = (145, 145, 145)
COLOR_FILL = (198, 198, 198)

PATH = "assets/uiframe/"

corners = [pygame.image.load(PATH + "highleft.png"), pygame.image.load(PATH + "highright.png"),
           pygame.image.load(PATH + "lowleft.png"), pygame.image.load(PATH + "lowright.png")]

def get_panel_surface(width, height):
    surface = pygame.Surface((6 + width, 6 + height))
    surface.fill(COLOR_FILL)
    # Top Left
    surface.blit(corners[0], (0, 0))
    pygame.draw.rect(surface, COLOR_TOP, pygame.Rect(3, 0, width, 3))
    # Top Right
    surface.blit(corners[1], (3 + width, 0))
    pygame.draw.rect(surface, COLOR_MIDDLE, pygame.Rect(0, 3, 3, height))
    # Bottom Left
    surface.blit(corners[2], (0, 3 + height))
    pygame.draw.rect(surface, COLOR_BOTTOM, pygame.Rect(3, 3 + height, width, 3))
    # Bottom Right
    surface.blit(corners[3], (3 + width, 3 + height))
    pygame.draw.rect(surface, COLOR_MIDDLE, pygame.Rect(3 + width, 3, 3, height))
    return surface

def create_button(button_filename):
    button_surface = pygame.image.load(button_filename)
    base_surface = get_panel_surface(button_surface.get_width(), button_surface.get_height())
    base_surface.blit(button_surface, (3, 3))
    return base_surface
