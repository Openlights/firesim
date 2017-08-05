
from models.pixelgroup import LinearPixelGroup


class Canvas:

    def __init__(self):
        self.pixel_groups = [LinearPixelGroup((100, 100), (300, 300), 120, (0, 0))]
        self.size = (800, 800)
        self.color_data = {}
