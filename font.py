import pygame

PATH = "assets/typeface/"

filenames = "A B C D E F G H I J K L M N O P Q R S T U V W X Y Z 1 2 3 4 5 6 7 8 9 0 $".split()

for f in range(len(filenames)):
    filenames[f] = PATH + filenames[f] + ".png"

alphabet = "a b c d e f g h i j k l m n o p q r s t u v w x y z 1 2 3 4 5 6 7 8 9 0 $".split()

images = {}

for i in range(len(alphabet)):
    images[alphabet[i]] = pygame.image.load(filenames[i])

def get_text_surface(text):
    surface = pygame.Surface((12 * len(text), 16))
    for i in range(len(text)):
        surface.blit(images[text[i]], (12 * i, 0))
    return surface