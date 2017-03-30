import logging as log
import struct
import array
import os
import numpy as np
import time

from ui.canvaswidget import CanvasWidget
from ui.fixturewidget import FixtureWidget
from ui.crosshairwidget import CrosshairWidget

from PySide import QtCore, QtGui


from models.fixture import Fixture

class SceneController(QtCore.QObject):

    new_frame = QtCore.Signal()

    def __init__(self, app, scene):
        super(SceneController, self).__init__()
        self.canvas = None
        self.scene = scene
        self.app = app
        self._output_buffer = None
        self.show_center = False
        self._color_mode = self.app.config.get("color_mode")
        self._frame_data = {}
        self.strand_data = {}
        self.times = []
        self.frame_start_time = 0.0
        if self.canvas is not None:
            self.init_view()

        self.scene.set_controller(self)
        self.create_pixel_array()

    def init_view(self):
        self.center_widget = CrosshairWidget(self.canvas, self.scene.center(), "Center", callback=self.on_center_moved)
        self.load_backdrop()
        self.update_canvas()

    def load_backdrop(self):
        if self.canvas is not None:
            if self.scene.get("backdrop_enable", False):
                image_filename = os.path.abspath(self.scene.get("backdrop_filename"))
                log.info("Loading backdrop from " + image_filename)
                img = QtGui.QImage(image_filename)
                if img.isNull():
                    log.error("Could not load background image: %s", image_filename)
                else:
                    self.canvas.set_background_image(img)
            else:
                self.canvas.set_background_image(None)
            self.canvas.update()

    def set_canvas(self, canvas):
        self.canvas = canvas
        canvas.controller = self
        self.init_view()

    def get_canvas(self):
        return self.canvas

    def update_canvas(self):
        if self.canvas is not None:
            fl = [f.get_widget() for f in self.scene.fixtures()]
            self.canvas.update_fixtures(fl)

    def on_center_moved(self, pos):
        print pos
        ipos = (int(pos.x()), int(pos.y()))
        self.scene.set_center(ipos)

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

    def update_all(self):
        for f in self.scene.fixtures():
            f.get_widget().update()
        self.center_widget.update()
        self.canvas.update()

    def toggle_background_enable(self):
        if self.scene.get("backdrop_enable", False):
            self.scene.set("backdrop_enable", False)
            self.load_backdrop()
            return False
        else:
            self.scene.set("backdrop_enable", True)
            self.load_backdrop()
            return True

    def toggle_labels_enable(self):
        enabled = not self.scene.get("labels_enable", False)
        self.scene.set("labels_enable", enabled)
        self.update_all()
        return enabled

    def toggle_locked(self):
        locked = not self.scene.get("locked", False)
        self.scene.set("locked", locked)
        if locked:
            self.canvas.deselect_all()
        self.update_all()
        return locked

    def toggle_show_center(self):
        self.show_center = not self.show_center
        self.center_widget.hidden = not self.show_center
        self.update_all()
        return self.show_center

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

    @QtCore.Slot(list)
    def process_command(self, packet):
        cmd = chr(packet[0])
        datalen = 0

        # begin frame
        if cmd == 'B':
            self.frame_start_time = time.time()
            self.app.netcontroller.frame_started()

        # Unpack strand pixel data
        elif cmd == 'S':
            strand = packet[1]
            datalen = (packet[3] << 8) + packet[2]
            data = [c for c in packet[4:]]
            self._frame_data[strand] = data

        # end frame
        elif cmd == 'E':
            for strand, data in self._frame_data.iteritems():
                data = [data[i:i+3] for i in xrange(0, len(data), 3)]
                self.strand_data[strand] = data
            self.times.append((time.time() - self.frame_start_time))
            if len(self.times) > 100:
                self.times.pop(0)
            self.new_frame.emit()

        else:
            log.error("Malformed packet of length %d!" % len(packet))
