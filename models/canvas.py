
from models.pixelgroup import LinearPixelGroup


test_pg_list = [
    {
        "type": "LinearPixelGroup",
        "start": [100, 100],
        "end": [300, 300],
        "count": 120,
        "address": [0, 0]
    }
]


class Canvas:

    def __init__(self):
        self.pixel_groups = []
        self.size = (800, 800)
        self.center = (400, 400)
        self.color_data = {}
