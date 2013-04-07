import logging as log
import colorsys
import random

from PySide import QtCore

from ui.fixturewidget import FixtureWidget


class Fixture:

    def __init__(self, data=None, controller=None):
        self._strand = 0
        self._address = 0
        self._type = "linear"
        self._pixels = 32
        self._pos1 = (10, 10)
        self._pos2 = (50, 50)
        self._locked = False

        if data is not None:
            self.unpack(data)

        self._widget = None
        self._controller = controller

        self._pixel_data = [(0, 0, 0)] * self._pixels

    def __repr__(self):
        return "[%d:%d]*%d" % (self._strand, self._address, self._pixels)

    def strand(self):
        return self._strand

    def set_strand(self, strand):
        self._strand = strand

    def address(self):
        return self._address

    def set_address(self, address):
        self._address = address

    def pixels(self):
        return self._pixels

    def set_pixels(self, pixels):
        self._pixels = pixels

    def pos1(self):
        return self._pos1

    def set_pos1(self, pos1):
        self._pos1 = pos1

    def pos2(self):
        return self._pos2

    def set_pos2(self, pos2):
        self._pos2 = pos2

    def destroy(self):
        self._widget.deleteLater()

    def request_destruction(self):
        self._controller.delete_fixture(self)

    def get_widget(self):
        if self._widget is None:
            self._widget = FixtureWidget(self._controller.get_canvas(), model=self)
            x, y = self._pos1[0], self._pos1[1]
            self._widget.setPos(x, y)
            #self._widget.setRotation(self.angle)
        return self._widget

    def unpack(self, data):
        self._strand = data.get("strand", 0)
        self._address = data.get("address", 0)
        self._type = data.get("type", "")
        self._pixels = data.get("pixels", 0)
        self._pos1 = data.get("pos1", [0, 0])
        self._pos2 = data.get("pos2", [0, 0])

    def pack(self):
        return {
                'strand': self._strand,
                'address': self._address,
                'type': self._type,
                'pixels': self._pixels,
                'pos1': self._pos1,
                'pos2': self._pos2
                }

    def fixture_move_callback(self, fixture):
        self._pos1 = map(int, fixture.drag1.pos().toTuple())
        self._pos2 = map(int, fixture.drag2.pos().toTuple())
        fixture.update_geometry()

    def blackout(self):
        self._pixel_data = [(0, 0, 0)] * self._pixels
        self._widget.update()

    def set(self, pixel, color):
        assert isinstance(color, tuple), "Color must be a 3-tuple (R, G, B)"
        self._pixel_data[pixel] = color
        self._widget.update()

    def set_all(self, color):
        assert isinstance(color, tuple), "Color must be a 3-tuple (R, G, B)"
        self._pixel_data = [color] * self._pixels
        self._widget.update()

    def random_color(self):
        r, g, b = [int(255.0 * c) for c in colorsys.hsv_to_rgb(random.random(), 1.0, 1.0)]
        self.set_all((r, g, b))