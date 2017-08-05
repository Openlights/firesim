from __future__ import print_function
from builtins import chr
from builtins import range
import logging as log
import struct
import array
import os
import numpy as np
import time

from PyQt5.QtCore import pyqtSignal, pyqtSlot, QObject
from PyQt5.QtGui import QImage

from ui.canvaswidget import CanvasWidget
from ui.fixturewidget import FixtureWidget
from ui.crosshairwidget import CrosshairWidget

from models.fixture import Fixture

class SceneController(QObject):

    new_frame = pyqtSignal()

    def __init__(self, app, scene):
        super(SceneController, self).__init__()
        self.canvas = None
        self.scene = scene
        self.app = app
        self._output_buffer = None
        self.show_center = False
        self._color_mode = self.app.config.get("color-mode")

        self.strand_data = {}
        if self.canvas is not None:
            self.init_view()

        self.scene.set_controller(self)
        self.create_pixel_array()

    def init_view(self):
        self.load_backdrop()

    def load_backdrop(self):
        if self.canvas is not None:
            # if self.scene.get("backdrop-enable", False):
            #     image_filename = os.path.abspath(self.scene.get("backdrop-filename"))
            #     log.info("Loading backdrop from " + image_filename)
            #     img = QImage(image_filename)
            #     if img.isNull():
            #         log.error("Could not load background image: %s", image_filename)
            #     else:
            #         self.canvas.set_background_image(img)
            # else:
            #     self.canvas.set_background_image(None)
            self.canvas.update()

    def set_canvas(self, canvas):
        self.canvas = canvas
        canvas.scene_controller = self
        self.init_view()

    def get_canvas(self):
        return self.canvas

    def add_fixture(self):
        fh = self.scene.fixture_hierarchy()
        if fh:
            new_strand = max(fh.keys())
            new_address = max(fh[new_strand].keys()) + 1
        else:
            new_strand = 0
            new_address = 0
        fixture = Fixture(controller=self, strand=new_strand,
                          address=new_address)
        self.scene.add_fixture(fixture)
        self.update_canvas()
        self.create_pixel_array()

    def delete_fixture(self, fixture):
        self.scene.delete_fixture(fixture)
        self.update_canvas()
        self.create_pixel_array()

    def clear_fixtures(self):
        self.scene.clear_fixtures()
        self.create_pixel_array()

    def widget_selected(self, selected, fixture, multi):
        if multi:
            pass
        else:
            for f in self.scene.fixtures():
                if f is not fixture:
                    f.get_widget().select(False)
        self.app.widget_selected(selected, fixture, multi)

    def save_scene(self):
        self.scene.save()

    @pyqtSlot()
    def update_all(self):
        self.canvas.update()

    @pyqtSlot()
    def on_backdrop_enable_changed(self):
        self.backdrop_enable(self.app.state.backdrop_enable)

    def backdrop_enable(self, en):
        self.scene.set("backdrop-enable", en)
        self.load_backdrop()

    @pyqtSlot()
    def on_labels_visible_changed(self):
        self.labels_visible(self.app.state.labels_visible)

    def labels_visible(self, visible):
        self.scene.set("labels-visible", visible)
        self.update_all()

    @pyqtSlot()
    def on_locked_changed(self):
        self.locked(self.app.state.locked)

    def locked(self, is_locked):
        self.scene.set("locked", is_locked)
        if is_locked:
            self.canvas.deselect_all()
        self.update_all()

    @pyqtSlot()
    def on_center_visible_changed(self):
        self.center_visible(self.app.state.center_visible)

    def center_visible(self, visible):
        self.center_widget.hidden = not visible
        self.update_all()

    def update_fixture(self, fixture, new_strand, new_address):
        self.scene.update_fixture(fixture, new_strand, new_address)
        self.create_pixel_array()

    def create_pixel_array(self):
        """
        Initializes the array of colors used for displaying incoming data from the network.
        Needs to be called when the shape of the scene has changed
        (fixtures added/removed, addresses changed, pixels per fixture changed)
        """
        max_pixels = 0
        fh = self.scene.fixture_hierarchy()

        for strand in fh:
            strand_len = 0
            for address in fh[strand]:
                fixture = self.scene.fixture(strand, address)
                fixture.update_offset(strand_len)
                strand_len += fixture.pixels()

            self.strand_data[strand] = [(0, 0, 0)] * strand_len
            max_pixels = max(max_pixels, strand_len)

        log.info("Scene has %d strands, %d pixels." % (len(fh), max_pixels))
        self._output_buffer = np.zeros((len(fh), max_pixels, 3))
