import drawable

class Snapshot(drawable.Drawable):

    def __init__(self, game, dimensions, background_color):
        super().__init__(game, dimensions)
        self.background_color = background_color
        self.surface = drawable.create_blank_surface(dimensions, background_color)
        self.update()

    def draw(self, dest_surface, position):
        dest_surface.blit(self.surface, position)

    def update(self):
        self.surface.fill(self.background_color)
