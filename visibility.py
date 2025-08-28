import math

class Visibility:
    # TODO: come up with a clever way not to make so many location checks all the time

    def __init__(self):
        self.scanners = []

    def get_visible(self, location):
        for scanner in self.scanners:
            if math.hypot(location[0] - scanner[0], location[1] - scanner[1]) < scanner[2]:
                return True
        return False

    def reset(self):
        self.scanners = []
