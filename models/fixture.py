from builtins import map
from builtins import object
import logging as log
import colorsys
import random
from util.clip import clip

from PyQt5 import QtCore


class Fixture(object):

    def __init__(self, data=None, controller=None, strand=0, address=0):
        self._strand = strand
        self._address = address
        self._type = "linear"
        self._num_pixels = 32
        self._pos1 = (-1, -1)
        self._pos2 = (-1, -1)
        self._locked = False
        self._data_offset = 0

        if data is not None:
            self.unpack(data)

        self._widget = None
        self._controller = controller

        #self._pixel_data = [(0, 0, 0)] * self._pixels

    def __repr__(self):
        return "[%d:%d]*%d  P1: %s  P2: %s" % (self._strand, self._address, self._num_pixels,
                                               self._pos1, self._pos2)

    def strand(self):
        return self._strand

    def set_strand(self, strand):
        self._strand = strand

    def address(self):
        return self._address

    def update_offset(self, offset):
        self._data_offset = offset

    def set_address(self, address):
        self._address = address
        # Offset will be updated from the SceneController

    def pixels(self):
        return self._num_pixels

    def set_pixels(self, pixels):
        self._num_pixels = pixels

    def pos1(self):
        return self._pos1

    def set_pos1(self, pos1):
        self._pos1 = pos1

    def pos2(self):
        return self._pos2

    def set_pos2(self, pos2):
        self._pos2 = pos2

    def destroy(self):
        log.info("Destroying fixture %s" % self)
        self._widget.deleteLater()

    def request_destruction(self):
        self._controller.delete_fixture(self)

    def pixel_data(self):
        data = self._controller.strand_data[self._strand][self._data_offset:self._data_offset+self._num_pixels]
        return data

    def unpack(self, data):
        self._strand = data.get("strand", 0)
        self._address = data.get("address", 0)
        self._type = data.get("type", "")
        self._num_pixels = data.get("pixels", 0)
        self._pos1 = data.get("pos1", [0, 0])
        self._pos2 = data.get("pos2", [0, 0])

    def pack(self):
        return {
                'strand': self._strand,
                'address': self._address,
                'type': self._type,
                'pixels': self._num_pixels,
                'pos1': self._pos1,
                'pos2': self._pos2
                }

    def fixture_move_callback(self, fixture):
        self._pos1 = list(map(int, (fixture.drag1.scene_x, fixture.drag1.scene_y)))
        self._pos2 = list(map(int, (fixture.drag2.scene_x, fixture.drag2.scene_y)))
        fixture.update_geometry()

    def random_color(self):
        r, g, b = [int(255.0 * c) for c in colorsys.hsv_to_rgb(random.random(), 1.0, 1.0)]
        self.set_all((r, g, b))
