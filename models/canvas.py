from PyQt5.QtCore import pyqtProperty, QObject

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


class Canvas(QObject):

    def __init__(self):
        super(Canvas, self).__init__()

        self.pixel_groups = []
        self.size = (800, 800)
        self.center = (400, 400)
        self.color_data = {}

        # The canvas is always in either design mode or sim mode.
        # In design mode, pixel colors are not drawn, and object manipulation
        # is allowed.  In sim mode, only pixel colors are drawn.
        self._design_mode = False

    @pyqtProperty(bool)
    def design_mode(self):
        return self._design_mode

    @design_mode.setter
    def design_mode(self, val):
        if self._design_mode != val:
            self._design_mode = val
