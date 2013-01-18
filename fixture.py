"""
Basic fixture class
"""

# TODO: support multidimensional (X, Y) fixtures

class Fixture:

    def __init__(self, size=1, pos_rect=None):
        self.num_pixels = size
        self.size = size
        self.pixels = [(0, 0, 0)] * size
        self.pos_rect = pos_rect

    def blackout(self):
        self.pixels = [(0, 0, 0)] * self.size

    def set(self, pixel, color):
        assert isinstance(color, tuple), "Color must be a 3-tuple (R, G, B)"
        self.pixels[pixel] = color

    def set_all(self, color):
        assert isinstance(color, tuple), "Color must be a 3-tuple (R, G, B)"
        self.pixels = [color] * self.size
