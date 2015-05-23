import logging as log
import struct
import array
import numpy as np

from ui.canvaswidget import CanvasWidget
from ui.fixturewidget import FixtureWidget
from ui.crosshairwidget import CrosshairWidget

from PySide import QtGui


from models.fixture import Fixture

class SceneController:

    def __init__(self, app=None, canvas=None, scene=None):
        self.canvas = canvas
        self.scene = scene
        self.app = app
        self.fixtures = []
        self._num_packets = 0
        self._max_fixtures = 0
        self._max_pixels = 0
        self._output_buffer = None
        self.show_center = False
        self._strand_keys = list()
        self._color_mode = self.app.config.get("color_mode")
        self._frame_data = {}
        self.strand_data = {}
        if self.canvas is not None:
            self.init_view()

        self.create_pixel_array()

    def init_view(self):
        self.center_widget = CrosshairWidget(self.canvas, self.scene.center(), "Center", callback=self.on_center_moved)
        self.load_backdrop()
        self.fixtures = []
        fixture_data = self.scene.get("fixtures", [])
        for fixture_data_item in fixture_data:
            self.fixtures.append(Fixture(fixture_data_item, controller=self))
        self.update_canvas()

    def load_backdrop(self):
        if self.canvas is not None:
            if self.scene.get("backdrop_enable", False):
                log.info("Loading backdrop from " + self.scene.get("backdrop_filename"))
                self.canvas.set_background_image(QtGui.QImage(self.scene.get("backdrop_filename")))
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
            fl = [f.get_widget() for f in self.fixtures]
            self.canvas.update_fixtures(fl)

    def on_center_moved(self, pos):
        print pos
        ipos = (int(pos.x()), int(pos.y()))
        self.scene.set_center(ipos)

    def add_fixture(self):
        self.fixtures.append(Fixture(controller=self))
        self.update_canvas()
        self.update_scene()
        self.create_pixel_array()

    def delete_fixture(self, fixture):
        self.fixtures = [f for f in self.fixtures if f is not fixture]
        log.info("Destroying fixture %s" % fixture)
        fixture.destroy()
        self.update_scene()
        self.update_canvas()
        self.create_pixel_array()

    def clear_fixtures(self):
        while len(self.fixtures) > 0:
            fixture = self.fixtures.pop()
            fixture.destroy()
            del fixture
        self.update_scene()
        self.create_pixel_array()

    def widget_selected(self, selected, fixture, multi):
        if multi:
            pass
        else:
            for f in self.fixtures:
                if f is not fixture:
                    f.get_widget().select(False)
        self.app.widget_selected(selected, fixture, multi)

    def update_scene(self):
        fd = []
        for fixture in self.fixtures:
            fd.append(fixture.pack())
        self.scene.set_fixture_data(fd)

    def save_scene(self):
        self.update_scene()
        self.scene.save()

    def get_fixture(self, id):
        for f in self.fixtures:
            if f.id == id:
                return f

    def get_fixtures(self):
        return self.fixtures

    def update_all(self):
        for f in self.fixtures:
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
        self.update_all()
        return locked

    def toggle_show_center(self):
        self.show_center = not self.show_center
        self.center_widget.hidden = not self.show_center
        self.update_all()
        return self.show_center

    def create_pixel_array(self):
        """
        Initializes the array of colors used for displaying incoming data from the network.
        Needs to be called when the shape of the scene has changed
        (fixtures added/removed, addresses changed, pixels per fixture changed)
        """
        fh = self.scene.fixture_hierarchy()
        self._strand_keys = list()
        for strand in fh:

            self._strand_keys.append(strand)
            if len(fh[strand]) > self._max_fixtures:
                self._max_fixtures = len(fh[strand])
            strand_len = 0
            for fixture in fh[strand]:
                strand_len += fh[strand][fixture].pixels()
                if fh[strand][fixture].pixels() > self._max_pixels:
                    self._max_pixels = fh[strand][fixture].pixels()
            self.strand_data[strand] = [(0, 0, 0)] * strand_len
        log.info("Scene has %d strands, creating array using %d fixtures by %d pixels." % (len(self._strand_keys), self._max_fixtures, self._max_pixels))
        self._output_buffer = np.zeros((len(self._strand_keys), self._max_fixtures, self._max_pixels, 3))

    def set_strand(self, strand, pixels):
        start = 0
        strand_fixtures = [f for f in self.fixtures if (f.strand() == strand or strand == -1)]
        for f in sorted(strand_fixtures, key=lambda f: f.address()):
            if (strand == -1 or f.strand() == strand):
                nd = 3 * f.pixels()
                if len(pixels) >= (start + nd):
                    fixture_pixels = pixels[start:start + nd]
                    f.set_flat_array(fixture_pixels)
                start += nd

    def process_command(self, packet):
        if len(packet) < 3:
            log.error("Malformed packet!")
            print packet
            return

        self._num_packets += 1

        while True:
            cmd = packet[0]
            datalen = 0

            # start frame
            if cmd == 0x01:
                self.app.netcontroller.frame_started()

            # Unpack strand pixel data
            elif cmd == 0x20:
                strand = packet[1]
                datalen = (packet[3] << 8) + packet[2]
                data = packet[4:]
                self._frame_data[strand] = data

            # end frame
            elif cmd == 0x02:
                self.app.netcontroller.frame_complete()
                for strand, data in self._frame_data.iteritems():
                    data = [data[i:i+3] for i in xrange(0, len(data), 3)]
                    self.strand_data[strand] = data

            if len(packet) > (4 + datalen):
                packet = packet[4 + datalen:]
                #print len(packet)
            else:
                break
