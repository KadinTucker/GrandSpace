import pygame

PATH = "assets/typeface/"
LETTER_WIDTH = 12
LETTER_HEIGHT = 16

filenames = "A B C D E F G H I J K L M N O P Q R S T U V W X Y Z 1 2 3 4 5 6 7 8 9 0 $ = + fslash".split()

for f in range(len(filenames)):
    filenames[f] = PATH + filenames[f] + ".png"

alphabet = "a b c d e f g h i j k l m n o p q r s t u v w x y z 1 2 3 4 5 6 7 8 9 0 $ : + /".split()

images = {}

for i in range(len(alphabet)):
    images[alphabet[i]] = pygame.image.load(filenames[i])

def get_text_surface(text, bg_color=(0, 0, 0)):
    surface = pygame.Surface((LETTER_WIDTH * len(text), LETTER_HEIGHT))
    surface.fill(bg_color)
    for i in range(len(text)):
        if text[i] == " ":
            continue
        try:
            surface.blit(images[text[i]], (LETTER_WIDTH * i, 0))
        except KeyError:
            print(f"WARNING: unknown character '{text[i]}' encountered.")
    return surface
